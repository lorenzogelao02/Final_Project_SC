#!/usr/bin/env python3
"""
Generate a borough-level resource summary CSV from processed datasets.
Writes output to website/assets/data/resource_summary.csv
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'website' / 'assets' / 'data' / 'resource_summary.csv'

files = {
    'Fountains': PROC / 'drinking_fountains_cleaned.csv',
    'Toilets': PROC / 'public_toilets_cleaned.csv',
    'Centers': PROC / 'drop_in_centers_cleaned.csv',
    'LinkNYC': PROC / 'link_nyc_cleaned.csv'
}

def read_boroughs(path):
    if not path.exists():
        return []
    boroughs = []
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # find likely borough key
        keys = [k.lower() for k in reader.fieldnames if k]
        key = None
        for candidate in ('borough','boro','boro_name','boro_name'.lower(),'boro_nm'):
            if candidate in keys:
                # find original key name
                for k in reader.fieldnames:
                    if k and k.lower() == candidate:
                        key = k
                        break
                if key:
                    break
        # fallback: look for field with name containing 'boro' or 'borough'
        if not key:
            for k in reader.fieldnames:
                if k and ('boro' in k.lower() or 'borough' in k.lower()):
                    key = k
                    break

        # If still not found, try common column names
        for row in reader:
            if key and row.get(key):
                boroughs.append(row[key].strip())
            else:
                # try some common fallbacks
                for fallback in ('borough','boro','boro_name','Borough'):
                    if fallback in row and row[fallback]:
                        boroughs.append(row[fallback].strip())
                        break
    return boroughs

def normalize(name):
    if not name:
        return ''
    n = name.strip()
    m = n.lower()
    if 'manhattan' in m:
        return 'Manhattan'
    if 'brooklyn' in m:
        return 'Brooklyn'
    if 'bronx' in m:
        return 'Bronx'
    if 'queens' in m:
        return 'Queens'
    if 'staten' in m or 'richmond' in m:
        return 'Staten Island'
    return n.title()

def main():
    counts = defaultdict(Counter)
    for res, path in files.items():
        boroughs = read_boroughs(path)
        for b in boroughs:
            bnorm = normalize(b)
            if bnorm:
                counts[res][bnorm] += 1

    boroughs = ['Manhattan','Brooklyn','Bronx','Queens','Staten Island']

    # ensure OUT dir exists
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Borough','Fountains','Toilets','Centers','LinkNYC'])
        for b in boroughs:
            row = [
                b,
                counts['Fountains'].get(b, 0),
                counts['Toilets'].get(b, 0),
                counts['Centers'].get(b, 0),
                counts['LinkNYC'].get(b, 0)
            ]
            writer.writerow(row)

    print(f'Wrote {OUT}')

if __name__ == '__main__':
    main()
