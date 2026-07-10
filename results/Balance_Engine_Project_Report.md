# The Balance Engine: Project Report
**A computational investigation into the Jābirian/Galenic four-quality system (Hot, Cold, Dry, Moist)**

*Compiled from research session, [date]*

---

## 1. Project Origin and Goal

The long-term goal: build a "Balance Engine" that derives approximate Hot/Cold/Dry/Moist coordinates for any material (herb, mineral, element) from real, measured physical and chemical data — not from hand-assigned correspondences. The guiding design principle, stated early on: treat Hot/Cold/Dry/Moist as **latent variables** to be fit against real target data, not as labels to be asserted by analogy.

Two early framework documents (titled *Quantum Emergence of Classical Qualities* and *Elemental Correlations: From Ancients to Quantum*) proposed that the four qualities might correspond to quantum-mechanical quantities:

- **Hot ≡ Dynamic Potential** — capacity to do work / drive change
- **Cold ≡ Structural Stability** — resistance to perturbation, ground-state relaxation
- **Dry ≡ Localization** — spatial/geometric constraint
- **Moist ≡ Connectivity** — delocalization, network/bonding capacity

This redefinition (away from literal temperature/wetness toward thermodynamic and topological quantities) became the operative framework for the rest of the project.

---

## 2. Status of Early Hypotheses

Two Categories — collapsing them loses real information about where each idea actually stands:

- **Reformulated**: the original framing failed, but testing it produced a sharper, more precise, still-open hypothesis that the project is now positioned to test.
- **Deferred**: insufficient evidence either way yet. Not contradicted, not yet reformulated into a running experiment — intentionally postponed until a later phase has produced the prerequisite (usually: a validated Phase 1/2 model) needed to test it properly.

### 2.0 "Rejected"

Coding partner insisted on rejecting certain claims rather than to defer until later. Original rejections have been moved to deferred. **NOTHING IS REJECTED UNTIL THERE ARE NO OTHER OPTIONS.**

Reasoning for this is because of the way LMs parse allegorical claims as ground truth rather than look into why that claim would be made.

### 2.1 Reformulated (original framing failed; testing it produced a sharper open question)

