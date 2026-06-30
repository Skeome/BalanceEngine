"""
Empirical dimensionality check (PCA), reading from the actual verified
compound dataset in data/compounds/ rather than a hardcoded list.

This automatically grows as more compounds pass the verification gate
and get added to those CSVs -- no code changes needed to include them.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

FEATURE_COLS = ["MolWt", "LogP", "TPSA", "HBD", "HBA", "RotatableBonds",
                "FractionCSP3",  "NumHeteroatoms", "MolarRefractivity",
                "RingCount", "AromaticRings"]
# NumHeteroatoms, MolarRefractivity, RingCount, AromaticRings are also
# present in these files but excluded here to keep the same 7-feature
# basis as the curated PCA script for direct comparison. Edit FEATURE_COLS
# to use the wider descriptor set once you're ready to compare results.


def load_verified_compounds():
    bartlett = pd.read_csv("data/compounds/bartlett_verified.csv")
    tcm = pd.read_csv("data/compounds/tcm_verified.csv")

    bartlett = bartlett.rename(columns={"herb": "source"})
    tcm = tcm.rename(columns={"herb_pinyin": "source"})

    bartlett["dataset"] = "bartlett"
    tcm["dataset"] = "tcm"

    combined = pd.concat([bartlett, tcm], ignore_index=True, sort=False)

    # Drop duplicate marker compounds (e.g. chlorogenic_acid appears for
    # multiple TCM herbs) -- keep one row per unique compound so PCA isn't
    # trivially dominated by a repeated point.
    combined = combined.drop_duplicates(subset="marker_compound", keep="first")

    missing = [c for c in FEATURE_COLS if c not in combined.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}. "
                          f"Check that both CSVs have the same descriptor schema.")

    combined = combined.dropna(subset=FEATURE_COLS)
    return combined


def run_pca(df: pd.DataFrame, feature_cols: list[str]):
    X = df[feature_cols].values.astype(float)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA()
    pca.fit(X_scaled)

    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f"PC{i+1}" for i in range(len(feature_cols))],
        index=feature_cols,
    )
    return pca, loadings


if __name__ == "__main__":
    df = load_verified_compounds()
    print(f"Loaded {len(df)} unique verified compounds "
          f"({(df['dataset']=='bartlett').sum()} Bartlett, "
          f"{(df['dataset']=='tcm').sum()} TCM)\n")

    pca, loadings = run_pca(df, FEATURE_COLS)

    print("=== EMPIRICAL DIMENSIONALITY REPORT (full verified dataset) ===")
    for i, v in enumerate(pca.explained_variance_ratio_):
        print(f"PC{i+1}: {v*100:.2f}% of variance explained")

    cumulative = np.cumsum(pca.explained_variance_ratio_)
    print("\n=== CUMULATIVE VARIANCE ===")
    for i, c in enumerate(cumulative):
        print(f"Components 1 to {i+1}: {c*100:.2f}% total")

    print("\n=== FEATURE LOADINGS (PC1-PC3) ===")
    print(loadings[["PC1", "PC2", "PC3"]].round(3))

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(cumulative) + 1), cumulative, marker="o", linestyle="--")
    plt.title(f"Scree Plot: Full Verified Dataset (N={len(df)})")
    plt.xlabel("Number of Components")
    plt.ylabel("Cumulative Explained Variance")
    plt.axhline(y=0.90, color="r", linestyle=":", label="90% threshold")
    plt.grid(True)
    plt.legend()
    plt.savefig("results/pca_scree_plot_full_dataset.png", dpi=150, bbox_inches="tight")
    print("\nSaved: results/pca_scree_plot_full_dataset.png")
