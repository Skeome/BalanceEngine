import re
import json

with open('/home/skeome/Development/Balance_Engine/source_materials/lovell_minerals_ocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text_flat = re.sub(r'\s+', ' ', text)

targets = {
    "Sulfur": ["Sulphur", "Brimftone", "Brimstone"],
    "Quicklime": ["Quicklime", "Calx viva", "Calx"],
    "Common Salt": [" Salt ", " Sal "],
    "Saltpetre/Nitre": ["Nitre", "Salt-peter", "Saltpeter", "Nitrum"],
    "Alum": ["Alum", "Allum", "Alumen"],
    "Vitriol": ["Vitriol"],
    "Cinnabar": ["Cinnabar", "Cinnabaris"],
    "Orpiment": ["Orpiment", "Auripigmentum"],
    "Realgar": ["Realgar", "Sandarach", "Sandaracha"],
    "Mercury": ["Mercury", "Quick-filver", "Quick-silver", "Quicksilver"],
    "Lead": ["Lead", "Plumbum"],
    "Tin": ["Tin", "Stannum"],
    "Copper": ["Copper", " Aes ", "Venus"],
    "Gold": ["Gold", "Aurum"],
    "Silver": ["Silver", "Argentum"],
    "Iron": ["Iron", "Ferrum"]
}

results = {}
for target, aliases in targets.items():
    contexts = []
    for alias in aliases:
        for m in re.finditer(re.escape(alias), text_flat, re.IGNORECASE):
            start = max(0, m.start() - 50)
            end = min(len(text_flat), m.end() + 300)
            context = text_flat[start:end]
            if " T." in context or "Temper" in context or "hot" in context or "cold" in context:
                contexts.append(context)
    if contexts:
        results[target] = contexts[:3] # just take first 3 matches

with open('/home/skeome/Development/Balance_Engine/source_materials/parsed_contexts.txt', 'w', encoding='utf-8') as f:
    for k, v in results.items():
        f.write(f"=== {k} ===\n")
        for c in v:
            f.write(c + "\n---\n")
