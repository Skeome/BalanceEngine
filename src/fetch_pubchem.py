"""
PubChem fetcher -- unblocked on a normally-networked machine (this was the
primary bottleneck during sandboxed development, where pubchem.ncbi.nlm.nih.gov
was unreachable and every compound had to be manually sourced and
cross-verified by hand).

Always pipe results through verify_compound.verify_compound() before
trusting them -- PubChem entries can still have data-quality issues
(see: the menthone SMILES mismatch found on a third-party vendor page
during manual sourcing, contradicted by every other independent source).
Never skip verification just because the source is now automated.
"""
import time
import pubchempy as pcp
from dataclasses import dataclass
from typing import Optional


@dataclass
class FetchResult:
    query: str
    found: bool
    cid: Optional[int] = None
    canonical_smiles: Optional[str] = None
    molecular_formula: Optional[str] = None
    iupac_name: Optional[str] = None
    error: Optional[str] = None


def fetch_compound(name_or_cid, by: str = "name", retries: int = 3, delay: float = 0.4) -> FetchResult:
    """
    by: 'name', 'cid', 'smiles', or 'inchikey'
    Politeness delay is applied to avoid hammering PubChem's servers --
    keep this even though rate limits are more permissive than the
    sandbox's total network block.
    """
    for attempt in range(retries):
        try:
            results = pcp.get_compounds(name_or_cid, by)
            if not results:
                return FetchResult(query=str(name_or_cid), found=False, error="NOT_FOUND")
            c = results[0]
            time.sleep(delay)
            return FetchResult(
                query=str(name_or_cid), found=True, cid=c.cid,
                canonical_smiles=c.canonical_smiles,
                molecular_formula=c.molecular_formula,
                iupac_name=c.iupac_name,
            )
        except Exception as e:
            if attempt == retries - 1:
                return FetchResult(query=str(name_or_cid), found=False, error=str(e))
            time.sleep(delay * (attempt + 1))


def fetch_batch(names: list[str], by: str = "name") -> tuple[list[FetchResult], list[FetchResult]]:
    found, missing = [], []
    for n in names:
        r = fetch_compound(n, by=by)
        (found if r.found else missing).append(r)
    return found, missing


if __name__ == "__main__":
    # Smoke test -- requires real network access, will fail in any
    # environment where pubchem.ncbi.nlm.nih.gov is blocked
    test_names = ["curcumin", "menthol", "this_should_not_exist_xyz123"]
    found, missing = fetch_batch(test_names)
    print(f"FOUND ({len(found)}):")
    for r in found:
        print(f"  {r.query}: CID {r.cid}, {r.molecular_formula}, {r.canonical_smiles}")
    print(f"MISSING ({len(missing)}):")
    for r in missing:
        print(f"  {r.query}: {r.error}")
