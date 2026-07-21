# Balance Engine — Filepath & Dependency Update Report

This report outlines the current repository files and identifies all hardcoded filepaths, obsolete CSV references, and structural schemas that need to be updated in order to unify your pipeline around [compound-db.csv](file:///home/skeome/Development/Balance_Engine/data/compounds/compound-db.csv).

---

## 1. Directory Structure Status

Currently, the directories contain:
* **`data/compounds/`**: Contains the active `compound-db.csv`, but still retains the old files (`bartlett_verified.csv`, `tcm_verified.csv`, `batch1.csv`, `batch2.csv`, `compound_catalog.csv`, `combined_rdkit_and_atomic.csv`) which you plan to delete after migrating herb references.
* **`src/`**: Contains the scripts that implement descriptor calculation and analytics.
* **`scripts/`**: Contains Lovell PDF/OCR parser utilities (clean of direct CSV references).

---

## 2. Code Filepath References to Update

Below is the list of scripts inside `src/` containing hardcoded references to obsolete CSV files. To switch entirely to `compound-db.csv`, these files need to be modified.

### [src/check_pc_separation.py](file:///home/skeome/Development/Balance_Engine/src/check_pc_separation.py)
* **Current References**:
  * Line 24: `pd.read_csv("data/compounds/bartlett_verified.csv")`
  * Line 25: `pd.read_csv("data/compounds/tcm_verified.csv")`
* **What needs to update**: Must be combined to read a single slice of `data/compounds/compound-db.csv` filtered by source (e.g. where `sourcesVerified` contains 'LOTUS' or specific herb references) or run on the entire `compound-db.csv` table.

### [src/compare_atomic_vs_rdkit.py](file:///home/skeome/Development/Balance_Engine/src/compare_atomic_vs_rdkit.py)
* **Current References**:
  * Line 32: `pd.read_csv("data/compounds/bartlett_verified.csv")`
  * Line 33: `pd.read_csv("data/compounds/tcm_verified.csv")`
  * Line 91: `merged.to_csv("data/compounds/combined_rdkit_and_atomic.csv", index=False)`
* **What needs to update**: Remove the merge path entirely. The calculated RDKit and atomic descriptors are already columns inside `compound-db.csv` (or should be populated directly back into it).

### [src/full_analysis.py](file:///home/skeome/Development/Balance_Engine/src/full_analysis.py)
* **Current References**:
  * Line 84: `pd.read_csv(data_dir / "bartlett_verified.csv")`
  * Line 103: `pd.read_csv(data_dir / "tcm_verified.csv")`
  * Line 118: `pd.read_csv(data_dir / "batch1.csv")`
  * Line 133: `pd.read_csv(data_dir / "batch2.csv")`
* **What needs to update**: Replace these four loads with a single load of `data/compounds/compound-db.csv`. Update the data frame extraction to map old column names to the new schema (see Section 3 below).

### [src/pca_full_dataset.py](file:///home/skeome/Development/Balance_Engine/src/pca_full_dataset.py)
* **Current References**:
  * Line 24: `pd.read_csv("data/compounds/bartlett_verified.csv")`
  * Line 25: `pd.read_csv("data/compounds/tcm_verified.csv")`
* **What needs to update**: Repoint to load `data/compounds/compound-db.csv`.

### [src/topology_pipeline.py](file:///home/skeome/Development/Balance_Engine/src/topology_pipeline.py)
* **Current References**:
  * Line 16: `Path("data/compounds/bartlett_verified.csv")`
  * Line 17: `Path("data/compounds/tcm_verified.csv")`
  * Line 66: `Path("data/compounds/verified_topology_descriptors.csv")`
* **What needs to update**: Repoint input paths to `data/compounds/compound-db.csv`. The topology output should either write directly back into the corresponding rows of `compound-db.csv` or output a temporary join file.

### [src/build_dataset.py](file:///home/skeome/Development/Balance_Engine/src/build_dataset.py)
* **Current References**:
  * Line 16: `out_path="data/compounds/new_batch.csv"` (in example/docstring)
* **What needs to update**: Safe to keep, but any script calling `build_dataset` should be directed to append to or update `data/compounds/compound-db.csv`.

---

## 3. Schema & Column Name Remapping

When updating these scripts, the following column name transformations must be applied:

| Old Column Name | New Column Name in `compound-db.csv` |
| :--- | :--- |
| `marker_compound` | `compoundName` |
| `herb` / `source_name` / `herb_pinyin` | `Base Plant` |
| `smiles` | `canonicalSmiles` |
| `formula_verified` | `molecularFormula` |
| `verification_strength` | `verificationStatus` |
| `MolWt` | `MolWT` |
| `NumHeteroatoms` | `NumHeteroAtoms` |
| `source_files` | `sourcesVerified` |

The remaining physics/physicochemical property columns (`LogP`, `TPSA`, `HBD`, `HBA`, `RotatableBonds`, `AromaticRings`, `FractionCSP3`, `MolarRefractivity`, `RingCount`) match exactly in casing.
