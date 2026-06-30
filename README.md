# Balance Engine

A computational, falsifiable research project investigating whether the classical four-quality system (Hot, Cold, Dry, Moist — from Galenic/Jābirian/Unani medicine) corresponds to real, measurable physicochemical properties of matter.

## Author's note

This project is conducted from an explicitly alchemical research stance. The working premise is that historical operative alchemy and humoral medicine encode real empirical regularities worth recovering with modern computational tools — not merely historical curiosities to be studied from a distance. The author is a practicing alchemist; this project treats that practice as a serious empirical tradition worth quantifying rigorously, in the spirit of early inductive science (Kepler working from Tycho's planetary data; Mendeleev working from measured atomic weights) rather than dismissing pre-modern observational traditions because their original theoretical framing has since been superseded.

The central claim under test is narrow and falsifiable:

> Can a latent-variable model derived from measurable physicochemical properties recover historically observed temperament classifications, and make accurate, testable predictions for substances never part of the historical corpus?

That claim can succeed, partially succeed, or fail outright — and each outcome is treated as scientifically informative.

## Methodology, in one paragraph

Hot/Cold/Dry/Moist are treated as **latent variables to be fit against real target data**, never as labels assigned by analogy. Every compound included in any dataset here passes a two-tier verification gate (formula-check + independent cross-source confirmation) before being used; compounds that fail are excluded, never patched. Historical classification systems (Culpeper, TCM, Bartlett's wet-lab measurements) are treated as **validation/prediction targets**, not training labels chosen to make the model agree with a preferred conclusion.

See `results/Balance_Engine_Project_Report.md` for the full account of what has been tested, what was rejected, what was reformulated into a sharper open question, and what remains deferred pending further data — including corrections made during the repository build (see the orthogonality-correlation correction in §4 as a worked example of the verification discipline catching a real error in the project's own prior output).

## Repository structure

```
data/
  ground_truth/       physically/textually measured data used to FIT the model
  compounds/          verified molecular descriptors (two-tier gate passed)
  prediction_targets/ held-out data (e.g. Culpeper) used ONLY to test predictions, never to fit
src/
  verify_compound.py      the two-tier verification gate
  fetch_pubchem.py        PubChem fetcher (requires real network access)
  build_dataset.py        combined fetch -> verify -> save pipeline
  orthogonality_test.py   standing diagnostic for any new Hot/Cold x Wet/Dry dataset
results/
  Balance_Engine_Project_Report.md   full project report and findings to date
exports/
  game/                   thin, downstream-only data export (e.g. for Flora Philosophica);
                          this directory is never a data SOURCE for the research itself
```

## Setup

```bash
pip install rdkit pubchempy mendeleev pymatgen pyreadr scikit-learn pandas matplotlib
```

PubChem-dependent scripts (`fetch_pubchem.py`, `build_dataset.py`) require unrestricted network access — they will not run in network-sandboxed environments.

## Current phase

See `results/Balance_Engine_Project_Report.md` §9 ("Active Roadmap") for the current phase structure (Learn → Validate → Emergence → Extend) and what's required before moving to the next phase. As of this commit: Phase 1 (fitting against Bartlett + growing Culpeper coverage) is in progress; the PCA dimensionality check (is "four independent qualities" even the right-shaped model?) has not yet been run and should happen before Phase 3.

## License

See `LICENSE`. Data sourced from third parties (TCMNP, Ramezany et al. 2013, PubChem) retains its own terms — check each source before redistribution; see citations in the project report.
