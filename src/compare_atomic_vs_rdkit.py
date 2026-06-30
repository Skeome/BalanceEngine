"""
Direct test: do atomic-level (composition-weighted) descriptors correlate
with real Hot/Cold labels anywhere near as well as RDKit's bond-graph-aware
descriptors (TPSA, LogP, HBD) did?

If yes: the atomic layer is a real bridge between organic and inorganic
domains, not just a fallback for when RDKit can't parse something.
If no: it may still be necessary for inorganics (where there's no
alternative), but shouldn't be expected to match RDKit's performance on
organics specifically.
"""
import sys
sys.path.insert(0, "src")
import pandas as pd
import numpy as np
from atomic_descriptors import formula_descriptors
import re


def parse_formula(formula_str: str) -> dict:
    """Minimal CHNOPS-style formula parser, e.g. 'C17H26O4' -> {'C':17,'H':26,'O':4}"""
    tokens = re.findall(r'([A-Z][a-z]?)(\d*)', formula_str)
    result = {}
    for sym, count in tokens:
        if sym == "":
            continue
        result[sym] = int(count) if count else 1
    return result


def main():
    bartlett = pd.read_csv("data/compounds/bartlett_verified.csv")
    tcm = pd.read_csv("data/compounds/tcm_verified.csv")
    gt = pd.read_csv("data/ground_truth/bartlett_measured.csv")
    gt = gt[gt['phlegm'] != '?']
    gt['hc_signed'] = gt['hot'].astype(float) - gt['cold'].astype(float)

    bartlett = bartlett.merge(gt[['herb', 'hc_signed']], on='herb', how='left')
    bartlett['hot_cold_label'] = bartlett['hc_signed']
    tcm['hot_cold_label'] = tcm['tcm_property_numeric']

    combined = pd.concat([bartlett, tcm], ignore_index=True, sort=False)
    combined = combined.drop_duplicates(subset='marker_compound', keep='first')
    combined = combined.dropna(subset=['hot_cold_label', 'formula_verified'])

    print(f"Computing atomic-level descriptors for {len(combined)} compounds...")
    atomic_rows = []
    failed = []
    for _, row in combined.iterrows():
        try:
            formula = parse_formula(row['formula_verified'])
            desc = formula_descriptors(formula)
            desc['marker_compound'] = row['marker_compound']
            atomic_rows.append(desc)
        except Exception as e:
            failed.append((row['marker_compound'], str(e)))

    print(f"  Succeeded: {len(atomic_rows)}, Failed: {len(failed)}")
    for name, err in failed:
        print(f"    FAILED {name}: {err}")

    atomic_df = pd.DataFrame(atomic_rows)
    merged = combined.merge(atomic_df, on='marker_compound', how='inner')

    print(f"\n=== Correlation with REAL Hot/Cold label (N={len(merged)}) ===")
    print(f"{'Descriptor':<35}{'r':<10}{'Layer'}")
    print("-" * 60)

    rdkit_fields = ['TPSA', 'LogP', 'HBD', 'HBA', 'MolWt']
    atomic_fields = ['avg_electronegativity_pauling', 'avg_first_ionization_energy',
                      'avg_electron_affinity', 'avg_dipole_polarizability',
                      'avg_covalent_radius', 'avg_atomic_radius',
                      'electronegativity_spread', 'avg_thermal_conductivity', 'avg_density']

    results = []
    for f in rdkit_fields:
        r = np.corrcoef(merged[f], merged['hot_cold_label'])[0, 1]
        results.append((f, r, "RDKit (bond-graph)"))
    for f in atomic_fields:
        valid = merged[f].notna()
        if valid.sum() > 2:
            r = np.corrcoef(merged.loc[valid, f], merged.loc[valid, 'hot_cold_label'])[0, 1]
        else:
            r = float('nan')
        results.append((f, r, "Atomic (composition)"))

    results.sort(key=lambda x: -abs(x[1]) if not np.isnan(x[1]) else 0)
    for f, r, layer in results:
        print(f"{f:<35}{r:<10.3f}{layer}")

    merged.to_csv("data/compounds/combined_rdkit_and_atomic.csv", index=False)
    print("\nSaved combined descriptor set to data/compounds/combined_rdkit_and_atomic.csv")


if __name__ == "__main__":
    main()
