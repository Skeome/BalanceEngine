import pandas as pd
import sys
import os

# Ensure we can import build_dataset
sys.path.append(os.path.join(os.getcwd(), 'src'))
from build_dataset import build_dataset

existing_df = pd.read_csv('data/compounds/tcm_verified.csv')
existing_herbs = set(existing_df['herb_pinyin'].str.lower())

herb_pm = pd.read_csv('data/herb_pm.csv')
# clean up column name for pinyin
pinyin_col = [c for c in herb_pm.columns if 'pinyin' in c.lower()][0]
prop_col = [c for c in herb_pm.columns if 'property' in c.lower()][0]
herb_pm[pinyin_col] = herb_pm[pinyin_col].str.lower().str.replace(' ', '')
prop_map = dict(zip(herb_pm[pinyin_col], herb_pm[prop_col]))

candidates = [
    ("ren shen", "ginsenoside Rb1"),
    ("lian qiao", "phillyrin"),
    ("chai hu", "saikosaponin A"),
    ("zhi mu", "mangiferin"),
    ("tian ma", "gastrodin"),
    ("ge gen", "puerarin"),
    ("chuan xiong", "tetramethylpyrazine"),
    ("mai dong", "ophiopogonin D"),
    ("wu zhu yu", "evodiamine"),
    ("ku shen", "matrine"),
    ("san qi", "notoginsenoside R1"),
    ("yuan zhi", "tenuifolin"),
    ("mu dan pi", "paeonol"),
    ("bai zhi", "imperatorin"),
    ("di huang", "catalpol"),
    ("huang bo", "berberine"),
    ("dang shen", "lobetyolin"),
    ("tu fu ling", "astilbin"),
    ("yin yang huo", "icariin"),
    ("du zhong", "pinoresinol diglucoside"),
    ("wu wei zi", "schisandrin")
]

entries = []
for h, m in candidates:
    h_clean = h.replace(' ', '')
    if h_clean in prop_map and h_clean not in [x.replace(' ','') for x in existing_herbs]:
        label = prop_map[h_clean]
        entries.append((h, m, label))

print(f"Found {len(entries)} valid candidates in herb_pm:")
for e in entries: print(" ", e)

if entries:
    print("Building dataset...")
    # we'll save it to a temporary csv and then append
    build_dataset(entries, "data/compounds/batch1.csv")
