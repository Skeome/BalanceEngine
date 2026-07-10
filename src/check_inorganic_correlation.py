import csv
import re
import numpy as np
from scipy.stats import pearsonr
import sys

# Ensure we can import atomic_descriptors
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from atomic_descriptors import formula_descriptors

def parse_formula(f_str):
    # Very simple formula parser for these specific 17 formulas
    # Handles e.g. S, CaO, NaCl, KNO3, FeSO4, CuSO4, HgS, As2S3, As4S4, Hg, Pb, Sn, Cu, Au, Ag, Fe
    # And KAl(SO4)2
    if f_str == 'KAl(SO4)2':
        return {'K':1, 'Al':1, 'S':2, 'O':8}
    
    counts = {}
    tokens = re.findall(r'([A-Z][a-z]*)(\d*)', f_str)
    for elem, num in tokens:
        counts[elem] = counts.get(elem, 0) + (int(num) if num else 1)
    return counts

hc_values = []
en_avgs = []
en_spreads = []
labels = []

with open('/home/skeome/Development/Balance_Engine/source_materials/lovell_minerals.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            f_dict = parse_formula(row['formula'])
            desc = formula_descriptors(f_dict)
            hc = int(row['hot']) - int(row['cold'])
            en_avg = desc.get('avg_electronegativity_pauling')
            en_spread = desc.get('electronegativity_spread', 0.0)
            
            if en_avg is not None:
                hc_values.append(hc)
                en_avgs.append(en_avg)
                en_spreads.append(en_spread)
                labels.append(row['substance'])
                print(f"{row['substance']:<15} formula={row['formula']:<10} hc={hc:2d}  avg_en={en_avg:.2f}  en_spread={en_spread:.2f}")
        except Exception as e:
            print(f"Error processing {row['substance']}: {e}")

if len(hc_values) > 2:
    r_avg, p_avg = pearsonr(hc_values, en_avgs)
    r_spread, p_spread = pearsonr(hc_values, en_spreads)
    print("\n--- Correlations ---")
    print(f"HC_signed vs Avg EN:     r = {r_avg:.3f}, p = {p_avg:.3f}")
    print(f"HC_signed vs EN Spread:  r = {r_spread:.3f}, p = {p_spread:.3f}")
