"""
End-to-end pipeline: take a list of (herb_or_source_name, marker_compound_name,
target_label) tuples, fetch each compound from PubChem, verify it, and save
a clean descriptor CSV.

This replaces the manual "search -> hand-write SMILES -> verify" loop used
during sandboxed development. On a machine with real network access this
should be the main way new compounds enter data/compounds/.

Usage pattern:
    entries = [
        ("Birch lvs", "betulin", "warm"),
        ("Caraway sd", "carvone", "warm"),
        ...
    ]
    build_dataset(entries, out_path="data/compounds/new_batch.csv")
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_pubchem import fetch_compound
from verify_compound import verify_compound


def build_dataset(entries: list[tuple[str, str, str]], out_path: str,
                   expected_formulas: dict[str, str] | None = None):
    """
    entries: list of (source_name, marker_compound, label)
    expected_formulas: optional {marker_compound: formula} to verify against
                        an INDEPENDENT source rather than trusting PubChem's
                        own formula field circularly. If not given, PubChem's
                        own stated formula is used as the verification target
                        (weaker check -- flagged in the output).
    """
    rows = []
    skipped = []

    for source_name, compound_name, label in entries:
        fetch_result = fetch_compound(compound_name, by="name")
        if not fetch_result.found:
            skipped.append((source_name, compound_name, f"FETCH_FAILED: {fetch_result.error}"))
            continue

        expected = None
        verification_strength = "weak (PubChem self-reported formula)"
        if expected_formulas and compound_name in expected_formulas:
            expected = expected_formulas[compound_name]
            verification_strength = "strong (independent source)"
        else:
            expected = fetch_result.molecular_formula

        verify_result = verify_compound(compound_name, fetch_result.canonical_smiles, expected)
        if not verify_result.passed:
            skipped.append((source_name, compound_name, f"VERIFY_FAILED: {verify_result.reason}"))
            continue

        row = {
            "source_name": source_name,
            "marker_compound": compound_name,
            "label": label,
            "cid": fetch_result.cid,
            "smiles": fetch_result.canonical_smiles,
            "formula_verified": verify_result.computed_formula,
            "verification_strength": verification_strength,
            **verify_result.descriptors,
        }
        rows.append(row)

    if rows:
        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    print(f"Saved {len(rows)} verified compounds to {out_path}")
    print(f"Skipped {len(skipped)}:")
    for s in skipped:
        print(f"  {s}")

    return rows, skipped


if __name__ == "__main__":
    print("This module requires real PubChem network access to run.")
    print("Example usage is documented in the module docstring.")
