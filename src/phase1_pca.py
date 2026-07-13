import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def main():
    # 1. Load data
    df = pd.read_csv("../data/compounds/combined_rdkit_and_atomic.csv")
    gt = pd.read_csv("../data/ground_truth/bartlett_measured.csv")
    gt = gt[gt['phlegm'] != '?']
    
    # Calculate target labels (Hot/Cold, Dry/Wet)
    gt['Hot_Cold'] = gt['hot'].astype(float) - gt['cold'].astype(float)
    gt['Dry_Wet'] = gt['dry'].astype(float) - gt['phlegm'].astype(float)
    
    # Map herbs to their marker compounds
    bartlett_verified = pd.read_csv("../data/compounds/bartlett_verified.csv")
    gt = gt.merge(bartlett_verified[['herb', 'marker_compound']], on='herb', how='inner')
    
    features = ['TPSA', 'LogP', 'HBD', 'HBA', 'MolWt', 
                'avg_electronegativity_pauling', 'avg_first_ionization_energy',
                'avg_electron_affinity', 'avg_dipole_polarizability',
                'avg_covalent_radius', 'avg_atomic_radius',
                'avg_thermal_conductivity', 'avg_density']
                
    df = df.dropna(subset=features)
    
    X = df[features].values
    
    # 2. PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=4)
    X_pca = pca.fit_transform(X_scaled)
    
    print("--- PCA Results ---")
    print(f"Explained Variance Ratio (top 4): {pca.explained_variance_ratio_}")
    print(f"Total Explained Variance: {sum(pca.explained_variance_ratio_):.4f}\n")
    
    df['PC1'] = X_pca[:, 0]
    df['PC2'] = X_pca[:, 1]
    df['PC3'] = X_pca[:, 2]
    df['PC4'] = X_pca[:, 3]
    
    # 3. Procrustes / Linear Projection to Bartlett
    # We will fit a linear model from the 4 PCs to the 2 (or 4) classical coordinates for Bartlett herbs
    bartlett_data = df.merge(gt[['marker_compound', 'Hot_Cold', 'Dry_Wet']], on='marker_compound', how='inner')
    
    X_calib = bartlett_data[['PC1', 'PC2', 'PC3', 'PC4']].values
    y_calib_hc = bartlett_data['Hot_Cold'].values
    y_calib_dw = bartlett_data['Dry_Wet'].values
    
    lr_hc = LinearRegression()
    lr_hc.fit(X_calib, y_calib_hc)
    
    lr_dw = LinearRegression()
    lr_dw.fit(X_calib, y_calib_dw)
    
    # Predict on all data
    df['pred_Hot_Cold'] = lr_hc.predict(df[['PC1', 'PC2', 'PC3', 'PC4']].values)
    df['pred_Dry_Wet'] = lr_dw.predict(df[['PC1', 'PC2', 'PC3', 'PC4']].values)
    
    print("--- Calibration (Bartlett) Performance ---")
    hc_corr = np.corrcoef(bartlett_data['Hot_Cold'], lr_hc.predict(X_calib))[0, 1]
    dw_corr = np.corrcoef(bartlett_data['Dry_Wet'], lr_dw.predict(X_calib))[0, 1]
    print(f"Hot/Cold R^2: {lr_hc.score(X_calib, y_calib_hc):.3f} (Correlation r={hc_corr:.3f})")
    print(f"Dry/Wet R^2: {lr_dw.score(X_calib, y_calib_dw):.3f} (Correlation r={dw_corr:.3f})\n")
    
    # Validate on TCM
    print("--- Validation (TCM) Performance ---")
    tcm_data = df.dropna(subset=['tcm_property_numeric'])
    
    # Check correlation between predicted Hot/Cold and TCM numeric property
    # NOTE: TCM numeric property scale: -2 (Cold) to +2 (Hot)
    # Our predicted Hot_Cold scale: Positive means Hot, Negative means Cold
    tcm_corr = np.corrcoef(tcm_data['tcm_property_numeric'], tcm_data['pred_Hot_Cold'])[0, 1]
    print(f"TCM Hot/Cold Correlation (r): {tcm_corr:.3f}")
    
    # Save the Phase 1 artifact
    df.to_csv("../exports/phase1_predictions.csv", index=False)
    print("\nPhase 1 complete. Projections saved to exports/phase1_predictions.csv")

if __name__ == '__main__':
    main()
