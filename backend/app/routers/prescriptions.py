from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from app.database import get_async_db
from app.models.prescription import Prescription
from app.dependencies import get_patient_or_doctor_access, get_current_user
from app.models.user import User
from app.models.alert import Alert, AlertSeverity, AlertType
from app.services.prescription_analyzer import analyze_prescription

router = APIRouter()

def _parse_free_text_prescription(text: str) -> List[Dict[str, str]]:
	"""Very simple heuristic parser: split by line breaks and extract medication lines.
	Expected formats like:
	  - "Tab. Amoxicillin" followed by strength/dose/frequency lines
	This returns a list of { name, dose, frequency, instructions } objects.
	"""
	meds: List[Dict[str, str]] = []
	lines = [l.strip() for l in text.splitlines() if l.strip()]
	current: Dict[str, str] | None = None
	for ln in lines:
		lower = ln.lower()
		if lower.startswith(("1.", "2.", "3.", "4.", "5.")) or lower.startswith(("tab", "cap", "syr", "inj")) or "tablet" in lower:
			# start new med
			if current:
				meds.append(current)
			name = ln
			# remove leading numbering and common prefixes
			name = name.lstrip("0123456789. ")
			name = name.replace("Tab.", "").replace("Cap.", "").replace("Syr.", "").strip()
			current = {"name": name, "dose": "", "frequency": "", "instructions": ""}
		elif current and ("mg" in lower or "ml" in lower or "strength" in lower):
			current["dose"] = ln
		elif current and ("once" in lower or "twice" in lower or "three" in lower or "every" in lower or "times a day" in lower or "sos" in lower):
			current["frequency"] = ln
		elif current and ("gargle" in lower or "with" in lower or "after meals" in lower or "as needed" in lower):
			# capture general instruction lines
			if current.get("instructions"):
				current["instructions"] += " " + ln
			else:
				current["instructions"] = ln
		else:
			# ignore quantities/refills/advice for now
			pass
	if current:
		meds.append(current)
	# cleanup
	for m in meds:
		m["name"] = m["name"].strip()
		m["dose"] = m["dose"].strip()
		m["frequency"] = m["frequency"].strip()
		if not m["instructions"]:
			m.pop("instructions", None)
	return meds


@router.get("/{patient_id}/prescriptions")
async def list_prescriptions(
	patient_id: int,
	_: Any = Depends(get_patient_or_doctor_access),
	db: AsyncSession = Depends(get_async_db)
):
	# Order by latest first so UI can show the most recent analysis at index 0
	result = await db.execute(
		select(Prescription)
		.where(Prescription.patient_id == patient_id)
		.order_by(Prescription.uploaded_at.desc())
	)
	items = result.scalars().all()

	# Include on-the-fly analysis so both patient & doctor UIs can show summary/findings
	response: list[dict[str, Any]] = []
	for p in items:
		meds = p.parsed_medications or []
		analysis = await analyze_prescription(db, meds)
		response.append({
			"id": p.id,
			"patientId": p.patient_id,
			"uploadedBy": p.uploaded_by,
			"uploadedAt": p.uploaded_at.isoformat() if p.uploaded_at else None,
			"ocrText": p.ocr_text,
			"parsedMedications": meds,
			"flags": p.flags or [],
			"analysis": {
				"summary": analysis.get("summary"),
				"interactions": analysis.get("interactions", []),
				"findings": analysis.get("findings", []),
			},
			"originalFilename": p.original_filename,
		})
	return response


@router.post("/{patient_id}/prescriptions")
async def create_prescription(
	patient_id: int,
	payload: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	_: Any = Depends(get_patient_or_doctor_access),
	db: AsyncSession = Depends(get_async_db)
):
	"""Create a prescription from free-text (ocrText) for now."""
	ocr_text = (payload or {}).get("ocrText", "").strip()
	if not ocr_text:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ocrText is required")

	meds = _parse_free_text_prescription(ocr_text)
	# Run analyzer: drug interactions + dosage rules + summary, and convert findings to flags
	analysis = await analyze_prescription(db, meds)
	flags = analysis.get("flags", [])

	pres = Prescription(
		patient_id=patient_id,
		uploaded_by=current_user.id,
		ocr_text=ocr_text,
		parsed_medications=meds,
		flags=flags,
		processing_status="completed",
	)
	db.add(pres)
	await db.commit()
	await db.refresh(pres)

	return {
		"id": pres.id,
		"patientId": pres.patient_id,
		"uploadedBy": pres.uploaded_by,
		"uploadedAt": pres.uploaded_at.isoformat() if pres.uploaded_at else None,
		"ocrText": pres.ocr_text,
		"parsedMedications": pres.parsed_medications or [],
		"flags": pres.flags or [],
		"analysis": {
			"summary": analysis.get("summary"),
			"interactions": analysis.get("interactions", []),
			"findings": analysis.get("findings", []),
		},
		"originalFilename": pres.original_filename,
	}


@router.patch("/{patient_id}/prescriptions/{prescription_id}")
async def update_prescription(
	patient_id: int,
	prescription_id: int,
	updates: Dict[str, Any],
	current_user: User = Depends(get_current_user),
	_: Any = Depends(get_patient_or_doctor_access),
	db: AsyncSession = Depends(get_async_db)
):
	"""Adjust a prescription (e.g., change dose/frequency) and append a flag entry."""
	result = await db.execute(select(Prescription).where(Prescription.id == prescription_id, Prescription.patient_id == patient_id))
	pres = result.scalar_one_or_none()
	if not pres:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

	# Apply simple updates to parsed medications (first med as example)
	meds = pres.parsed_medications or []
	if meds and isinstance(meds, list):
		m0 = dict(meds[0])
		if "dose" in updates:
			m0["dose"] = updates["dose"]
		if "frequency" in updates:
			m0["frequency"] = updates["frequency"]
		meds[0] = m0
		pres.parsed_medications = meds

	# Append a review/adjustment flag
	flags = pres.flags or []
	flags.append({"severity": "low", "message": f"Adjusted by user {current_user.id}"})
	pres.flags = flags

	db.add(pres)

	# Create an informational alert for the doctor timeline
	db.add(Alert(
		patient_id=patient_id,
		severity=AlertSeverity.MILD,
		type=AlertType.DRUG_INTERACTION,
		title="Prescription Adjusted",
		message=f"Prescription {prescription_id} was adjusted",
		alert_metadata={"prescription_id": prescription_id, "updates": updates}
	))

	await db.commit()
	await db.refresh(pres)

	return {
		"id": pres.id,
		"patientId": pres.patient_id,
		"uploadedBy": pres.uploaded_by,
		"uploadedAt": pres.uploaded_at.isoformat() if pres.uploaded_at else None,
		"ocrText": pres.ocr_text,
		"parsedMedications": pres.parsed_medications or [],
		"flags": pres.flags or [],
		"originalFilename": pres.original_filename,
	}
