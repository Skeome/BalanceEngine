import re
import csv

text_file = "source_materials/lovellpanzooryktologia.txt"
with open(text_file, "r", encoding="utf-8") as f:
    content = f.read()

# We want to find entries which look like "Name -> Place -> Matter -> Temperature"
# We can search for paragraphs containing "Temperature" and one of our target names.
paragraphs = content.split('\n\n')

targets = [
    ("Sulfur", ["Sulphur", "Brimstone"]),
    ("Quicklime", ["Quicklime", "Calx viva"]),
    ("Common Salt", ["Salt", "Sal "]),
    ("Saltpetre/Nitre", ["Nitre", "Salt-peter"]),
    ("Alum", ["Alum", "Allum", "Alumen"]),
    ("Vitriol/Iron Vitriol", ["Vitriol"]),
    ("Copper Vitriol", ["Copper Vitriol", "Blue Vitriol", "Vitriol of Copper"]),
    ("Cinnabar", ["Cinnabar", "Cinnabaris"]),
    ("Orpiment", ["Orpiment", "Auripigmentum"]),
    ("Realgar", ["Realgar", "Sandarach"]),
    ("Mercury/Quicksilver", ["Mercury", "Quick-silver"]),
    ("Lead", ["Lead", "Plumbum"]),
    ("Tin", ["Tin", "Stannum"]),
    ("Copper", ["Copper", "Aes", "Venus"]),
    ("Gold", ["Gold", "Aurum"]),
    ("Silver", ["Silver", "Argentum"]),
    ("Iron", ["Iron", "Ferrum"])
]

results = []
for p in paragraphs:
    if "Temperature" in p or "Temp." in p or "temperature" in p.lower():
        p_lower = p.lower()
        for substance, names in targets:
            if any(name.lower() in p_lower for name in names):
                results.append((substance, p.strip().replace('\n', ' ')))

with open("temp_results.txt", "w", encoding="utf-8") as out:
    for r in results:
        out.write(f"--- {r[0]} ---\n{r[1]}\n\n")

print(f"Found {len(results)} matches.")
