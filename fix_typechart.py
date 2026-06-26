#!/usr/bin/env python3
"""Fix type chart values based on Showdown format."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Showdown damageTaken values:
# 0 = not very effective (0.5x)
# 1 = normal (1x) 
# 2 = super effective (2x)
# 3 = immune (0x)
VALUE_MAP = {0: 0.5, 1: 1, 2: 2, 3: 0}

def fix_typechart():
    with open(os.path.join(DATA_DIR, "typechart.json")) as f:
        raw = json.load(f)
    
    fixed = {}
    for type_name, data in raw.items():
        # Skip non-type entries
        if type_name.lower() not in [t.lower() for t in [
            'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
            'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
            'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy', 'Stellar'
        ]]:
            continue
        
        fixed[type_name] = {}
        for target, value in data.items():
            if target.lower() in ['prankster', 'par', 'psn', 'brn', 'frz', 'slp']:
                continue  # Skip status conditions
            if isinstance(value, (int, float)):
                fixed[type_name][target] = VALUE_MAP.get(value, value)
    
    with open(os.path.join(DATA_DIR, "typechart_clean.json"), "w") as f:
        json.dump(fixed, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed type chart: {len(fixed)} types")
    
    # Verify
    print("\nVerification:")
    print(f"  Bug vs Fighting: {fixed.get('Bug', {}).get('Fighting')} (should be 2)")
    print(f"  Bug vs Fire: {fixed.get('Bug', {}).get('Fire')} (should be 0.5)")
    print(f"  Ground vs Electric: {fixed.get('Ground', {}).get('Electric')} (should be 2)")
    print(f"  Ground vs Flying: {fixed.get('Ground', {}).get('Flying')} (should be 0)")
    print(f"  Dragon vs Fairy: {fixed.get('Dragon', {}).get('Fairy')} (should be 0.5)")
    print(f"  Dragon vs Dragon: {fixed.get('Dragon', {}).get('Dragon')} (should be 1)")

if __name__ == "__main__":
    fix_typechart()
