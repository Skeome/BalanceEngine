"""
Standing diagnostic: for any dataset with both a Hot<->Cold axis and a
Wet<->Dry axis measured, check whether they're actually independent.

Run this on EVERY new ground-truth dataset before assuming the four
qualities behave as independent axes. On Bartlett's 14-herb data this
returned r=-0.95 (strong anti-correlation, NOT independence) -- a result
independently replicated by Ramezany et al. 2013 at much larger N
(Phi=-0.78 to -0.91). Do not assume orthogonality; test it every time.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler


def test_orthogonality(df: pd.DataFrame, hot_col: str, cold_col: str,
                        wet_col: str, dry_col: str,
                        feature_cols: list[str] | None = None) -> dict:
    """
    Returns dict with:
      raw_correlation: simple r between (Hot-Cold) and (Dry-Wet)
      residual_correlation: r between LOOCV residuals of each axis fit
                             separately against feature_cols (if given)
    """
    hc = df[hot_col] - df[cold_col]
    wd = df[dry_col] - df[wet_col]
    raw_corr = np.corrcoef(hc, wd)[0, 1]

    result = {"n": len(df), "raw_correlation": round(raw_corr, 3)}

    if feature_cols and len(df) > len(feature_cols):
        X = df[feature_cols].values.astype(float)
        loo = LeaveOneOut()

        def loocv_residuals(y):
            preds = np.zeros_like(y, dtype=float)
            for train_idx, test_idx in loo.split(X):
                scaler = StandardScaler()
                Xtr = scaler.fit_transform(X[train_idx])
                Xte = scaler.transform(X[test_idx])
                model = Ridge(alpha=5.0)
                model.fit(Xtr, y[train_idx])
                preds[test_idx] = model.predict(Xte)
            return y - preds

        hc_resid = loocv_residuals(hc.values)
        wd_resid = loocv_residuals(wd.values)
        result["residual_correlation"] = round(np.corrcoef(hc_resid, wd_resid)[0, 1], 3)
    else:
        result["residual_correlation"] = None
        result["note"] = "Not enough samples relative to features for residual test"

    if abs(raw_corr) > 0.7:
        result["interpretation"] = "STRONG correlation -- axes are NOT behaving independently in this data"
    elif abs(raw_corr) > 0.3:
        result["interpretation"] = "MODERATE correlation -- partial independence"
    else:
        result["interpretation"] = "WEAK correlation -- axes appear roughly independent in this data"

    return result


if __name__ == "__main__":
    df = pd.read_csv("data/ground_truth/bartlett_measured.csv")
    df = df[df[['hot', 'cold', 'wet', 'dry']].notna().all(axis=1)]  # keep all rows with valid H/C/W/D
    result = test_orthogonality(df, "hot", "cold", "wet", "dry")
    print("Bartlett ground truth orthogonality check:")
    for k, v in result.items():
        print(f"  {k}: {v}")
