from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import get_async_db
from app.models.vitals import Vitals
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.user import User
from app.models.patient import Patient
from app.dependencies import get_current_user, get_patient_or_doctor_access

router = APIRouter()


def _vital_to_dict(v: Vitals) -> Dict[str, Any]:
	return {
		"id": v.id,
		"patientId": v.patient_id,
		"recordedAt": v.recorded_at.isoformat() if v.recorded_at else None,
		"systolic": v.systolic,
		"diastolic": v.diastolic,
		"heartRate": v.heart_rate,
		"temperature": float(v.temperature) if v.temperature is not None else None,
		"bloodGlucose": float(v.blood_glucose) if v.blood_glucose is not None else None,
		"oxygenSaturation": v.oxygen_saturation,
		"weight": float(v.weight) if v.weight is not None else None,
		"notes": v.notes,
	}


@router.get("/{patient_id}/vitals")
async def list_vitals(
	patient_id: int,
	limit: int = Query(50, ge=1, le=200),
	offset: int = Query(0, ge=0),
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_async_db),
):
	"""Get vitals history for a patient. Patients can only access their own; doctors can access any."""

	# Access control (returns patient or raises)
	await get_patient_or_doctor_access(patient_id, current_user, db)

	stmt = (
		select(Vitals)
		.where(Vitals.patient_id == patient_id)
		.order_by(desc(Vitals.recorded_at))
		.offset(offset)
		.limit(limit)
	)
	result = await db.execute(stmt)
	rows = result.scalars().all()
	return [_vital_to_dict(v) for v in rows]


@router.post("/{patient_id}/vitals")
async def add_vitals(
	patient_id: int,
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_async_db),
):
	"""Add a new vitals record for a patient. Patients can add their own; doctors can add for any."""

	# Access control (returns patient or raises)
	await get_patient_or_doctor_access(patient_id, current_user, db)

	# Create vitals record; use now if recordedAt not provided
	recorded_at = None
	if payload.get("recordedAt"):
		try:
			recorded_at = datetime.fromisoformat(payload["recordedAt"])  # expects ISO string
		except Exception:
			recorded_at = datetime.utcnow()
	else:
		recorded_at = datetime.utcnow()

	# Normalize units where UI differs from DB defaults
	# Temperature: UI uses °F, DB historically used °C in seeds. Convert if clearly Fahrenheit.
	temp = payload.get("temperature")
	if temp is not None and isinstance(temp, (int, float)) and temp > 45:
		temp = (float(temp) - 32.0) * (5.0 / 9.0)

	# Weight: UI label shows lbs, DB seeds look like kg. Convert large values as lbs -> kg.
	weight = payload.get("weight")
	if weight is not None and isinstance(weight, (int, float)) and weight > 200:
		weight = float(weight) / 2.20462

	v = Vitals(
		patient_id=patient_id,
		recorded_at=recorded_at,
		systolic=payload.get("systolic"),
		diastolic=payload.get("diastolic"),
		heart_rate=payload.get("heartRate"),
		temperature=temp,
		blood_glucose=payload.get("bloodGlucose"),
		oxygen_saturation=payload.get("oxygenSaturation"),
		weight=weight,
		notes=payload.get("notes"),
	)

	db.add(v)
	await db.flush()

	# Generate threshold-based alerts for abnormal vitals
	alerts_to_create: List[Alert] = []
	s, d = v.systolic or 0, v.diastolic or 0
	hr = v.heart_rate or 0
	bg = float(v.blood_glucose) if v.blood_glucose is not None else 0.0
	spo2 = v.oxygen_saturation or 0
	t = float(v.temperature) if v.temperature is not None else 0.0

	# Blood pressure thresholds
	if s >= 180 or d >= 120:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.CRITICAL,
			type=AlertType.RISK_THRESHOLD,
			title="Hypertensive Crisis",
			message=f"BP {s}/{d} mmHg exceeds crisis threshold",
			recommendation="Seek immediate medical attention",
			alert_metadata={"systolic": s, "diastolic": d}
		))
	elif s >= 160 or d >= 100:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.URGENT,
			type=AlertType.RISK_THRESHOLD,
			title="Severely Elevated Blood Pressure",
			message=f"BP {s}/{d} mmHg is severely elevated",
			recommendation="Review antihypertensive therapy",
			alert_metadata={"systolic": s, "diastolic": d}
		))
	elif s >= 140 or d >= 90:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.SERIOUS,
			type=AlertType.RISK_THRESHOLD,
			title="Elevated Blood Pressure",
			message=f"BP {s}/{d} mmHg is above normal",
			recommendation="Monitor and consider medication adjustment",
			alert_metadata={"systolic": s, "diastolic": d}
		))

	# Heart rate thresholds
	if hr >= 130:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.URGENT,
			type=AlertType.ANOMALY,
			title="Tachycardia Detected",
			message=f"Heart rate {hr} bpm",
			recommendation="Assess for arrhythmia or dehydration",
			alert_metadata={"heart_rate": hr}
		))

	# Blood glucose thresholds (random > 200 mg/dL)
	if bg >= 250:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.URGENT,
			type=AlertType.RISK_THRESHOLD,
			title="Severe Hyperglycemia",
			message=f"Blood glucose {bg} mg/dL",
			recommendation="Review insulin/medication; check for DKA symptoms",
			alert_metadata={"blood_glucose": bg}
		))
	elif bg >= 180:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.SERIOUS,
			type=AlertType.RISK_THRESHOLD,
			title="Hyperglycemia",
			message=f"Blood glucose {bg} mg/dL",
			recommendation="Dietary review and medication adherence",
			alert_metadata={"blood_glucose": bg}
		))

	# Oxygen saturation low
	if spo2 and spo2 <= 92:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.URGENT if spo2 <= 88 else AlertSeverity.SERIOUS,
			type=AlertType.ANOMALY,
			title="Low Oxygen Saturation",
			message=f"SpO2 {spo2}%",
			recommendation="Evaluate respiratory status",
			alert_metadata={"oxygen_saturation": spo2}
		))

	# Fever threshold (°C)
	if t and t >= 38.0:
		alerts_to_create.append(Alert(
			patient_id=patient_id,
			severity=AlertSeverity.MILD,
			type=AlertType.ANOMALY,
			title="Fever Detected",
			message=f"Temperature {round(t,1)} °C",
			recommendation="Hydration and symptomatic care; monitor",
			alert_metadata={"temperature_c": t}
		))

	if alerts_to_create:
		db.add_all(alerts_to_create)

	await db.commit()
	await db.refresh(v)
	return _vital_to_dict(v)


@router.get("/{patient_id}/vitals/latest")
async def get_latest_vitals(
	patient_id: int,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_async_db),
):
	"""Get the most recent vitals reading for a patient."""
	await get_patient_or_doctor_access(patient_id, current_user, db)
	stmt = (
		select(Vitals)
		.where(Vitals.patient_id == patient_id)
		.order_by(desc(Vitals.recorded_at))
		.limit(1)
	)
	result = await db.execute(stmt)
	v = result.scalar_one_or_none()
	if not v:
		return None
	return _vital_to_dict(v)
