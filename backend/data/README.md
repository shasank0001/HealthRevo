# Drug Interactions Data

Place your interaction data file(s) here.

Recommended: a UTF-8 CSV at `backend/data/drug_interactions.csv` with headers:

- drug_a (required)
- drug_b (required)
- severity (minor|moderate|major|contraindicated)
- description (required)
- mechanism (optional)
- clinical_management (optional)
- drugbank_id_a (optional)
- drugbank_id_b (optional)
- drug_a_aliases (optional; JSON array or semicolon-separated list)
- drug_b_aliases (optional; JSON array or semicolon-separated list)

Import into DB:

```bash
python backend/scripts/seed_drug_interactions.py --csv backend/data/drug_interactions.csv --replace
```

Alternatively, import from an external SQLite DB/table:

```bash
python backend/scripts/seed_drug_interactions.py --sqlite /path/to/source.db --table drug_interactions --replace
```
