from __future__ import annotations

from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.models.drug_interaction import DrugInteraction


def _norm(name: str) -> str:
    return (name or "").strip().lower()


async def check_interactions(db: AsyncSession, meds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    names = [m.get("name", "").strip() for m in meds if m.get("name")]
    unique = list({n.lower(): n for n in names}.values())
    interactions: List[Dict[str, Any]] = []
    # Check all pairs against DrugInteraction table (case-insensitive)
    for i in range(len(unique)):
        for j in range(i + 1, len(unique)):
            a, b = unique[i], unique[j]
            stmt = select(DrugInteraction).where(
                or_(
                    (func.lower(DrugInteraction.drug_a) == func.lower(a)) & (func.lower(DrugInteraction.drug_b) == func.lower(b)),
                    (func.lower(DrugInteraction.drug_a) == func.lower(b)) & (func.lower(DrugInteraction.drug_b) == func.lower(a))
                )
            )
            result = await db.execute(stmt)
            match = result.scalar_one_or_none()
            if match:
                interactions.append({
                    "drugA": a,
                    "drugB": b,
                    "severity": match.severity,
                    "description": match.description,
                    "mechanism": match.mechanism,
                    "management": match.clinical_management,
                })
    return interactions


def check_dosage_rules(meds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for m in meds:
        name = _norm(m.get("name", ""))
        dose = (m.get("dose") or "").lower()
        freq = (m.get("frequency") or "").lower()

        # Simple paracetamol checks
        if "paracetamol" in name or "acetaminophen" in name:
            if "1000" in dose:
                findings.append({
                    "severity": "medium",
                    "type": "dose",
                    "message": "High single dose of paracetamol (1000 mg). Review total daily dose.",
                })
            if "650" in dose and ("three" in freq or "four" in freq):
                findings.append({
                    "severity": "medium",
                    "type": "frequency",
                    "message": "Paracetamol 650 mg taken ≥3 times daily may exceed safe limits.",
                })

        # Basic amoxicillin frequency sanity
        if "amoxicillin" in name and not any(w in freq for w in ["twice", "three", "every 8"]):
            findings.append({
                "severity": "low",
                "type": "frequency",
                "message": "Amoxicillin frequency looks uncommon; verify dosing interval.",
            })

    # Duplicate medications
    seen = {}
    for m in meds:
        n = _norm(m.get("name", ""))
        if not n:
            continue
        seen[n] = seen.get(n, 0) + 1
    for n, cnt in seen.items():
        if cnt > 1:
            findings.append({
                "severity": "low",
                "type": "duplicate",
                "message": f"Duplicate medication entries detected for '{n}'.",
            })

    return findings


async def analyze_prescription(db: AsyncSession, meds: List[Dict[str, Any]]) -> Dict[str, Any]:
    interactions = await check_interactions(db, meds)
    findings = check_dosage_rules(meds)

    # Build a short AI-style summary (deterministic, no external API)
    issues = []
    if interactions:
        issues.append(f"{len(interactions)} potential drug interaction(s) detected")
    if any(f["severity"] == "medium" for f in findings):
        issues.append("dosage/frequency review recommended")
    if any(f["type"] == "duplicate" for f in findings):
        issues.append("duplicate entries found")

    summary = "All medications look within expected ranges." if not issues else (
        "; ".join(issues).capitalize() + "."
    )

    # Convert interactions into flag-like messages to surface in current UI
    interaction_flags = [
        {
            "severity": ("high" if it.get("severity") in ("major", "contraindicated") else ("medium" if it.get("severity") == "moderate" else "low")),
            "message": f"Interaction: {it['drugA']} + {it['drugB']} — {it['description']}",
        }
        for it in interactions
    ]

    return {
        "summary": summary,
        "interactions": interactions,
        "findings": findings,
        "flags": interaction_flags + [
            {"severity": f.get("severity", "low"), "message": f.get("message", "")}
            for f in findings
        ],
    }