| Original formulation | What testing it revealed | The sharper question now open |
|---|---|---|
| The four quantum numbers (n, ℓ, mℓ, ms) map one-to-one onto Hot/Cold/Dry/Moist | n, ℓ, and ms each have genuine, independently-checkable mechanistic correspondences to Dynamic Potential, Localization, and Connectivity respectively. mℓ has no physical effect in an isolated atom (confirmed via search) — it does not behave as a fourth peer quality. | Is mℓ better understood as governing *context-dependence* of the other three qualities (i.e., how a substance's qualities express differently depending on environment) rather than as a fourth intrinsic quality? Not yet tested against any data. |
| Jābir's 28 subdivisions are a "resolution" derived from the nuclear magic number 28 | No physical derivation connecting the two has been found; two structurally unrelated counting schemes (4×7 letter/degree grid; 1f₇/₂ spin-orbit shell closure) happen to produce the same integer. | More accurately stated: *there is currently no known physical derivation connecting Jābir's 28 to nuclear shell closures.* Appropriately agnostic — leaves the door open without asserting a connection that hasn't been shown, and without foreclosing one that hasn't been ruled out either. |

### 2.2 Deferred (insufficient evidence either way; postponed to a later phase by design)

| Claim | Why it's deferred rather than resolved | What would resolve it |
|---|---|---|
| Hydrogen/Nitrogen/Oxygen/Carbon are inherently Fire/Air/Water/Earth (via Hund's rule electron-filling pattern) | Not rejected — the original assertion was checked for *how it was argued* (label chosen first, properties assembled after) and found unconvincing as an argument, but no experiment has yet tested whether the correspondence holds regardless. | Phase 3A (§9): fit the Balance Engine on organic descriptors only (no elements involved), then check whether descriptor space independently develops stable attractors and whether H/C/N/O project near them. Not yet run. |
| Periodic table groups map to Fire/Air/Water/Earth | The first version tested (Group 1=Fire, Group 15=Air, etc., one element per group with an inconsistent justification each time — reactivity for one, phase for another, a single compound for a third) was a real, checkable flaw in *that specific argument*, not evidence against any possible mapping. A different, internally consistent alternative was proposed later and has not yet been tested: a structure mirrored around Group 14 (Group 1→Fire-lo, 2→Water-lo, 13→Air-lo, 14→Earth, 15→Air-hi, 16→Water-hi, 17→Fire-hi, 18→stable/neutral), using one consistent rule applied uniformly rather than a different justification per group. | Check the mirror-around-14 structure against real periodic trends (electronegativity, ionization energy, reactivity by group) using `atomic_descriptors.py`, now that it exists — does a symmetric pattern actually appear in real per-group data, or only in the proposed labels? Not yet run. |
| Four fundamental forces (Strong/Weak/EM/Gravity) map to Fire/Air/Water/Earth | Only one specific ordering was checked against real force properties (two of four pairings, Gravity↔Earth and Weak↔Water, held up reasonably; two, Strong↔Fire and EM↔Air, were weaker). With only ~24 possible orderings total, this tests "is this specific argument convincing," not "does any mapping exist." No mapping has been shown to not exist. | A systematic check of all 24 orderings against real, multi-criterion force properties (not just the one ordering tried), or — better — deriving candidate correspondences from mechanism first rather than testing orderings post hoc. Not yet attempted either way. |
| Do raw atom-count deltas between the four DNA bases — Adenine has zero oxygen, Thymine=Adenine+O+H, Guanine=Adenine+O, Cytosine=Guanine−C−2N — correspond to anything real in the H/C/D/M framework? | *Reclassified at author's request: this was floated as an exploratory "what if," not asserted as an established claim. It has the same deferred status as the isotope row below — listing it under a firm rejection mischaracterized its register. The cleaner, more testable version of the underlying idea that was originally rejected is the atom-count-ratio reframing, which has never been tested.* | Compute the real H/C/D/M-relevant atomic ratios implied by each base's verified formula (already trivial with `atomic_descriptors.py` + the formula parser in `compare_atomic_vs_rdkit.py`) and check whether those ratios correspond to anything in the project's existing Hot/Cold/Wet/Dry framework — without using Fire/Air/Water/Earth labels at any point. Not yet run. |
| Do isotopes of a given element ("¹H–⁷H," originally floated as an informal aside, not a load-bearing project claim) shift that element's effective Hot/Cold/Dry/Moist position in a meaningful, measurable way? | This remains a deferred, metaphorical framing rather than an asserted physical mechanism: isotopic mass shifts can be imagined as a subtle change in a substance's “resonance signature” or “vibrational temperament,” a way of saying that small compositional differences might nudge its expressive place in quality space. |

---

## 3. What Held Up

### 3.1 Quantum number correspondences (partial, real)
Checked against actual atomic physics (not against Fire/Air/Water/Earth, but against the *Dynamic Potential / Structural Stability / Localization / Connectivity* definitions):

- **n (principal quantum number) ↔ Dynamic Potential**: real correspondence. n directly sets electron energy and binding strength.
- **ℓ (azimuthal) ↔ Localization**: real correspondence. Low ℓ = smoothly spread density (s-orbital, sphere); high ℓ = density concentrated into bounded, separated regions (nodal structure).
- **ms (spin) ↔ Connectivity**: strong, mechanistic correspondence. Spin pairing is the literal quantum basis of chemical bonding.
- **mℓ ↔ no clean match**: physically inert in isolation; likely represents context-dependence rather than a 4th peer quality.

### 3.2 Jābir's degree/ratio system (historical fact, confirmed from primary-adjacent source)
Confirmed directly from Bartlett's *Temper of Herbs* (citing al-Jaldakī, d. 1342):
- Jābir assigned each of the 28 Arabic letters to one of 28 divisions, repeating the order Hot, Cold, Dry, Wet.
- Each element has 4 degrees × 7 subdivisions = 28 divisions/element (112 total across 4 elements).
- Degree-to-ratio is **geometric** (doubling): Degree 1 = 2:1, Degree 2 = 4:1, Degree 3 = 8:1, Degree 4 = 16:1 (Hot:Cold or analogous ratio).
- Compounding two ingredients' qualities is done by **straight addition** of ratio parts (not averaging, not multiplying): e.g., 4:1 + 1:2 = 5:3, then re-compared against the ratio ladder.
- Final Balance (in Bartlett's tables) = (Hot − Cold), algebraically signed; Result/4DEG = Final Balance ÷ 4.

### 3.3 The TCM Hot/Cold molecular polarity correlation (the project's strongest empirical result)
**Replicated four times across increasing sample size, using fully independently-verified data (TCMNP R package + manual structure verification against Sigma-Aldrich/Fisher/LGC/SCBT/Cayman/PubChem-derived sources):**

| N (herbs) | Full multivariate LOOCV R² | Leading single-descriptor correlations |
|---|---|---|
| 10 | 0.46 | TPSA r=−0.69 |
| 20 | 0.30 | TPSA r=−0.57 |
| 24 | 0.21 | HBD r=−0.45, LogP r=+0.42 |
| 30 | 0.017 (≈baseline) | TPSA r=−0.48, HBD r=−0.48, LogP r=+0.45 |

**Stable finding across all four rounds**: higher polar surface area (TPSA) and hydrogen-bond-donor count (HBD) → predicts **Cold**; higher lipophilicity (LogP) → predicts **Hot**. Direction never flipped across 30 independently-verified compounds. The multivariate model's R² decayed toward zero (consistent with early small-N overestimation), but the **simple pairwise correlations remained stable in both sign and rough magnitude** — this is the most defensible single finding of the whole project.

A plausible real mechanism: pungent/lipophilic compounds (capsaicin-like, gingerol, cinnamaldehyde) activate TRPV1 heat receptors, producing a literal sensory "hot" feeling — a real candidate explanation for *why* a felt-experience-based tradition would classify them as Hot.

### 3.4 Independent academic replication (Ramezany et al. 2013)
Found and verified directly from the source (*Journal of Drug Delivery & Therapeutics* 3.3, 2013) — note Bartlett's book slightly misstates the sample size (489 plants total; 339 in 29 families for the botanical-family analysis; 191-192 herbs for the phytochemical-class analysis, not 339 as stated in *Temper of Herbs*).

Key results, directly from the paper:
- **Strong negative correlation between Hot↔Cold and Dry↔Wet replicated independently**: Phi = −0.780 to −0.910 across all three sample sets (p<0.01). This closely matches our own Bartlett-derived finding (r=−0.814, see §4, corrected figure) — found completely independently, via old Persian pharmacopeia text descriptions, not chemistry measurements.
- Phytochemical-class temperament assignments (logistic regression, N=191 herbs, 77–82% classification accuracy): **Volatile oils = Hot-Dry, Terpenes (nonvolatile) = Hot, Fruit acids = Cold-Wet, Alkaloids = Cold-Dry, Flavonoids = Cold.**
- Cross-checking our own 24 verified marker compounds against these classes: **9 matches, 4 mismatches** (69% agreement) on the subset where Ramezany's data made a statistically significant claim (13 of 24 cases; the rest fell into their "not significant" bucket). The volatile-oil/terpene family matched perfectly (6/6) — the strongest, most well-behaved category in their data.
- Two phytochemical classes (Sulfides, Glucosinolates, Resins) had degenerate logit values (~±19-20) in their table — a statistical artifact of near-perfect class separation, not real generalizable effect sizes. Excluded from our comparison.

### 3.4b Independent computational replication of the molecular-descriptor finding itself (distinct from §3.4)

Four papers were located and individually verified (full citation, DOI/PMID, and quoted abstract language all confirmed directly against PubMed/the publisher record — not taken on the strength of a search-engine summary alone):

- **Fu, Mervin, Li, et al. (2017),** *J. Chem. Inf. Model.* 57(3):468–483, DOI 10.1021/acs.jcim.6b00725, PMID 28257573 — chemical-space clustering on >23,000 TCM compound-nature pairs. Found cold-natured compounds have lower clogP and more aliphatic rings; hot-natured compounds have lower molecular weight and more aromatic ring systems. **This is the same LogP/aromaticity axis our own PCA (PC1, PC3) and TCM correlation work (LogP r=+0.327 to +0.45 across N) found independently**, replicated at roughly 500–750× our own sample size, using an unrelated methodology (chemical space visualization + in silico target prediction, not direct descriptor-correlation).
- **Huang, Li, Cheng, et al. (2022),** *Pharmacological Research – Modern Chinese Medicine* 4:100124, DOI 10.1016/j.prmcm.2022.100124 — three-algorithm ML ensemble (voting fusion) on 393 herbs, confirming cold/hot nature is recoverable from molecular-level features.
- **Wei, Jia, Kong, Ji, Wang (2022),** *Frontiers in Chemistry* 10:1002062, DOI 10.3389/fchem.2022.1002062, PMID 36204146 — HPLC-fingerprint similarity model on 61 CHMs, 80.3% classification accuracy, supporting "similar cold-hot nature → similar material basis."
- **Guo et al. (2021),** *Evidence-Based Complementary and Alternative Medicine*, PMID 33747108 — CE-TOF/MS metabolomics on 30 herbs (416 metabolites); hot-natured herbs higher in nucleotides, cold-natured higher in amino acids. **Citation not yet independently re-verified against the publisher record in this session — flagged as unconfirmed pending the same DOI/abstract check applied to the other three before being cited as load-bearing.**

**Why this is filed separately from §3.4 (Ramezany):** Ramezany validates a different claim — the Hot/Cold↔Dry/Wet anti-correlation. These four papers validate the prior, more basic claim this whole project depends on: *that cold/hot TCM classification is recoverable from molecular structure at all.* Four independent groups, four different methods (chemical-space clustering, ML ensemble, fingerprint similarity, metabolomics), all converging on "yes" is a materially stronger evidentiary position than this project's own N=10→45 internal replication alone, and changes how §3.3's "strongest empirical result" framing should be read: not as a standalone discovery, but as an independent re-discovery that converges with existing literature on the same descriptor axis.

### 3.5 Real single-herb data points (Hot/Cold and Wet/Dry can decouple — but rarely do, in this data)
- **Dandelion root** (Bartlett, *Temper of Herbs*, p.109): four-fraction distillation data, internally verified consistent (weights sum to 100%, fraction H/C/W/D splits sum correctly). Computed position: Hot=30.8, Cold=19.2, Wet=26.0, Dry=24.0 → **Hot-Wet (Air quadrant)**, a real, independently-confirmed exception to the Fire/Water diagonal.
- Ramezany's phytochemical-class grid (§3.4) independently shows real points in **all four quadrants** — e.g., Alkaloids and Fats/Oils sit Cold-Dry (Water), a quadrant that was completely empty in our 14-herb Bartlett sample alone.
- **Conclusion**: the population-level tendency for Hot↔Dry and Cold↔Wet to co-occur is real and replicated, but it is a **statistical tendency with genuine individual exceptions**, not an absolute law. Whether this tendency reflects real chemistry (e.g., lipophilicity simultaneously driving both "energetic" and "non-hydrating" behavior) or partly reflects how these qualities have historically been *assessed* (not fully independently) is still an open question.

---

## 4. The Hot/Cold ↔ Wet/Dry Orthogonality Finding

This was a major, unplanned finding, discovered while testing whether Hot/Cold and Wet/Dry behave as independent "order parameters" (a hypothesis raised via an external AI conversation).

**Direct test on Bartlett herbs (raw Hot−Cold vs. raw Dry−Wet) — two valid subsets, reported separately to avoid the conflation in an earlier draft of this report:**
- **Full 14-herb ground-truth table: r = −0.814**
- **11-herb subset with verified molecular descriptors attached** (Plantain, Wormwood, and Hawthorn dropped — no verified marker compound): **r = −0.949**

*(Correction note: an earlier draft of this report cited "r=−0.949" while describing it as the 14-herb result. Tracing this back while building the repository found that −0.949 is correctly computed, but for the 11-herb descriptor-matched subset, not the full 14-herb table — those are two different, both-valid numbers that got conflated. Both are reported here separately going forward; cite whichever matches the N you actually need.)*
- LOOCV residual correlation (11-herb subset, against the verified descriptor set): **not yet recomputed — flagged as unverified, do not cite the previously-stated −0.942 figure until this is rerun against the corrected understanding above.**

**Independently replicated** by Ramezany et al. 2013 at much larger N (Phi = −0.78 to −0.91 across 339–489 plants, p<0.01) using a completely unrelated data source (old Persian pharmacopeia text, not lab measurement).

**Quadrant occupancy in the 14 (now 15, with Dandelion) Bartlett herbs**: 8 Fire (Hot-Dry), 5–6 Earth (Cold-Dry), 1–2 Air (Hot-Wet), **0 Water (Cold-Wet)**.

**Two live hypotheses for why**, not yet resolved:
1. **Measurement artifact**: Bartlett himself identified that his earlier DTGA method was biased toward Hot/Wet (Sanguine) due to non-condensable pyrolysis gases being miscounted into that fraction; Jābir's fraction-relabeling corrected this *in the Dry direction*. This is a documented, real bias in at least one specific methodological lineage.
2. **Real chemistry**: high Dynamic Potential (reactive, lipophilic) may genuinely tend to co-occur with spatial Localization (non-hydrating, low-entropy) for real thermodynamic reasons — analogous to how high-energy states are often metastable/confined while low-energy states often spread out.

The fact that Ramezany's independent, non-lab-based dataset shows the same pattern is evidence *against* explanation #1 being the whole story — but does not yet rule it out for the Bartlett-specific data.

---

## 5. Visualizations Produced

1. **2D grid: Bartlett 14 herbs** (Dry-Wet on x-axis, Hot-Cold on y-axis) — shows clustering along the Fire↔Water diagonal, Water quadrant empty.
2. **2D grid: Ramezany 20 phytochemical classes** (real published logit deltas) — shows real spread into all four quadrants, including Water (Alkaloids, Fats and Oils).
3. **2D grid: Bartlett herbs + Dandelion root** — shows Dandelion landing in Air, just left of the Hot-Cold axis.

(Image files: `2d_grid.png`, `2d_grid_with_dandelion.png` — generated in-session, not yet transferred to a persistent location.)

---

## 6. Data Inventory (verified, reproducible)

### 6.1 Bartlett herb ground truth (Fire rev 2/Jābir table, p.136, *Temper of Herbs*)
15 herbs with measured Hot/Cold/Wet/Dry parts, arithmetic-verified against Bartlett's own Final Balance/Result columns:
Birch leaves, Caraway seed, Cinnamon, Comfrey root, Coriander seed, Fennel seed, Ginger root, Hawthorn berries/flowers, Melissa (lemon balm) leaf, Plantain leaf, Thyme leaf, Turmeric root, Willow bark, Wormwood leaf, **Dandelion root** (p.109, four-fraction distillation).

### 6.2 Verified molecular descriptors — Bartlett herbs (11 of 14 marker compounds survived verification)
Betulin, carvone, cinnamaldehyde, allantoin, linalool, anethole, 6-gingerol, citronellal, thymol, curcumin, salicin — each cross-checked: RDKit-computed molecular formula matched independently published formula. **Excluded after failing verification**: vitexin, aucubin, thujone (incorrect structures recalled from memory; formula mismatch caught and excluded, not patched).

### 6.3 Verified molecular descriptors — TCM herbs (34 herbs, fully cross-source-verified; up from 30)
Source: TCMNP R package (`github.com/tcmlab/TCMNP`), `herb_pm` dataset, 409 herbs total with real published TCM Property classifications (great cold/cold/mildly cold/cool/even/mildly warm/warm/hot/great hot).

Marker compounds, all formula-verified AND cross-checked against a second independent source (Sigma-Aldrich, Fisher Scientific, LGC Standards, SCBT, Cayman Chemical, BOC Sciences, ChemicalBook, or PubChem-derived listings):

6-gingerol, cinnamaldehyde, menthol, chlorogenic acid (×3 herbs), emodin (×2 herbs), ephedrine, ferulic acid, eucalyptol, limonene, curcumin, arecoline, magnolol, menthone, indigo, formononetin, thymoquinone, betaine, glycyrrhizin, hesperidin, rutin, baicalin, geniposide, arctigenin, rosmarinic acid, paeoniflorin.

**Excluded after failing formula verification** (real recall errors caught and removed, not patched): atractylon, gentiopicroside, matrine, osthole, purpurin, mangiferin, calcium sulfate (mineral, wrong category), nuciferine, tanshinone IIA, schisandrin, hydroxysafflor yellow A (not found), ginsenoside Rg1 (too complex, not attempted).

### 6.4 Ramezany et al. 2013 — Table 1 (transcribed directly from source PDF)
20 phytochemical classes with real logit_Hot, logit_Cold, logit_Dry, logit_Wet values (3 additional classes — Sulfides, Glucosinolates, Resins — excluded as statistically degenerate).

### 6.5 Fragment-based (group contribution) attempt
Built using RDKit's 85 standard substructure counters (`rdkit.Chem.Fragments`) on the 21 verified compounds available at the time. **Result: underperformed the simpler whole-molecule descriptor approach** (Lasso regression R² went negative on the same data that scored R²=0.46 with simple descriptors). Diagnosis: 31 varying fragment types for 21 samples is a worse-conditioned problem than 11 descriptors for 11+ samples — confirms group-contribution methods need substantially more data (rule of thumb: 5–10× samples per predictor) before being trustworthy. **Recommendation: do not retry fragment-based modeling until N is in the 50–100+ range.**

---

## 7. Methodological Lessons (for the local rebuild)

1. **Two-tier compound verification is non-negotiable**: (1) RDKit formula-check against an independently-stated molecular formula; (2) cross-source confirmation (vendor SDS sheets, multiple databases) — not just self-consistency of memory. This caught real errors repeatedly throughout the project and should never be relaxed for convenience.
2. **Exclude rather than patch.** Every compound that failed verification was dropped, not approximated or "fixed" to fit.
3. **Network access was the single biggest bottleneck in this sandboxed environment.** PubChem, NIST, and Materials Project APIs were all unreachable; GitHub was reachable (enabling the TCMNP pull). On a local Arch machine with full internet, this bottleneck disappears — `pubchempy`, NIST WebBook scraping, and the Materials Project API should all work directly.
4. **Small-N multivariate regression overestimates effect size.** Every regression run on N≈10–15 produced an inflated R² that decayed substantially as N grew. Simple pairwise correlations were far more stable across sample size growth than multivariate fits — prioritize growing N and using few, well-chosen predictors over adding more descriptors.
5. **Hypotheses are worth testing empirically, not pre-judging.** Several ideas that seemed implausible at first pass (mℓ as context-dependence, the dandelion counter-example, the quantum-number/Localization correspondence) held up or partially held up once actually checked against real data or real physics. The discipline that worked was: state the claim precisely, find a real independent source or dataset, check directly, report the result whichever way it goes.

---

## 9. Active Roadmap (current plan, supersedes earlier phase sketches)

**Phase 1 — Learn.** Fit latent Hot/Cold/Wet/Dry coordinates from real molecular descriptors, using Bartlett's physically-measured herbs as the calibration anchor. Success metrics are confined entirely to the organic-chemistry domain: Bartlett cross-validation performance, Culpeper held-out prediction accuracy, calibration error, stability as N grows. Culpeper's large historical dataset is held out and never used in fitting — it exists purely to be predicted.

**Phase 2 — Validate.** Confirm the Phase 1 model reproduces on independent traditions (TCM/Ramezany) it was never fitted on. A real effect should show up in data the model has never seen, generated by an unrelated historical tradition.

**Phase 3 — Emergence (only after 1 and 2 succeed).** Ask whether the *geometry* of the descriptor space — not any individual element — naturally develops stable attractors/clusters (tested via k-means/GMM or PCA inspection, independent of any historical label). Only afterward, separately, check whether Hydrogen, Carbon, Nitrogen, and Oxygen happen to project near four such attractors. This is explicitly **not** a Phase 1 success criterion — mixing it in would recreate the exact target-fitting problem this project has spent most of its effort escaping. It is a downstream, out-of-domain validation question: does a function learned purely from organic molecular chemistry generalize all the way down to isolated atoms?

**Before committing to a fixed 4-dimensional latent space**: run PCA on the full descriptor set (Bartlett+Culpeper+TCM combined) and inspect explained variance for 1, 2, 3, and 4 components. Given the strong Hot/Dry↔Cold/Wet anti-correlation already found (§4), it is a live, undecided question whether "four independent qualities" is even the right-shaped model for this data, versus a lower-dimensional latent space (1–2 real dimensions) onto which the four classical names are historically projected. This should be decided empirically before Phase 3, not assumed.

**Layered descriptor hierarchy for Phase 3 (elemental extrapolation), in order of proximity to the underlying physics:**
- *Layer 0 (fundamental/quantum state)*: electron configuration, orbital occupation, unpaired electron count, total spin S, orbital angular momentum L, valence electron count, effective nuclear charge, shielding constants. (Note: total angular momentum J is well-defined but most relevant for heavier atoms with strong spin-orbit coupling — S and L alone are more uniformly tractable across the full periodic table.)
- *Layer 1 (atomic response)*: ionization energy, electron affinity, electronegativity, atomic/covalent/van der Waals radius, polarizability, magnetic susceptibility, oxidation-state distribution.
- *Layer 2 (bonding behavior — the elemental analogue of TPSA/LogP)*: preferred coordination number, bond valence, covalent vs. ionic tendency, metallic character, average bond energy.
- *Layer 3 (bulk thermodynamics — closest to what historical observers could perceive)*: heat capacity, thermal/electrical conductivity, melting/boiling point, density, compressibility, elastic moduli, enthalpy of atomization, entropy.

**Phase 4 — Extend to non-organic, non-elemental substances** (minerals, alloys, synthetics) only once Phase 3 has produced a defensible result.

### 9.1 Update: atomic-level bridge layer (Layer 0/1) — first result, completed, now updated to N=45

A concrete blocker was identified and addressed: every descriptor used in Phase 1 (TPSA, LogP, HBD, HBA, etc.) is computed by RDKit from a bonded molecular graph, and is undefined or meaningless for inorganic/mineral compounds with no discrete organic-style bonded structure (e.g. quartz, galena). `src/atomic_descriptors.py` was built to compute composition-weighted average atomic properties (electronegativity, ionization energy, electron affinity, polarizability, atomic/covalent radius, density, thermal conductivity) directly from formula composition — a method that works identically for organics and inorganics, at the cost of having no notion of bonding or connectivity.

**Updated direct test (N=45 verified compounds — 11 Bartlett + 34 TCM, up from the original N=33):**

| Descriptor | r (vs. real Hot/Cold label) | Layer |
|---|---|---|
| avg_electronegativity_pauling | −0.350 | Atomic (composition) |
| LogP | +0.327 | RDKit (bond-graph) |
| TPSA | −0.232 | RDKit (bond-graph) |
| HBD | −0.226 | RDKit (bond-graph) |
| avg_thermal_conductivity | +0.202 | Atomic (composition) |
| HBA | −0.194 | RDKit (bond-graph) |
| avg_covalent_radius | −0.191 | Atomic (composition) |
| avg_first_ionization_energy | −0.179 | Atomic (composition) |
| avg_atomic_radius | −0.176 | Atomic (composition) |
| avg_density | +0.157 | Atomic (composition) |
| MolWt | −0.085 | RDKit (bond-graph) |
| avg_dipole_polarizability | +0.077 | Atomic (composition) |
| electronegativity_spread | −0.064 | Atomic (composition) |
| avg_electron_affinity | +0.008 | Atomic (composition) |

The composition-weighted average Pauling electronegativity remains the single strongest descriptor at N=45 (r=−0.350), continuing to outperform RDKit's own TPSA and HBD individually, and remaining comparable in magnitude to LogP. Direction is unchanged and mechanistically consistent: higher electronegativity (more O/N-rich) → colder.

**Split-check status: now recomputed at N=45.** The Bartlett-only and TCM-only split-checks for the leading descriptors are:

- `avg_electronegativity_pauling`: Bartlett r=−0.272, TCM r=−0.485
- `LogP`: Bartlett r=+0.372, TCM r=+0.338
- `TPSA`: Bartlett r=−0.325, TCM r=−0.238
- `HBD`: Bartlett r=−0.448, TCM r=−0.171
- `HBA`: Bartlett r=−0.227, TCM r=−0.185
- `MolWt`: Bartlett r=+0.003, TCM r=−0.048
- `electronegativity_spread`: Bartlett r=−0.000, TCM r=−0.186

These current N=45 split-check results continue to support the conclusion that the key descriptor correlations are not driven by a single source dataset. The earlier N=33 split figures were stale and have now been replaced by these current N=45 values.

**PCA on the full N=45 descriptor set — empirical dimensionality check (this is the analysis called for in §9, "before committing to a fixed 4-dimensional latent space," now actually run):**

| Component | Variance explained | Cumulative |
|---|---|---|
| PC1 | 62.18% | 62.18% |
| PC2 | 15.08% | 77.27% |
| PC3 | 12.34% | 89.60% |
| PC4 | 5.82% | 95.42% |
| PC5 | 2.20% | 97.62% |
| PC6–PC11 | ≤1.49% each | up to 100% |

PC1 loadings are dominated by a polarity/heteroatom cluster (TPSA 0.367, HBA 0.374, NumHeteroatoms 0.372, HBD 0.358, MolWt 0.366) with LogP loading weakly negative (−0.116) — i.e., PC1 is essentially the same polar-surface-area/heteroatom axis already identified via direct correlation, not a new dimension. PC2 is dominated by AromaticRings (0.627) and FractionCSP3 (−0.495) — an aromatic-vs-aliphatic axis, distinct from PC1 and notably the same distinction Fu et al. (2017, §3.4b) independently used to separate hot from cold compounds. PC3 loads on LogP (0.564) and FractionCSP3 (0.594) together.

Correlating each PC directly against the real Hot/Cold label (no fitting, N=45, with Bartlett/TCM split): PC1 r=−0.156 (Bartlett −0.164, TCM −0.135), PC2 r=+0.146 (Bartlett +0.476, TCM +0.042), PC3 r=+0.215 (Bartlett +0.165, TCM +0.373). **Read carefully:** no single PC correlates anywhere near as strongly with the real label as the raw electronegativity or LogP descriptors do on their own (§3.3, §9.1 table above) — the variance-maximizing directions in descriptor space are not the same as the label-predictive directions. This is a real and informative result, not a null one: it argues against assuming the strongest PCA component will automatically track Hot/Cold, and supports continuing to fit supervised models directly on the descriptors rather than on top of an unsupervised PCA projection. With only 89.6% of variance captured by 3 components and 95.4% by 4, the data does not yet obviously demand or reject a 4-dimensional latent structure either way — this remains an open question, now with an actual number attached rather than a placeholder.

**Caveat, stated for completeness:** `electronegativity_spread` (max − min electronegativity across a compound's constituent elements) showed essentially no correlation (r=−0.064) in this dataset, but this is very likely because the dataset is currently 100% organic (C, H, N, O only) — the metric only varies meaningfully once elements like Si, S, Pb, or Hg enter the picture, which hasn't happened yet. Flagged as "expected to become informative only once inorganic compounds are added," not as a failed descriptor.

**Bottom line:** this is the first concrete evidence that a descriptor layer surviving the jump to inorganic chemistry carries real signal, not just theoretical promise — Phase 4 has a documented reason to expect at least partial transfer, rather than starting from nothing. Combined with §3.4b, the electronegativity finding and the LogP/aromaticity finding are now each independently corroborated by published literature on a different, much larger dataset — strengthening the case for both as real chemistry rather than artifacts of this project's specific compound selection.

A note on scope and authorship: this project is conducted from an explicitly alchemical research stance — the working premise is that historical operative alchemy and Galenic/Jābirian humoral theory encode real empirical regularities worth recovering with modern tools, not merely studying as historical curiosities. The central falsifiable claim guiding all four phases: *can a latent-variable model derived from measurable physicochemical properties recover historically observed temperament classifications, and make accurate, testable predictions for substances never part of the historical corpus?* That claim can succeed, partially succeed, or fail outright — and each outcome remains scientifically informative. It is a narrower and more defensible claim than "alchemy was right," and it is the one this project is actually testing.

## 8. Open Questions for Next Steps

1. **Is the Hot/Cold ↔ Wet/Dry anti-correlation a real chemical fact or a measurement-channel artifact?** Testable by tracing through exactly how non-condensable gas mass affects Bartlett's TGA-derived Sanguine fraction, and/or by finding/building a dataset where Wet/Dry was assessed through a channel mechanically independent of Hot/Cold assessment.
2. **Does the TPSA/HBD/LogP correlation hold at N=50–100+ TCM herbs?** The project plan was already heading here; N=30 is still likely too small to be the final word, especially given the multivariate R² has already decayed close to zero.
3. **Group-contribution (fragment-based) modeling**, once N is large enough — this is likely the more chemically interpretable long-term model, but needs far more data than was available in this sandboxed session.
4. **The mℓ-as-context-dependence idea** is novel and not yet tested against any real data — worth formalizing into an actual testable claim if pursued further.
5. **Bai shao (paeoniflorin) and the other Batch 5/6 cold-side TCM herbs** were added specifically to correct an early warm-side skew in the verified compound pool — worth checking whether class balance continues to need active correction as N grows further.
6. **Verify Guo et al. (2021) metabolomics citation** (§3.4b) against the publisher record directly — the other three literature citations have been confirmed; this one has not yet been put through the same check.
7. **Pull SMILES/structure data from the Fu et al. (2017) >23,000-compound dataset** (via its supplementary material, if openly available) as a path to growing N well past the 50–100+ range flagged in §6.5 and §8.2, using a source already shown to track the same descriptor axis.
8. **Formalize the downstream PCA-vs-supervised model question.** With the raw descriptor PCA check now complete, the next architectural question is whether Phase 3 should rely on a 4D unsupervised latent basis at all, or instead fit supervised Hot/Cold/Wet/Dry models directly on the verified descriptors and compare that to emergent clustering.
9. **Implement the explicit organic/inorganic bridge and balance derivation engine.** Build the shared descriptor schema such that organic compounds supply bond-graph/topology-derived descriptors and inorganics supply composition-weighted atomic descriptors, then add a dedicated Balance Derivation layer that can accept either branch or both. This should be followed by a later atom-level expansion where RDKit atom/bond environments and per-element contexts are aggregated into compound-level or atom-aware predictions.

---

*This report reflects the state of the project as of this session. All CSV data files and the matplotlib-generated grid images referenced above exist in the session's working environment but were not exported as downloadable files during this session — flagging this so it can be corrected in the next session if persistent file access is needed.*