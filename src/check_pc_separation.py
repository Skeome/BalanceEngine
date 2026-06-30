"""
Plot verified compounds in PC1-PC3 space, colored by their REAL, ALREADY-
KNOWN Hot/Cold classification. No rotation or fitting to the labels --
this only asks whether visual separation already exists in the
descriptor-only PCA space, using labels strictly for coloring/checking,
never for fitting.

TCM compounds: colored by tcm_property_numeric (continuous -3 to +3 scale).
Bartlett compounds: colored by (hot - cold) from the ground truth table,
joined in by source herb name.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

FEATURE_COLS = ["MolWt", "LogP", "TPSA", "HBD", "HBA", "RotatableBonds",
                 "FractionCSP3", "NumHeteroatoms", "MolarRefractivity",
                 "RingCount", "AromaticRings"]


def load_and_label():
    bartlett = pd.read_csv("data/compounds/bartlett_verified.csv")
    tcm = pd.read_csv("data/compounds/tcm_verified.csv")
    gt = pd.read_csv("data/ground_truth/bartlett_measured.csv")
    gt = gt[gt['phlegm'] != '?']  # exclude Dandelion (no descriptor match anyway)
    gt['hc_signed'] = gt['hot'].astype(float) - gt['cold'].astype(float)

    bartlett = bartlett.merge(gt[['herb', 'hc_signed']], on='herb', how='left')
    bartlett['hot_cold_label'] = bartlett['hc_signed']
    bartlett['source_dataset'] = 'Bartlett'
    bartlett['display_name'] = bartlett['marker_compound']

    tcm['hot_cold_label'] = tcm['tcm_property_numeric']
    tcm['source_dataset'] = 'TCM'
    tcm['display_name'] = tcm['marker_compound']

    combined = pd.concat([bartlett, tcm], ignore_index=True, sort=False)
    combined = combined.drop_duplicates(subset='marker_compound', keep='first')
    combined = combined.dropna(subset=FEATURE_COLS + ['hot_cold_label'])
    return combined


def main():
    df = load_and_label()
    print(f"N = {len(df)} compounds with both descriptors and a real Hot/Cold label")
    print(f"  Bartlett: {(df['source_dataset']=='Bartlett').sum()}")
    print(f"  TCM: {(df['source_dataset']=='TCM').sum()}")

    X = df[FEATURE_COLS].values.astype(float)
    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA(n_components=3)
    coords = pca.fit_transform(X_scaled)
    df['PC1'], df['PC2'], df['PC3'] = coords[:, 0], coords[:, 1], coords[:, 2]

    print(f"\nVariance explained: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, "
          f"PC2={pca.explained_variance_ratio_[1]*100:.1f}%, "
          f"PC3={pca.explained_variance_ratio_[2]*100:.1f}%")

    # Correlation of each PC with the real label -- the actual test,
    # no fitting, just checking what's already there
    print("\n=== Correlation of each PC with REAL Hot/Cold label (no fitting) ===")
    for pc in ['PC1', 'PC2', 'PC3']:
        r_all = np.corrcoef(df[pc], df['hot_cold_label'])[0, 1]
        r_bartlett = np.corrcoef(df.loc[df['source_dataset']=='Bartlett', pc],
                                   df.loc[df['source_dataset']=='Bartlett', 'hot_cold_label'])[0, 1]
        r_tcm = np.corrcoef(df.loc[df['source_dataset']=='TCM', pc],
                              df.loc[df['source_dataset']=='TCM', 'hot_cold_label'])[0, 1]
        print(f"  {pc}: all={r_all:+.3f}  Bartlett-only={r_bartlett:+.3f}  TCM-only={r_tcm:+.3f}")

    # Plot: PC1 vs PC3 (the two most likely candidates), colored by label,
    # marker shape by source dataset
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    for ax, (x_pc, y_pc) in zip(axes, [('PC1', 'PC3'), ('PC2', 'PC3')]):
        for dataset, marker in [('Bartlett', 'o'), ('TCM', '^')]:
            sub = df[df['source_dataset'] == dataset]
            sc = ax.scatter(sub[x_pc], sub[y_pc], c=sub['hot_cold_label'],
                             cmap='coolwarm', marker=marker, s=90,
                             edgecolors='black', linewidths=0.5,
                             label=dataset, vmin=df['hot_cold_label'].min(),
                             vmax=df['hot_cold_label'].max())
        ax.set_xlabel(x_pc)
        ax.set_ylabel(y_pc)
        ax.set_title(f"{x_pc} vs {y_pc}, colored by real Hot(red)<->Cold(blue) label")
        ax.legend()
        ax.axhline(0, color='gray', linewidth=0.5)
        ax.axvline(0, color='gray', linewidth=0.5)

    plt.colorbar(sc, ax=axes, label='Hot <-> Cold (real label)')
    plt.savefig("results/pc_space_colored_by_real_label.png", dpi=150, bbox_inches='tight')
    print("\nSaved: results/pc_space_colored_by_real_label.png")


if __name__ == "__main__":
    main()
