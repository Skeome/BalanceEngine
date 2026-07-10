import csv
from pathlib import Path

CLASS_TEMPERAMENT_MAP = {
    'Alkaloids': 'Cold-Dry',
    'Flavonoids': 'Cold-NS',
    'Volatile oils': 'Hot-Dry',
    'Terpenes (nonvolatile)': 'Hot-NS',
    'Fruit acids': 'Cold-Wet',
    'Phenolic acids': 'NS-Dry',
    'Saponins': 'Hot-Wet',
    'Tannins': 'Cold-NS',
    'Lignans': 'Hot-NS',
    'Phenols': 'Hot-Temperate',
    'Fats and Oils': 'Cold-Temperate',
    'Phenolic acid esters': 'Cold-Dry',
    'Iridoids': 'Hot-Wet',
    'Anthraquinones': 'NS-Wet',
    'Steroids': 'Temperate-Wet',
    'Cardiac Glycosides': 'NS-Temperate',
    'Unknown': 'Unknown',
}

EXACT_COMPOUND_CLASS = {
    'saikosaponin a': 'Saponins',
    'ginsenoside rb1': 'Saponins',
    'notoginsenoside r1': 'Saponins',
    'ophiopogonin d': 'Saponins',
    'astragaloside iv': 'Saponins',
    'platycodin d': 'Saponins',
    'pinoresinol diglucoside': 'Lignans',
    'schisandrin': 'Lignans',
    'arctigenin': 'Lignans',
    'baicalin': 'Flavonoids',
    'hesperidin': 'Flavonoids',
    'rutin': 'Flavonoids',
    'hyperoside': 'Flavonoids',
    'icariin': 'Flavonoids',
    'puerarin': 'Flavonoids',
    'geniposide': 'Iridoids',
    'gastrodin': 'Phenolic acids',
    'mangiferin': 'Flavonoids',
    'formononetin': 'Flavonoids',
    'astilbin': 'Flavonoids',
    'perillaldehyde': 'Volatile oils',
    'eucalyptol': 'Volatile oils',
    'linalool': 'Volatile oils',
    'limonene': 'Volatile oils',
    'anethole': 'Volatile oils',
    'menthol': 'Volatile oils',
    'menthone': 'Volatile oils',
    'methyleugenol': 'Volatile oils',
    'cinnamaldehyde': 'Volatile oils',
    'thymol': 'Volatile oils',
    'carvone': 'Volatile oils',
    'citronellal': 'Volatile oils',
    'citric acid': 'Fruit acids',
    'chlorogenic acid': 'Phenolic acid esters',
    'rosmarinic acid': 'Phenolic acid esters',
    'salvianolic acid b': 'Phenolic acid esters',
    'ferulic acid': 'Phenolic acids',
    'hydroxysafflor yellow a': 'Phenolic acids',
    'salicin': 'Phenolic acids',
    'emodin': 'Anthraquinones',
    'gentiopicroside': 'Iridoids',
    'paeoniflorin': 'Iridoids',
    'catalpol': 'Iridoids',
    'artemisinin': 'Terpenes (nonvolatile)',
    'andrographolide': 'Terpenes (nonvolatile)',
    'tussilagone': 'Terpenes (nonvolatile)',
    'costunolide': 'Terpenes (nonvolatile)',
    'tanshinone iia': 'Terpenes (nonvolatile)',
    'boswellic acid': 'Fats and Oils',
    'oleanolic acid': 'Fats and Oils',
    'betulin': 'Fats and Oils',
    'pachymic acid': 'Fats and Oils',
    'diosgenin': 'Steroids',
    'ecdysterone': 'Steroids',
    'amygdalin': 'Cardiac Glycosides',
    'berberine': 'Alkaloids',
    'aconitine': 'Alkaloids',
    'ephedrine': 'Alkaloids',
    'arecoline': 'Alkaloids',
    'evodiamine': 'Alkaloids',
    'matrine': 'Alkaloids',
    'tetrahydropalmatine': 'Alkaloids',
    'tetramethylpyrazine': 'Alkaloids',
    'leonurine': 'Alkaloids',
    'liensinine': 'Alkaloids',
    'nuciferine': 'Alkaloids',
    'rhynchophylline': 'Alkaloids',
    'gentiopicroside': 'Iridoids',
    'phillyrin': 'Lignans',
    'pinoresinol diglucoside': 'Lignans',
    'schisandrin': 'Lignans',
    'purpurin': 'Phenols',
    'resveratrol': 'Phenols',
    'saponin': 'Saponins',
}

