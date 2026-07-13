import csv
from verify_compound import verify_batch

entries = {}
with open('../data/compounds/compound_catalog.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['marker_compound']
        smiles = row['smiles']
        formula = row['formula_verified']
        if smiles and formula:
            entries[name] = (smiles, formula)

passed, failed = verify_batch(entries)
print(f"Total passed: {len(passed)}")
print(f"Total failed: {len(failed)}")
for f in failed:
    print(f"FAILED: {f.name} - {f.reason}")
