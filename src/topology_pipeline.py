"""
Compute topology descriptors for the currently verified organic compounds.
This is the first pipeline step that explicitly bridges the existing organic
RDKit descriptor set with a dedicated topology layer.
"""
import csv
from pathlib import Path
from typing import List

import pandas as pd

from topology_descriptors import compute_topology_descriptors, topology_descriptor_names


VERIFIED_FILES = [
    Path("data/compounds/bartlett_verified.csv"),
    Path("data/compounds/tcm_verified.csv"),
]


def load_unique_verified_compounds(files: List[Path]) -> pd.DataFrame:
    frames = []
    for path in files:
        frames.append(pd.read_csv(path))
    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined = combined.drop_duplicates(subset=["marker_compound", "smiles"], keep="first")
    return combined[["marker_compound", "smiles", "formula_verified"]].copy()


def compute_topology_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    failures = []
    for _, row in df.iterrows():
        smiles = row["smiles"]
        try:
            topo = compute_topology_descriptors(smiles)
            row_data = {
                "marker_compound": row["marker_compound"],
                "smiles": smiles,
                "canonical_smiles": topo.canonical_smiles,
                "formula_verified": row["formula_verified"],
                "topology_formula": topo.formula,
            }
            row_data.update({f"topology_{name}": value for name, value in topo.descriptors.items()})
            rows.append(row_data)
        except Exception as exc:
            failures.append((row["marker_compound"], smiles, str(exc)))

    if failures:
        print("Topology descriptor failures:")
        for name, smiles, error in failures:
            print(f"  {name}: {smiles} -> {error}")

    return pd.DataFrame(rows)


def save_topology_descriptors(df: pd.DataFrame, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved topology descriptors for {len(df)} compounds to {out_path}")


if __name__ == "__main__":
    verified = load_unique_verified_compounds(VERIFIED_FILES)
    topology_df = compute_topology_table(verified)
    save_topology_descriptors(topology_df, Path("data/compounds/verified_topology_descriptors.csv"))