KEYWORD_CLASS_HINTS = [
    ('saponin', 'Saponins'),
    ('glycoside', 'Flavonoids'),
    ('flav', 'Flavonoids'),
    ('isoflav', 'Flavonoids'),
    ('anthocyan', 'Flavonoids'),
    ('coumarin', 'Coumarins'),
    ('alkaloid', 'Alkaloids'),
    ('ine', 'Alkaloids'),
    ('amine', 'Alkaloids'),
    ('berber', 'Alkaloids'),
    ('quinine', 'Alkaloids'),
    ('ole', 'Volatile oils'),
    ('ane', 'Volatile oils'),
    ('ol', 'Volatile oils'),
    ('aldehyde', 'Volatile oils'),
    ('acid', 'Phenolic acids'),
    ('phenol', 'Phenols'),
    ('stilbene', 'Phenols'),
    ('lignan', 'Lignans'),
    ('terpen', 'Terpenes (nonvolatile)'),
    ('sterol', 'Steroids'),
    ('steroid', 'Steroids'),
    ('saponin', 'Saponins'),
    ('iridoid', 'Iridoids'),
    ('anthraquinone', 'Anthraquinones'),
]


def guess_compound_class(compound_name: str) -> str:
    clean_name = compound_name.strip().lower()
    if clean_name in EXACT_COMPOUND_CLASS:
        return EXACT_COMPOUND_CLASS[clean_name]

    for key, class_name in KEYWORD_CLASS_HINTS:
        if key in clean_name:
            return class_name

    if clean_name.endswith('one') or clean_name.endswith('ol'):
        return 'Volatile oils'
    if clean_name.endswith('ine') or clean_name.endswith('ide'):
        return 'Alkaloids'
    if clean_name.endswith('acid'):
        return 'Phenolic acids'
    return 'Unknown'


def collect_compound_rows(compound_dir: Path) -> dict:
    catalog = {}
    for csv_path in sorted(compound_dir.glob('*.csv')):
        with csv_path.open(newline='') as fh:
            reader = csv.DictReader(fh)
            if 'smiles' not in reader.fieldnames or 'marker_compound' not in reader.fieldnames:
                continue
            for row in reader:
                name = (row.get('marker_compound') or row.get('herb') or row.get('source_name') or '').strip()
                if not name:
                    continue

                smiles = (row.get('smiles') or '').strip()
                formula = (row.get('formula_verified') or '').strip()
                verification_strength = (row.get('verification_strength') or '').strip()
                compound_type = guess_compound_class(name)
                temperament = CLASS_TEMPERAMENT_MAP.get(compound_type, 'Unknown')

                key = (name, smiles, formula)
                entry = catalog.setdefault(key, {
                    'marker_compound': name,
                    'smiles': smiles,
                    'formula_verified': formula,
                    'verification_strength': verification_strength,
                    'source_files': [],
                    'compound_type': compound_type,
                    'temperament': temperament,
                    'notes': '',
                })
                if csv_path.name not in entry['source_files']:
                    entry['source_files'].append(csv_path.name)
                if verification_strength and verification_strength not in entry['verification_strength']:
                    if entry['verification_strength']:
                        entry['verification_strength'] = f"{entry['verification_strength']} | {verification_strength}"
                    else:
                        entry['verification_strength'] = verification_strength
                if entry['compound_type'] == 'Unknown' and compound_type != 'Unknown':
                    entry['compound_type'] = compound_type
                    entry['temperament'] = temperament

    return catalog


def write_compound_catalog(catalog: dict, out_path: Path):
    fieldnames = [
        'marker_compound',
        'smiles',
        'formula_verified',
        'verification_strength',
        'source_files',
        'compound_type',
        'temperament',
        'notes',
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for entry in sorted(catalog.values(), key=lambda e: e['marker_compound'].lower()):
            row = {
                'marker_compound': entry['marker_compound'],
                'smiles': entry['smiles'],
                'formula_verified': entry['formula_verified'],
                'verification_strength': entry['verification_strength'],
                'source_files': ';'.join(entry['source_files']),
                'compound_type': entry['compound_type'],
                'temperament': entry['temperament'],
                'notes': entry['notes'],
            }
            writer.writerow(row)


if __name__ == '__main__':
    out_file = Path('data/compounds/compound_catalog.csv')
    catalog = collect_compound_rows(Path('data/compounds'))
    write_compound_catalog(catalog, out_file)
    print(f'Wrote {len(catalog)} compound catalog entries to {out_file}')
