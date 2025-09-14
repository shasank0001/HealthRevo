"""
Utilities to load drug interaction data into the HealthRevo database.

Supports loading from CSV (recommended) and from an external SQLite file.

Expected CSV columns (case-insensitive, extra columns ignored):
  - drug_a, drug_b (required)
  - severity (minor|moderate|major|contraindicated)
  - description (required)
  - mechanism (optional)
  - clinical_management (optional)
  - drugbank_id_a, drugbank_id_b (optional)
  - drug_a_aliases, drug_b_aliases (optional; JSON string or ";"-separated)

Place your CSV at: backend/data/drug_interactions.csv
Run the seed script: python backend/scripts/seed_drug_interactions.py --csv backend/data/drug_interactions.csv --replace
"""
from __future__ import annotations

from typing import Iterable, Dict, Any, Optional
import csv
import json
import os
import sqlite3

from app.database import SessionLocal, Base, sync_engine
from app.models.drug_interaction import DrugInteraction


def _norm_severity(s: Optional[str]) -> str:
    if not s:
        return "moderate"
    s = s.strip().lower()
    if s in {"minor", "low"}:
        return "minor"
    if s in {"moderate", "medium"}:
        return "moderate"
    if s in {"major", "high"}:
        return "major"
    if s in {"contraindicated", "contra-indicated", "contra"}:
        return "contraindicated"
    return "moderate"


def _to_json_or_text(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None
    # If it looks like JSON already, keep it
    if (v.startswith("[") and v.endswith("]")) or (v.startswith("{") and v.endswith("}")):
        return v
    # Otherwise, treat as semicolon/comma separated list and convert to JSON array
    parts = [p.strip() for p in v.replace("\n", " ").split(";") if p.strip()]
    if not parts:
        parts = [p.strip() for p in v.split(",") if p.strip()]
    if parts:
        return json.dumps(parts, ensure_ascii=False)
    return v


def _prepare_row(row: Dict[str, Any]) -> Dict[str, Any]:
    # Normalize keys to lowercase for robustness
    r = {k.lower(): v for k, v in row.items()}

    drug_a = (r.get("drug_a") or r.get("a") or "").strip()
    drug_b = (r.get("drug_b") or r.get("b") or "").strip()
    description = (r.get("description") or r.get("desc") or "").strip()

    if not drug_a or not drug_b or not description:
        raise ValueError("drug_a, drug_b, and description are required")

    payload = {
        "drug_a": drug_a,
        "drug_b": drug_b,
        "severity": _norm_severity(r.get("severity")),
        "description": description,
        "mechanism": (r.get("mechanism") or "").strip() or None,
        "clinical_management": (r.get("clinical_management") or r.get("management") or "").strip() or None,
        "drugbank_id_a": (r.get("drugbank_id_a") or r.get("drugbank_a") or "").strip() or None,
        "drugbank_id_b": (r.get("drugbank_id_b") or r.get("drugbank_b") or "").strip() or None,
        "drug_a_aliases": _to_json_or_text(r.get("drug_a_aliases")),
        "drug_b_aliases": _to_json_or_text(r.get("drug_b_aliases")),
    }
    return payload


def _bulk_insert(session, rows: Iterable[Dict[str, Any]], replace: bool = False, batch_size: int = 1000) -> int:
    if replace:
        session.query(DrugInteraction).delete()
        session.commit()

    count = 0
    batch: list[DrugInteraction] = []
    for r in rows:
        try:
            payload = _prepare_row(r)
        except ValueError:
            # Skip invalid rows
            continue
        batch.append(DrugInteraction(**payload))
        if len(batch) >= batch_size:
            session.bulk_save_objects(batch)
            session.commit()
            count += len(batch)
            batch.clear()
    if batch:
        session.bulk_save_objects(batch)
        session.commit()
        count += len(batch)
    return count


def load_drug_interactions_from_csv(csv_path: str, replace: bool = False) -> int:
    """Load drug interactions from a CSV file into the database.

    Returns number of rows inserted.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    # Ensure tables exist
    Base.metadata.create_all(bind=sync_engine)

    with SessionLocal() as session:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = _bulk_insert(session, reader, replace=replace)
    return count


def load_drug_interactions_from_sqlite(sqlite_path: str, table: str = "drug_interactions", replace: bool = False) -> int:
    """Load drug interactions from an external SQLite file/table.
    The source table should have columns that map to the expected CSV headers.
    """
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(sqlite_path)

    Base.metadata.create_all(bind=sync_engine)

    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = [dict(r) for r in cur.fetchall()]

    with SessionLocal() as session:
        count = _bulk_insert(session, rows, replace=replace)
    return count


def load_drug_interactions_from_medi_co_dataset(csv_path: str, synonyms_json_path: str, replace: bool = False) -> int:
    """Load drug interactions from medi-co style dataset:
    - csv_path: CSV with columns Drug1, Drug2 (or Drug1 ID/Drug2 ID), and Interaction
    - synonyms_json_path: JSON mapping { drugbank_id: [names...] }

    We map DrugBank IDs to a primary name (first in the synonyms list), clean 'Compound::' prefix,
    and store as DrugInteraction with default 'moderate' severity.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)
    if not os.path.exists(synonyms_json_path):
        raise FileNotFoundError(synonyms_json_path)

    Base.metadata.create_all(bind=sync_engine)

    # Load synonyms
    with open(synonyms_json_path, "r", encoding="utf-8") as f:
        synonyms = json.load(f)
    id_to_name: Dict[str, str] = {str(k): (v[0] if isinstance(v, list) and v else str(k)) for k, v in synonyms.items()}

    # Stream CSV and build rows
    def _iter_rows():
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                # Accept both original and renamed columns
                id1 = (r.get("Drug1") or r.get("Drug1 ID") or r.get("drug1") or r.get("drug1 id") or "").strip()
                id2 = (r.get("Drug2") or r.get("Drug2 ID") or r.get("drug2") or r.get("drug2 id") or "").strip()
                desc = (r.get("Interaction") or r.get("interaction") or "").strip()
                if not id1 or not id2 or not desc:
                    continue
                # Clean Compound:: prefix
                if id1.startswith("Compound::"):
                    id1 = id1.split("::", 1)[1]
                if id2.startswith("Compound::"):
                    id2 = id2.split("::", 1)[1]
                name1 = id_to_name.get(id1, id1)
                name2 = id_to_name.get(id2, id2)
                yield {
                    "drug_a": name1,
                    "drug_b": name2,
                    "severity": "moderate",
                    "description": desc,
                    "mechanism": None,
                    "clinical_management": None,
                    "drugbank_id_a": id1,
                    "drugbank_id_b": id2,
                    "drug_a_aliases": None,
                    "drug_b_aliases": None,
                }

    with SessionLocal() as session:
        count = _bulk_insert(session, _iter_rows(), replace=replace)
    return count
