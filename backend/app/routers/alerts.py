from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.database import get_async_db
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.user import User
from app.dependencies import get_current_user, RequireDoctor, require_roles

router = APIRouter()

def _alert_to_dict(a: Alert) -> Dict[str, Any]:
	# Coerce enum-like fields to lowercase strings for frontend compatibility
	sev = a.severity.value if hasattr(a.severity, "value") else a.severity
	typ = a.type.value if hasattr(a.type, "value") else a.type
	sev_str = sev.lower() if isinstance(sev, str) else str(sev).lower()
	typ_str = typ.lower() if isinstance(typ, str) else str(typ).lower()
	return {
		"id": a.id,
		"patientId": a.patient_id,
		"generatedAt": a.generated_at.isoformat() if a.generated_at else None,
		"severity": sev_str,
		"type": typ_str,
		"title": a.title,
		"message": a.message,
		"acknowledged": a.acknowledged,
		"acknowledgedAt": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
		"resolved": a.resolved,
		"resolvedAt": a.resolved_at.isoformat() if a.resolved_at else None,
		"metadata": a.alert_metadata,
		"recommendation": a.recommendation,
		"priority": a.priority_score,
	}


@router.get("/")
@router.get("")
async def list_alerts(
	patient_id: Optional[int] = Query(default=None),
	severity: Optional[str] = Query(default=None, pattern="^(mild|serious|urgent|critical)$"),
	acknowledged: Optional[bool] = Query(default=None),
	limit: int = Query(50, ge=1, le=200),
	offset: int = Query(0, ge=0),
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_async_db),
):
	"""List alerts. Doctors can see all; patients see their own."""
	stmt = select(Alert).order_by(desc(Alert.generated_at)).offset(offset).limit(limit)

	# Filter by role
	if current_user.role == "patient":
		from app.models.patient import Patient
		# Find their patient id
		# Note: small join-less path since relationship exists; safe with simple select
		# but we can filter directly by patient_id via subquery if needed
		# For simplicity, let frontend pass patient_id too; otherwise, we skip
		if patient_id is None:
			# without patient_id, restrict by the patient linked to current user
			from sqlalchemy import select as sa_select
			from app.models.patient import Patient
			sub = sa_select(Patient.id).where(Patient.user_id == current_user.id).scalar_subquery()
			stmt = stmt.where(Alert.patient_id == sub)
		else:
			stmt = stmt.where(Alert.patient_id == patient_id)
	else:
		if patient_id is not None:
			stmt = stmt.where(Alert.patient_id == patient_id)

	if severity:
		try:
			sev = AlertSeverity(severity)
			stmt = stmt.where(Alert.severity == sev)
		except Exception:
			raise HTTPException(status_code=400, detail="Invalid severity filter")

	if acknowledged is not None:
		stmt = stmt.where(Alert.acknowledged == acknowledged)

	result = await db.execute(stmt)
	alerts = result.scalars().all()
	return [_alert_to_dict(a) for a in alerts]


@router.patch("/{alert_id}")
async def update_alert(
	alert_id: int,
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_async_db),
):
	"""Update an alert (acknowledge/resolve)."""
	result = await db.execute(select(Alert).where(Alert.id == alert_id))
	alert = result.scalar_one_or_none()
	if not alert:
		raise HTTPException(status_code=404, detail="Alert not found")

	# Patients can only update their own alerts; doctors/admin can update any
	if current_user.role == "patient":
		# fetch their patient id
		from sqlalchemy import select as sa_select
		from app.models.patient import Patient
		sub = await db.execute(sa_select(Patient.id).where(Patient.user_id == current_user.id))
		pid = sub.scalar_one_or_none()
		if alert.patient_id != pid:
			raise HTTPException(status_code=403, detail="Not allowed")

	now = datetime.utcnow()
	if "acknowledged" in payload:
		alert.acknowledged = bool(payload["acknowledged"])
		alert.acknowledged_at = now if alert.acknowledged else None
		alert.acknowledged_by = current_user.id if alert.acknowledged else None

	if "resolved" in payload:
		alert.resolved = bool(payload["resolved"])
		alert.resolved_at = now if alert.resolved else None

	await db.commit()
	await db.refresh(alert)
	return _alert_to_dict(alert)
