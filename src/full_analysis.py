"""
Full N=101 analysis pipeline.

Combines ALL verified compound sources (bartlett_verified, tcm_verified,
batch1, batch2), deduplicates by marker_compound, computes both RDKit
and atomic descriptors for every compound with a hot/cold label,
runs correlation analysis, PCA, and the Phase 1 Procrustes projection.

This supersedes the earlier compare_atomic_vs_rdkit.py (N=44) and
phase1_pca.py scripts by operating on the full verified dataset.
"""
import sys
import re
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_score

from atomic_descriptors import formula_descriptors
from verify_compound import verify_compound, CORE_DESCRIPTOR_FUNCS, RING_DESCRIPTOR_FUNCS
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors


def parse_formula(formula_str: str) -> dict:
    """Minimal formula parser, e.g. 'C17H26O4' -> {'C':17,'H':26,'O':4}"""
    tokens = re.findall(r'([A-Z][a-z]?)(\d*)', formula_str)
    result = {}
    for sym, count in tokens:
        if sym == "":
            continue
        result[sym] = int(count) if count else 1
    return result


def normalize_label(label_str: str) -> float:
    """Convert TCM/Bartlett text labels to a numeric hot/cold scale.
    Scale: great hot=3, hot=2, warm=1.5, mildly warm=1,
           even/neutral=0, cool=-1, mildly cold=-1.5, cold=-2, great cold=-3
    """
    mapping = {
        'great hot': 3.0, 'hot': 2.0, 'warm': 1.5, 'mildly warm': 1.0,
        'even': 0.0, 'neutral': 0.0,
        'cool': -1.0, 'mildly cold': -1.5, 'cold': -2.0, 'great cold': -3.0,
    }
    if isinstance(label_str, (int, float)):
        return float(label_str)
    cleaned = str(label_str).strip().lower()
    if cleaned in mapping:
        return mapping[cleaned]
    try:
        return float(cleaned)
    except ValueError:
        return None


