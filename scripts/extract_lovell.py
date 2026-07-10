import re

with open('source_materials/lovell_ocr_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace newlines with spaces for easier regex matching
text_flat = re.sub(r'\s+', ' ', text)

targets = [
    ("Sulfur", ["Sulphur", "Brimftone", "Brimstone"]),
    ("Quicklime", ["Quicklime", "Calx viva", "Calx-viva"]),
    ("Common Salt", ["Salt ", "Sal "]),
    ("Saltpetre/Nitre", ["Nitre", "Salt-peter", "Saltpeter"]),
    ("Alum", ["Alum ", "Allum", "Alumen"]),
    ("Vitriol/Iron Vitriol", ["Vitriol"]),
    ("Cinnabar", ["Cinnabar", "Cinnabaris"]),
    ("Orpiment", ["Orpiment", "Auripigmentum"]),
    ("Realgar", ["Realgar", "Sandarach"]),
    ("Mercury/Quicksilver", ["Mercury", "Quick-filver", "Quick-silver", "Quicksilver"]),
    ("Lead", ["Lead ", "Plumbum"]),
    ("Tin", ["Tin ", "Stannum"]),
    ("Copper", ["Copper", " Aes ", "Venus"]),
    ("Gold", ["Gold", "Aurum"]),
    ("Silver", ["Silver", "Argentum"]),
    ("Iron", ["Iron ", "Ferrum"])
]

results = []

for sub, aliases in targets:
    for alias in aliases:
        # Look for the alias, followed by up to 400 chars, followed by "Temper"
        matches = re.finditer(rf'(.{{0,100}}{re.escape(alias)}[^.]*?Temper[^.]*\.)', text_flat, re.IGNORECASE)
        for m in matches:
            print(f"[{sub}] {m.group(1).strip()}")

