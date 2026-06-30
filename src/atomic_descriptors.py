"""
Atomic-level (Layer 0/1) descriptor extraction.

This is the part of the pipeline that is NOT specific to organic
molecular chemistry. Every descriptor here is defined per-ELEMENT and
works identically whether that element sits in an organic molecule, an
ionic mineral lattice, or pure metal -- because it never depends on a
bonded molecular graph (the thing RDKit needs and inorganics often don't
cleanly have). This is the actual answer to "what's shared by just about
everything," and it's the layer the organic-only pipeline (verify_compound.py,
PCA scripts) cannot reach.

Two levels are provided:
1. element_descriptors(symbol) -- raw, per-element Layer 0/1 quantities.
2. formula_descriptors(formula_dict) -- aggregates per-element values up to
   a COMPOUND by composition (e.g. {'Si': 1, 'O': 2} for quartz), using
   composition-weighted averages. This is deliberately a much cruder
   aggregation than RDKit's bond-graph-aware descriptors (it has no
   concept of bonding, geometry, or connectivity) -- that's the honest
   cost of a method that also works for things RDKit can't parse at all.
"""
from dataclasses import dataclass
from typing import Optional
from mendeleev import element as get_element


@dataclass
class ElementDescriptors:
    symbol: str
    atomic_number: int
    block: str                       # s, p, d, f -- shell type being filled
    group: Optional[int]
    period: int
    atomic_radius: Optional[float]    # pm
    covalent_radius: Optional[float]  # pm (Cordero)
    electronegativity_pauling: Optional[float]
    first_ionization_energy: Optional[float]   # eV
    electron_affinity: Optional[float]          # eV
    dipole_polarizability: Optional[float]      # atomic units
    density: Optional[float]                    # g/cm3
    melting_point: Optional[float]               # K (NOT in mendeleev's
                                                   # core table for all
                                                   # elements -- may be None)
    thermal_conductivity: Optional[float]
    common_oxidation_states: list


def element_descriptors(symbol: str) -> ElementDescriptors:
    """
    Fetch real Layer 0/1 quantities for a single element symbol.
    Raises ValueError via mendeleev if the symbol is invalid -- this is
    intentional, do not catch-and-default; an invalid symbol should fail
    loudly, the same verification philosophy as verify_compound.py.
    """
    e = get_element(symbol)
    ie = e.ionenergies.get(1) if e.ionenergies else None
    # Use direct attribute access -- more portable across mendeleev
    # installations than the phase_transitions relationship, which is not
    # consistently exposed depending on how the local data backend was
    # initialized (confirmed: this broke on at least one real machine).
    melting_point = getattr(e, "melting_point", None)

    return ElementDescriptors(
        symbol=e.symbol,
        atomic_number=e.atomic_number,
        block=e.block,
        group=e.group_id,
        period=e.period,
        atomic_radius=e.atomic_radius,
        covalent_radius=e.covalent_radius_cordero,
        electronegativity_pauling=e.en_pauling,
        first_ionization_energy=ie,
        electron_affinity=e.electron_affinity,
        dipole_polarizability=e.dipole_polarizability,
        density=e.density,
        melting_point=melting_point,
        thermal_conductivity=e.thermal_conductivity,
        common_oxidation_states=list(e.oxistates) if e.oxistates else [],
    )


def formula_descriptors(formula: dict[str, int]) -> dict:
    """
    formula: {element_symbol: count}, e.g. quartz SiO2 -> {'Si': 1, 'O': 2}
             or cinnamaldehyde C9H8O -> {'C': 9, 'H': 8, 'O': 1}

    Returns composition-weighted average of each numeric descriptor.
    EXPLICITLY CRUDER than RDKit's bond-aware descriptors -- this has no
    notion of bonding, connectivity, or geometry. Use this layer
    specifically because it is the one that survives the jump to
    inorganics; do not expect it to match RDKit's TPSA/LogP-based
    results on organics where both are available.
    """
    total_atoms = sum(formula.values())
    if total_atoms == 0:
        raise ValueError("Empty formula")

    per_element = {sym: element_descriptors(sym) for sym in formula}

    numeric_fields = [
        "atomic_radius", "covalent_radius", "electronegativity_pauling",
        "first_ionization_energy", "electron_affinity",
        "dipole_polarizability", "density", "thermal_conductivity",
    ]

    aggregated = {}
    for field in numeric_fields:
        weighted_sum = 0.0
        weight_used = 0
        for sym, count in formula.items():
            val = getattr(per_element[sym], field)
            if val is not None:
                weighted_sum += val * count
                weight_used += count
        aggregated[f"avg_{field}"] = (weighted_sum / weight_used) if weight_used > 0 else None
        aggregated[f"{field}_coverage"] = f"{weight_used}/{total_atoms} atoms had data"

    # Electronegativity SPREAD (max-min) is a real, separate, meaningful
    # quantity distinct from the average -- it's a rough proxy for how
    # ionic vs. covalent the compound's bonding character is likely to be,
    # which the average alone can't capture.
    ens = [getattr(per_element[sym], "electronegativity_pauling")
           for sym in formula if getattr(per_element[sym], "electronegativity_pauling") is not None]
    aggregated["electronegativity_spread"] = (max(ens) - min(ens)) if len(ens) >= 2 else 0.0

    aggregated["total_atoms"] = total_atoms
    aggregated["unique_elements"] = len(formula)
    return aggregated


if __name__ == "__main__":
    print("=== Single-element check: H vs O ===")
    for sym in ["H", "O", "Si", "Pb", "Hg"]:
        d = element_descriptors(sym)
        print(f"{sym}: EN={d.electronegativity_pauling}, IE1={d.first_ionization_energy} eV, "
              f"covalent_r={d.covalent_radius} pm, block={d.block}")

    print("\n=== Formula-level aggregation check ===")
    print("Quartz (SiO2) -- inorganic, would fail in the RDKit pipeline:")
    quartz = formula_descriptors({"Si": 1, "O": 2})
    for k, v in quartz.items():
        print(f"  {k}: {v}")

    print("\nCinnamaldehyde (C9H8O) -- organic, for comparison against RDKit's own descriptors:")
    cinnamaldehyde = formula_descriptors({"C": 9, "H": 8, "O": 1})
    for k, v in cinnamaldehyde.items():
        print(f"  {k}: {v}")
