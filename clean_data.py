#!/usr/bin/env python3
"""Clean up type chart and add Chinese translations."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Type name mappings (English -> Chinese)
TYPE_CN = {
    "Normal": "一般", "Fire": "火", "Water": "水", "Electric": "电",
    "Grass": "草", "Ice": "冰", "Fighting": "格斗", "Poison": "毒",
    "Ground": "地面", "Flying": "飞行", "Psychic": "超能", "Bug": "虫",
    "Rock": "岩石", "Ghost": "幽灵", "Dragon": "龙", "Dark": "恶",
    "Steel": "钢", "Fairy": "妖精", "Stellar": "星晶"
}

# Reverse mapping
TYPE_EN = {v: k for k, v in TYPE_CN.items()}

# Standard types (excluding Stellar)
STANDARD_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

def clean_typechart():
    """Clean the raw typechart data."""
    with open(os.path.join(DATA_DIR, "typechart.json")) as f:
        raw_chart = json.load(f)
    
    # Showdown typechart values:
    # 0 = immune (0x)
    # 1 = normal (1x)
    # 2 = super effective (2x)
    # 3 = not very effective (0.5x)
    # 4 = immune (0x) - sometimes used
    # Also has special entries like 'prankster', 'par', etc. that we skip
    
    VALUE_MAP = {0: 0, 1: 1, 2: 2, 3: 0.5}
    
    chart = {}
    for type_en, matchups in raw_chart.items():
        type_key = type_en.capitalize()
        if type_key not in STANDARD_TYPES:
            continue
        
        clean_matchups = {}
        for target, value in matchups.items():
            if target.capitalize() not in STANDARD_TYPES:
                continue  # Skip non-type entries like 'prankster', 'par'
            if isinstance(value, (int, float)):
                clean_matchups[target] = VALUE_MAP.get(value, value)
        
        chart[type_key] = clean_matchups
    
    with open(os.path.join(DATA_DIR, "typechart_clean.json"), "w") as f:
        json.dump(chart, f, indent=2, ensure_ascii=False)
    
    print(f"Cleaned type chart: {len(chart)} types")
    return chart

def create_type_cn_map():
    """Create a comprehensive English-Chinese mapping for Pokemon, moves, etc."""
    # This will be populated from the actual data
    mapping = {"types": TYPE_CN}
    
    with open(os.path.join(DATA_DIR, "type_cn.json"), "w") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print("Created type CN mapping")

if __name__ == "__main__":
    chart = clean_typechart()
    create_type_cn_map()
    
    # Show the cleaned chart
    print("\nType effectiveness (showing 2x and 0.5x):")
    for atk_type, matchups in sorted(chart.items()):
        super_eff = [t for t, v in matchups.items() if v == 2]
        not_eff = [t for t, v in matchups.items() if v == 0.5]
        immune = [t for t, v in matchups.items() if v == 0]
        if super_eff or not_eff:
            print(f"  {atk_type}: 2x={super_eff} 0.5x={not_eff}")