def compute_rdkit_descriptors(smiles: str) -> dict:
    """Compute the standard RDKit descriptors from a SMILES string."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    desc = {}
    for name, func in CORE_DESCRIPTOR_FUNCS.items():
        desc[name] = round(func(mol), 3)
    for name, func in RING_DESCRIPTOR_FUNCS.items():
        desc[name] = func(mol)
    return desc


def load_all_labeled_compounds() -> pd.DataFrame:
    """Load and unify all compound data from every verified source file."""
    data_dir = Path(__file__).parent.parent / "data" / "compounds"

    rows = []

    # 1. Bartlett verified (herbs with ground-truth measured H/C/W/D)
    bartlett = pd.read_csv(data_dir / "bartlett_verified.csv")
    gt = pd.read_csv(data_dir.parent / "ground_truth" / "bartlett_measured.csv")
    gt_clean = gt[gt['phlegm'] != '?'].copy()
    gt_clean['hot_val'] = gt_clean['hot'].astype(float)
    gt_clean['cold_val'] = gt_clean['cold'].astype(float)
    gt_clean['hc_numeric'] = gt_clean['hot_val'] - gt_clean['cold_val']
    bartlett = bartlett.merge(gt_clean[['herb', 'hc_numeric', 'hot_val', 'cold_val']],
                              on='herb', how='inner')
    for _, row in bartlett.iterrows():
        rows.append({
            'marker_compound': row['marker_compound'],
            'smiles': row['smiles'],
            'formula_verified': row['formula_verified'],
            'hc_numeric': row['hc_numeric'],
            'source': 'bartlett',
            'source_herb': row['herb'],
        })

    # 2. TCM verified
    tcm = pd.read_csv(data_dir / "tcm_verified.csv")
    for _, row in tcm.iterrows():
        hc = normalize_label(row.get('tcm_property_numeric', row.get('tcm_property', '')))
        if hc is None:
            continue
        rows.append({
            'marker_compound': row['marker_compound'],
            'smiles': row['smiles'],
            'formula_verified': row['formula_verified'],
            'hc_numeric': hc,
            'source': 'tcm',
            'source_herb': row.get('herb_pinyin', ''),
        })

    # 3. Batch 1
    b1 = pd.read_csv(data_dir / "batch1.csv")
    for _, row in b1.iterrows():
        hc = normalize_label(row.get('label', ''))
        if hc is None:
            continue
        rows.append({
            'marker_compound': row['marker_compound'],
            'smiles': row['smiles'],
            'formula_verified': row['formula_verified'],
            'hc_numeric': hc,
            'source': 'batch1',
            'source_herb': row.get('source_name', ''),
        })

    # 4. Batch 2
    b2 = pd.read_csv(data_dir / "batch2.csv")
    for _, row in b2.iterrows():
        hc = normalize_label(row.get('label', ''))
        if hc is None:
            continue
        rows.append({
            'marker_compound': row['marker_compound'],
            'smiles': row['smiles'],
            'formula_verified': row['formula_verified'],
            'hc_numeric': hc,
            'source': 'batch2',
            'source_herb': row.get('source_name', ''),
        })

    df = pd.DataFrame(rows)
    # Deduplicate by marker_compound, prefer bartlett > tcm > batch
    priority = {'bartlett': 0, 'tcm': 1, 'batch1': 2, 'batch2': 3}
    df['_priority'] = df['source'].map(priority)
    df = df.sort_values('_priority').drop_duplicates(subset='marker_compound', keep='first')
    df = df.drop(columns=['_priority'])
    return df.reset_index(drop=True)


def main():
    print("=" * 70)
    print("BALANCE ENGINE — FULL DATASET ANALYSIS (N=101 target)")
    print("=" * 70)

    # ── Load all compounds ──
    df = load_all_labeled_compounds()
    print(f"\n[1] Loaded {len(df)} unique labeled compounds from all sources")
    print(f"    Bartlett: {(df['source']=='bartlett').sum()}")
    print(f"    TCM:      {(df['source']=='tcm').sum()}")
    print(f"    Batch 1:  {(df['source']=='batch1').sum()}")
    print(f"    Batch 2:  {(df['source']=='batch2').sum()}")

    # ── Compute RDKit descriptors ──
    print(f"\n[2] Computing RDKit descriptors...")
    rdkit_results = []
    rdkit_failed = []
    for _, row in df.iterrows():
        desc = compute_rdkit_descriptors(row['smiles'])
        if desc is not None:
            rdkit_results.append({'marker_compound': row['marker_compound'], **desc})
        else:
            rdkit_failed.append(row['marker_compound'])

    rdkit_df = pd.DataFrame(rdkit_results)
    df = df.merge(rdkit_df, on='marker_compound', how='inner')
    print(f"    RDKit succeeded: {len(rdkit_df)}, failed: {len(rdkit_failed)}")
    if rdkit_failed:
        print(f"    Failed: {rdkit_failed}")

    # ── Compute atomic descriptors ──
    print(f"\n[3] Computing atomic descriptors...")
    atomic_results = []
    atomic_failed = []
    for _, row in df.iterrows():
        try:
            formula = parse_formula(row['formula_verified'])
            desc = formula_descriptors(formula)
            desc['marker_compound'] = row['marker_compound']
            atomic_results.append(desc)
        except Exception as e:
            atomic_failed.append((row['marker_compound'], str(e)))

    atomic_df = pd.DataFrame(atomic_results)
    df = df.merge(atomic_df, on='marker_compound', how='inner')
    print(f"    Atomic succeeded: {len(atomic_df)}, failed: {len(atomic_failed)}")
    if atomic_failed:
        for name, err in atomic_failed:
            print(f"    FAILED {name}: {err}")

    N = len(df)
    print(f"\n[4] Final unified dataset: N = {N}")

    # ── Correlation analysis ──
    print(f"\n{'='*70}")
    print(f"CORRELATION ANALYSIS (N={N})")
    print(f"{'='*70}")

    rdkit_fields = ['LogP', 'TPSA', 'HBD', 'HBA', 'MolWt', 'RotatableBonds',
                    'FractionCSP3', 'NumHeteroatoms', 'MolarRefractivity',
                    'AromaticRings', 'RingCount']
    atomic_fields = ['avg_electronegativity_pauling', 'avg_first_ionization_energy',
                     'avg_electron_affinity', 'avg_dipole_polarizability',
                     'avg_covalent_radius', 'avg_atomic_radius',
                     'electronegativity_spread', 'avg_thermal_conductivity',
                     'avg_density', 'avg_melting_point']

    results = []
    for f in rdkit_fields:
        if f in df.columns:
            valid = df[f].notna()
            if valid.sum() > 2:
                r = np.corrcoef(df.loc[valid, f], df.loc[valid, 'hc_numeric'])[0, 1]
                results.append((f, r, "RDKit (bond-graph)"))
    for f in atomic_fields:
        if f in df.columns:
            valid = df[f].notna()
            if valid.sum() > 2:
                r = np.corrcoef(df.loc[valid, f], df.loc[valid, 'hc_numeric'])[0, 1]
                results.append((f, r, "Atomic (composition)"))

    results.sort(key=lambda x: -abs(x[1]) if not np.isnan(x[1]) else 0)
    print(f"\n{'Descriptor':<35}{'r':<10}{'Layer'}")
    print("-" * 65)
    for f, r, layer in results:
        print(f"{f:<35}{r:<10.3f}{layer}")

    # ── Split-check: Bartlett-only vs rest ──
    print(f"\n{'='*70}")
    print(f"SPLIT-CHECK: Bartlett-only vs Non-Bartlett")
    print(f"{'='*70}")
    bartlett_mask = df['source'] == 'bartlett'
    non_bartlett_mask = ~bartlett_mask
    n_b = bartlett_mask.sum()
    n_nb = non_bartlett_mask.sum()
    print(f"  Bartlett N={n_b}, Non-Bartlett N={n_nb}")

    leading = [r[0] for r in results[:7]]
    print(f"\n{'Descriptor':<35}{'Bartlett r':<15}{'Other r':<15}")
    print("-" * 65)
    for f in leading:
        if f in df.columns:
            b_valid = df.loc[bartlett_mask, f].notna()
            nb_valid = df.loc[non_bartlett_mask, f].notna()
            r_b = np.corrcoef(df.loc[bartlett_mask & df[f].notna(), f],
                              df.loc[bartlett_mask & df[f].notna(), 'hc_numeric'])[0, 1] if b_valid.sum() > 2 else float('nan')
            r_nb = np.corrcoef(df.loc[non_bartlett_mask & df[f].notna(), f],
                               df.loc[non_bartlett_mask & df[f].notna(), 'hc_numeric'])[0, 1] if nb_valid.sum() > 2 else float('nan')
            print(f"{f:<35}{r_b:<15.3f}{r_nb:<15.3f}")

    # ── PCA on combined descriptors ──
    print(f"\n{'='*70}")
    print(f"PCA (N={N})")
    print(f"{'='*70}")

    pca_features = ['MolWt', 'LogP', 'TPSA', 'HBD', 'HBA', 'RotatableBonds',
                    'FractionCSP3', 'NumHeteroatoms', 'MolarRefractivity',
                    'AromaticRings', 'RingCount',
                    'avg_electronegativity_pauling', 'avg_first_ionization_energy',
                    'avg_electron_affinity', 'avg_dipole_polarizability',
                    'avg_covalent_radius', 'avg_atomic_radius',
                    'avg_thermal_conductivity', 'avg_density']

    # Keep only features that exist and aren't all-NaN
    available = [f for f in pca_features if f in df.columns and df[f].notna().sum() > N * 0.5]
    df_pca = df.dropna(subset=available).copy()
    N_pca = len(df_pca)
    print(f"  Features used: {len(available)}")
    print(f"  Compounds with complete data: {N_pca}")

    X = df_pca[available].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    print(f"\n  Explained Variance:")
    print(f"  {'Component':<12}{'Variance %':<15}{'Cumulative %'}")
    cumulative = 0.0
    for i, ev in enumerate(pca.explained_variance_ratio_):
        cumulative += ev
        print(f"  PC{i+1:<9}{ev*100:<15.2f}{cumulative*100:.2f}")
        if i >= 7:
            break

    # Add PC columns
    for i in range(min(4, X_pca.shape[1])):
        df_pca[f'PC{i+1}'] = X_pca[:, i]

    # PC loadings
    print(f"\n  Top PC1 loadings:")
    loadings = pd.DataFrame(pca.components_[:4].T, index=available, columns=[f'PC{i+1}' for i in range(4)])
    for pc in ['PC1', 'PC2', 'PC3', 'PC4']:
        top = loadings[pc].abs().nlargest(5)
        print(f"\n    {pc}:")
        for feat, val in loadings.loc[top.index, pc].items():
            print(f"      {feat:<35} {val:+.3f}")

    # PC vs label correlations
    print(f"\n  PC vs Hot/Cold label correlations:")
    for i in range(min(4, X_pca.shape[1])):
        pcname = f'PC{i+1}'
        r = np.corrcoef(df_pca[pcname], df_pca['hc_numeric'])[0, 1]
        print(f"    {pcname}: r = {r:.3f}")

    # ── Phase 1: Procrustes projection using Bartlett as calibration anchor ──
    print(f"\n{'='*70}")
    print(f"PHASE 1: PROCRUSTES PROJECTION")
    print(f"{'='*70}")

    gt = pd.read_csv(Path(__file__).parent.parent / "data" / "ground_truth" / "bartlett_measured.csv")
    gt_clean = gt[gt['phlegm'] != '?'].copy()
    gt_clean['Hot_Cold'] = gt_clean['hot'].astype(float) - gt_clean['cold'].astype(float)
    gt_clean['Dry_Wet'] = gt_clean['dry'].astype(float) - gt_clean['phlegm'].astype(float)

    bartlett_data = df_pca[df_pca['source'] == 'bartlett'].merge(
        gt_clean[['herb', 'Hot_Cold', 'Dry_Wet']].rename(columns={'herb': 'source_herb'}),
        on='source_herb', how='inner'
    )
    n_calib = len(bartlett_data)
    print(f"  Calibration herbs (Bartlett with measured H/C/W/D): {n_calib}")

    if n_calib >= 4:
        pc_cols = [f'PC{i+1}' for i in range(min(4, X_pca.shape[1]))]
        X_calib = bartlett_data[pc_cols].values
        y_hc = bartlett_data['Hot_Cold'].values
        y_dw = bartlett_data['Dry_Wet'].values

        lr_hc = LinearRegression()
        lr_hc.fit(X_calib, y_hc)
        lr_dw = LinearRegression()
        lr_dw.fit(X_calib, y_dw)

        # Calibration performance
        hc_pred = lr_hc.predict(X_calib)
        dw_pred = lr_dw.predict(X_calib)
        r_hc_calib = np.corrcoef(y_hc, hc_pred)[0, 1]
        r_dw_calib = np.corrcoef(y_dw, dw_pred)[0, 1]
        r2_hc = lr_hc.score(X_calib, y_hc)
        r2_dw = lr_dw.score(X_calib, y_dw)
        print(f"  Hot/Cold  calibration: R²={r2_hc:.3f}, r={r_hc_calib:.3f}")
        print(f"  Dry/Wet   calibration: R²={r2_dw:.3f}, r={r_dw_calib:.3f}")

        # LOOCV on Bartlett
        loo = LeaveOneOut()
        loocv_hc = cross_val_score(LinearRegression(), X_calib, y_hc, cv=loo, scoring='r2')
        loocv_dw = cross_val_score(LinearRegression(), X_calib, y_dw, cv=loo, scoring='r2')
        print(f"  Hot/Cold  LOOCV R²: {np.mean(loocv_hc):.3f}")
        print(f"  Dry/Wet   LOOCV R²: {np.mean(loocv_dw):.3f}")

        # Project ALL compounds
        df_pca['pred_Hot_Cold'] = lr_hc.predict(df_pca[pc_cols].values)
        df_pca['pred_Dry_Wet'] = lr_dw.predict(df_pca[pc_cols].values)

        # Validate on non-Bartlett (held-out)
        non_bartlett = df_pca[df_pca['source'] != 'bartlett']
        if len(non_bartlett) > 2:
            # Correlation of predicted Hot/Cold vs actual numeric label
            r_val = np.corrcoef(non_bartlett['hc_numeric'], non_bartlett['pred_Hot_Cold'])[0, 1]
            print(f"\n  Held-out validation (non-Bartlett, N={len(non_bartlett)}):")
            print(f"    pred_Hot_Cold vs actual hc_numeric:  r = {r_val:.3f}")

        # Source-level breakdown
        print(f"\n  Source-level validation:")
        for src in ['tcm', 'batch1', 'batch2']:
            subset = df_pca[df_pca['source'] == src]
            if len(subset) > 2:
                r = np.corrcoef(subset['hc_numeric'], subset['pred_Hot_Cold'])[0, 1]
                print(f"    {src:<10} (N={len(subset):<3}): r = {r:.3f}")
    else:
        print("  NOT ENOUGH BARTLETT CALIBRATION DATA")

    # ── Class balance ──
    print(f"\n{'='*70}")
    print(f"CLASS BALANCE")
    print(f"{'='*70}")
    hot_mask = df['hc_numeric'] > 0
    cold_mask = df['hc_numeric'] < 0
    even_mask = df['hc_numeric'] == 0
    print(f"  Hot-side (>0):  {hot_mask.sum()}")
    print(f"  Even (=0):      {even_mask.sum()}")
    print(f"  Cold-side (<0): {cold_mask.sum()}")

    # ── Save outputs ──
    out_dir = Path(__file__).parent.parent / "exports"
    out_dir.mkdir(exist_ok=True)

    df_pca.to_csv(out_dir / "phase1_full_predictions.csv", index=False)
    df.to_csv(out_dir / "full_n101_dataset.csv", index=False)
    print(f"\n[DONE] Saved {len(df_pca)} records to exports/phase1_full_predictions.csv")
    print(f"[DONE] Saved {len(df)} records to exports/full_n101_dataset.csv")

    # ── Summary JSON for report update ──
    summary = {
        'N_total': int(N),
        'N_bartlett': int((df['source'] == 'bartlett').sum()),
        'N_tcm': int((df['source'] == 'tcm').sum()),
        'N_batch1': int((df['source'] == 'batch1').sum()),
        'N_batch2': int((df['source'] == 'batch2').sum()),
        'N_pca': int(N_pca),
        'pca_features_used': len(available),
        'pca_variance_4pc': round(sum(pca.explained_variance_ratio_[:4]) * 100, 2),
        'correlations': [(f, round(r, 3), layer) for f, r, layer in results],
        'class_balance': {
            'hot_side': int(hot_mask.sum()),
            'even': int(even_mask.sum()),
            'cold_side': int(cold_mask.sum()),
        },
    }
    with open(out_dir / "analysis_summary.json", 'w') as fh:
        json.dump(summary, fh, indent=2)
    print(f"[DONE] Saved analysis summary to exports/analysis_summary.json")


if __name__ == '__main__':
    main()
