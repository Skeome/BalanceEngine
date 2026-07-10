"""
Bonded-graph topology descriptor extraction for organic compounds.
This layer is distinct from the atomic composition layer in atomic_descriptors.py.
It requires an RDKit-parsable organic SMILES and returns descriptors that
depend on molecular connectivity, aromaticity, and graph topology.
"""
from dataclasses import dataclass
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors


@dataclass
class TopologyDescriptors:
    smiles: str
    canonical_smiles: str
    formula: str
    descriptors: dict


CORE_TOPOLOGY_FUNCS = {
    "MolWt": Descriptors.MolWt,
    "LogP": Descriptors.MolLogP,
    "TPSA": Descriptors.TPSA,
    "HBD": Descriptors.NumHDonors,
    "HBA": Descriptors.NumHAcceptors,
    "RotatableBonds": Descriptors.NumRotatableBonds,
    "FractionCSP3": Descriptors.FractionCSP3,
    "NumHeteroatoms": Descriptors.NumHeteroatoms,
}

RING_TOPOLOGY_FUNCS = {
    "AromaticRings": rdMolDescriptors.CalcNumAromaticRings,
    "RingCount": rdMolDescriptors.CalcNumRings,
    "NumAliphaticRings": rdMolDescriptors.CalcNumAliphaticRings,
    "NumSaturatedRings": rdMolDescriptors.CalcNumSaturatedRings,
    "NumHeterocycles": rdMolDescriptors.CalcNumHeterocycles,
}


def compute_topology_descriptors(smiles: str) -> TopologyDescriptors:
    """Compute topology descriptors from an organic SMILES string."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES_PARSE_FAILED: {smiles}")

    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    mol_h = Chem.AddHs(mol)
    formula = rdMolDescriptors.CalcMolFormula(mol_h)

    descriptors = {}
    for name, func in CORE_TOPOLOGY_FUNCS.items():
        descriptors[name] = float(round(func(mol), 6))
    for name, func in RING_TOPOLOGY_FUNCS.items():
        descriptors[name] = int(func(mol))

    return TopologyDescriptors(
        smiles=smiles,
        canonical_smiles=canonical,
        formula=formula,
        descriptors=descriptors,
    )


def topology_descriptor_names() -> list[str]:
    return list(CORE_TOPOLOGY_FUNCS) + list(RING_TOPOLOGY_FUNCS)


if __name__ == '__main__':
    sample_smiles = 'C1=CC=CC=C1'  # benzene
    print('Sample topology descriptors for benzene:')
    topo = compute_topology_descriptors(sample_smiles)
    print(f'  SMILES: {topo.smiles}')
    print(f'  Canonical SMILES: {topo.canonical_smiles}')
    print(f'  Formula: {topo.formula}')
    for k, v in topo.descriptors.items():
        print(f'    {k}: {v}')
