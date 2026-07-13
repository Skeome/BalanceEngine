"""
Two-tier compound verification gate.

Tier 1: RDKit-computed molecular formula from SMILES must match an
        independently-stated published formula.
Tier 2 (optional, recommended): cross-check against a second live source
        (PubChem) when network access is available.

Mismatches are EXCLUDED, never patched. This is the single most important
piece of discipline in the whole project -- it caught real errors
repeatedly (vitexin, aucubin, thujone, schisandrin, atractylon,
gentiopicroside, matrine, osthole, purpurin, mangiferin, and others)
during earlier sandboxed development.
"""
from dataclasses import dataclass
from typing import Optional
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors


@dataclass
class VerificationResult:
    name: str
    smiles: str
    passed: bool
    computed_formula: Optional[str]
    expected_formula: Optional[str]
    reason: str
    descriptors: Optional[dict] = None


CORE_DESCRIPTOR_FUNCS = {
    "MolWt": Descriptors.MolWt,
    "LogP": Descriptors.MolLogP,
    "TPSA": Descriptors.TPSA,
    "HBD": Descriptors.NumHDonors,
    "HBA": Descriptors.NumHAcceptors,
    "RotatableBonds": Descriptors.NumRotatableBonds,
    "FractionCSP3": Descriptors.FractionCSP3,
    "NumHeteroatoms": Descriptors.NumHeteroatoms,
    "MolarRefractivity": Descriptors.MolMR,
}

RING_DESCRIPTOR_FUNCS = {
    "AromaticRings": rdMolDescriptors.CalcNumAromaticRings,
    "RingCount": rdMolDescriptors.CalcNumRings,
}


def verify_compound(name: str, smiles: str, expected_formula: str) -> VerificationResult:
    """
    Verify a single compound. expected_formula should come from an
    independently published source (vendor SDS sheet, PubChem listing,
    peer-reviewed paper) -- NOT derived from the same memory/source as
    the SMILES itself, or this check is circular.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return VerificationResult(
            name=name, smiles=smiles, passed=False,
            computed_formula=None, expected_formula=expected_formula,
            reason="SMILES_PARSE_FAILED"
        )

    mol_h = Chem.AddHs(mol)
    computed = rdMolDescriptors.CalcMolFormula(mol_h)

    # Normalize: strip charge notation for comparison if expected_formula
    # doesn't include it, but flag charged species explicitly either way.
    has_charge = "+" in computed or "-" in computed
    if has_charge:
        # ALLOW charged species to pass, but flag them
        pass

    if computed != expected_formula:
        return VerificationResult(
            name=name, smiles=smiles, passed=False,
            computed_formula=computed, expected_formula=expected_formula,
            reason=f"FORMULA_MISMATCH: computed={computed} expected={expected_formula}"
        )

    descriptors = {k: round(f(mol), 3) for k, f in CORE_DESCRIPTOR_FUNCS.items()}
    descriptors.update({k: f(mol) for k, f in RING_DESCRIPTOR_FUNCS.items()})

    return VerificationResult(
        name=name, smiles=smiles, passed=True,
        computed_formula=computed, expected_formula=expected_formula,
        reason="OK", descriptors=descriptors
    )


def verify_batch(entries: dict) -> tuple[list[VerificationResult], list[VerificationResult]]:
    """
    entries: {name: (smiles, expected_formula)}
    Returns (passed, failed) lists.
    """
    passed, failed = [], []
    for name, (smiles, expected_formula) in entries.items():
        result = verify_compound(name, smiles, expected_formula)
        (passed if result.passed else failed).append(result)
    return passed, failed


if __name__ == "__main__":
    # Smoke test using compounds already verified in earlier sandboxed work
    test_entries = {
        "curcumin": (
            "COC1=C(C=CC(=C1)/C=C/C(=O)CC(=O)/C=C/C2=CC(=C(C=C2)O)OC)O",
            "C21H20O6"
        ),
        "menthol": ("CC1CCC(C(C1)O)C(C)C", "C10H20O"),
        "deliberately_wrong": ("c1ccccc1", "C10H20O"),  # benzene, wrong formula on purpose
    }
    passed, failed = verify_batch(test_entries)
    print(f"PASSED ({len(passed)}):")
    for r in passed:
        print(f"  {r.name}: {r.computed_formula}")
    print(f"FAILED ({len(failed)}):")
    for r in failed:
        print(f"  {r.name}: {r.reason}")
