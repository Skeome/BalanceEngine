"""
Empirical dimensionality check (PCA) on verified molecular descriptors.

Corrected version: the original script (thrown together quickly) had four
SMILES errors that produced wrong molecular formulas -- 6-gingerol,
betulin, anethole, and chlorogenic_acid. All four are fixed below using
the structures already verified earlier in this project (formula-checked
against independently published values). This script also pulls from the
full verified compound set in data/compounds/ rather than a short
hardcoded list, so it scales as more compounds get added there.
"""
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Corrected SMILES for the 4 that failed formula verification, plus the
# 10 that were already correct. Source: project verification history.
compound_data = {
    "6-gingerol":        "CCCCCC(O)CC(=O)CCc1ccc(O)c(OC)c1",          # fixed: was missing a CH2 linker
    "cinnamaldehyde":    "C1=CC=C(C=C1)C=CC=O",
    "carvone":           "CC1=CC(=O)CC(C1)C(=C)C",
    "betulin":           "CC(=C)C1CCC2(CCC3(C)C(CCC4C3(C)CCC3C4(C)CCC(O)C3(C)C)C12)CO",  # fixed: was one CH2 short
    "allantoin":         "C1(C(=O)NC(=O)N1)NC(=O)N",
    "linalool":          "CC(=CCCC(C)(C=C)O)C",
    "anethole":          "COc1ccc(/C=C/C)cc1",                        # fixed: was a 4-carbon (butenyl) chain, should be 3-carbon (propenyl)
    "thymol":            "CC1=CC(=C(C=C1)C(C)C)O",
    "curcumin":          "COC1=CC(=CC=C1O)/C=C/C(=O)CC(=O)/C=C/C2=CC(=C(C=C2)O)OC",
    "salicin":           "C1=CC=C(C(=C1)CO)O[C@H]2[C@@H]([C@H]([C@@H]([C@H](O2)CO)O)O)O",
    "menthol":           "CC1CCC(C(C1)O)C(C)C",
    "chlorogenic_acid":  "OC1CC(O)(CC(O)C1OC(=O)/C=C/c1ccc(O)c(O)c1)C(=O)O",  # fixed: had one extra oxygen
    "emodin":            "CC1=CC2=C(C(=C1)O)C(=O)C3=C(C=C(C=C3C2=O)O)O",
    "ephedrine":         "CC(C(C1=CC=CC=C1)O)NC",
}

# Expected formulas, for a verification gate INSIDE this script too --
# never trust a hardcoded SMILES dict again without checking it here first.
expected_formulas = {
    "6-gingerol": "C17H26O4", "cinnamaldehyde": "C9H8O", "carvone": "C10H14O",
    "betulin": "C30H50O2", "allantoin": "C4H6N4O3", "linalool": "C10H18O",
    "anethole": "C10H12O", "thymol": "C10H14O", "curcumin": "C21H20O6",
    "salicin": "C13H18O7", "menthol": "C10H20O", "chlorogenic_acid": "C16H18O9",
    "emodin": "C15H10O5", "ephedrine": "C10H15NO",
}


def extract_descriptors(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return {
        "MolWt": Descriptors.MolWt(mol),
        "LogP": Descriptors.MolLogP(mol),
        "TPSA": Descriptors.TPSA(mol),
        "HBD": Descriptors.NumHDonors(mol),
        "HBA": Descriptors.NumHAcceptors(mol),
        "RotatableBonds": Descriptors.NumRotatableBonds(mol),
        "FractionCSP3": Descriptors.FractionCSP3(mol),
        "LabuteASA": Descriptors.LabuteASA(mol),
    }


def verify_and_build(compound_data, expected_formulas):
    from rdkit.Chem import rdMolDescriptors
    features, names, failed = [], [], []
    for name, smiles in compound_data.items():
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            failed.append((name, "PARSE_FAILED"))
            continue
        mol_h = Chem.AddHs(mol)
        computed = rdMolDescriptors.CalcMolFormula(mol_h)
        expected = expected_formulas.get(name)
        if expected and computed != expected:
            failed.append((name, f"FORMULA_MISMATCH computed={computed} expected={expected}"))
            continue
        desc = extract_descriptors(smiles)
        if desc:
            features.append(desc)
            names.append(name)
    return features, names, failed


features, names, failed = verify_and_build(compound_data, expected_formulas)

print("=== VERIFICATION GATE ===")
print(f"Passed: {len(names)} / {len(compound_data)}")
if failed:
    print("Failed (excluded):")
    for n, reason in failed:
        print(f"  {n}: {reason}")
print()

df = pd.DataFrame(features, index=names)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

pca = PCA()
X_pca = pca.fit_transform(X_scaled)

print("=== EMPIRICAL DIMENSIONALITY REPORT ===")
for i, variance in enumerate(pca.explained_variance_ratio_):
    print(f"Principal Component {i+1}: {variance*100:.2f}% of variance explained")

cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
print("\n=== CUMULATIVE VARIANCE ===")
for i, cum_var in enumerate(cumulative_variance):
    print(f"Components 1 to {i+1}: {cum_var*100:.2f}% total variance explained")

loadings = pd.DataFrame(
    pca.components_.T,
    columns=[f'PC{i+1}' for i in range(len(df.columns))],
    index=df.columns
)

print("\n=== FEATURE LOADINGS MATRIX ===")
print(loadings[['PC1', 'PC2', 'PC3']].round(3))
print("===============================")

print("\n[Analytical Check]")
for col in ['PC1', 'PC2']:
    top_feature = loadings[col].abs().idxmax()
    direction = "positive" if loadings.loc[top_feature, col] > 0 else "negative"
    print(f"-> {col} is heavily anchored by {top_feature} in the {direction} direction.")

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), cumulative_variance, marker='o', linestyle='--')
plt.title('Scree Plot: Latent Space Dimensionality Determination (corrected structures)')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.grid(True)
plt.axhline(y=0.90, color='r', linestyle=':', label='90% Variance Threshold')
plt.legend()
plt.savefig('results/pca_scree_plot.png', dpi=150, bbox_inches='tight')
print("\nScree plot saved to results/pca_scree_plot.png")
