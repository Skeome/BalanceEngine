import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))
from build_dataset import build_dataset

existing_df = pd.read_csv('data/compounds/tcm_verified.csv')
existing_herbs = set(existing_df['herb_pinyin'].str.lower())
# also add batch1
b1_df = pd.read_csv('data/compounds/batch1.csv')
existing_herbs.update(set(b1_df['source_name'].str.lower()))

herb_pm = pd.read_csv('data/herb_pm.csv')
pinyin_col = [c for c in herb_pm.columns if 'pinyin' in c.lower()][0]
prop_col = [c for c in herb_pm.columns if 'property' in c.lower()][0]
herb_pm[pinyin_col] = herb_pm[pinyin_col].str.lower().str.replace(' ', '')
prop_map = dict(zip(herb_pm[pinyin_col], herb_pm[prop_col]))

candidates = [
    ("bai bu", "stemonine"),
    ("cang zhu", "atractylodin"),
    ("dong chong xia cao", "cordycepin"),
    ("fang feng", "prim-O-glucosylcimifugin"),
    ("fu ling", "pachymic acid"),
    ("gou teng", "rhynchophylline"),
    ("he ye", "nuciferine"),
    ("hong hua", "hydroxysafflor yellow A"),
    ("kuan dong hua", "tussilagone"),
    ("lian zi", "liensinine"),
    ("lu hui", "aloin"),
    ("mu gua", "oleanolic acid"),
    ("qian hu", "praeruptorin A"),
    ("rou cong rong", "echinacoside"),
    ("sang bai pi", "morusin"),
    ("shan yao", "diosgenin"),
    ("suan zao ren", "jujuboside A"),
    ("tao ren", "amygdalin"),
    ("tu si zi", "hyperoside"),
    ("xing ren", "amygdalin"),
    ("xuan shen", "harpagoside"),
    ("yan hu suo", "tetrahydropalmatine"),
    ("yi mu cao", "leonurine"),
    ("yin xing ye", "ginkgolide A"),
    ("zhi ke", "naringin"),
    ("zi su ye", "perillaldehyde"),
    ("wu mei", "citric acid"),
    ("cang er zi", "atractyloside"),
    ("che qian zi", "plantamajoside"),
    ("huang jing", "diosgenin"),
    ("hu zhang", "resveratrol"),
    ("jie geng", "platycodin D"),
    ("mu xiang", "costunolide"),
    ("niu xi", "ecdysterone"),
    ("nu zhen zi", "specnuezhenide"),
    ("qian cao", "purpurin"),
    ("qiang huo", "notopterol"),
    ("qin jiao", "gentiopicroside"),
    ("ru xiang", "boswellic acid"),
    ("sha ren", "bornyl acetate"),
    ("she gan", "tectoridin"),
    ("wu yao", "linderane"),
    ("xi xin", "methyleugenol"),
    ("ze xie", "alisol B")
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
    build_dataset(entries, "data/compounds/batch2.csv")
