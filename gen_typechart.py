#!/usr/bin/env python3
"""Generate accurate type chart based on official Pokemon data."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Official Pokemon type effectiveness chart
# Key: attacking type, Value: {defending_type: multiplier}
# Based on the official Pokemon games

TYPE_CHART = {
    "Normal": {
        "Rock": 0.5, "Ghost": 0, "Steel": 0.5
    },
    "Fire": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2,
        "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2
    },
    "Water": {
        "Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2,
        "Rock": 2, "Dragon": 0.5
    },
    "Electric": {
        "Water": 2, "Grass": 0.5, "Ground": 0, "Flying": 2,
        "Dragon": 0.5
    },
    "Grass": {
        "Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5,
        "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2,
        "Dragon": 0.5, "Steel": 0.5
    },
    "Ice": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5,
        "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5
    },
    "Fighting": {
        "Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5,
        "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0,
        "Dark": 2, "Steel": 2, "Fairy": 0.5
    },
    "Poison": {
        "Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5,
        "Ghost": 0.5, "Steel": 0, "Fairy": 2
    },
    "Ground": {
        "Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2,
        "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2
    },
    "Flying": {
        "Grass": 2, "Electric": 0.5, "Ground": 0, "Bug": 2,
        "Rock": 0.5, "Steel": 0.5
    },
    "Psychic": {
        "Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0,
        "Steel": 0.5
    },
    "Bug": {
        "Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5,
        "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2,
        "Steel": 0.5, "Fairy": 0.5
    },
    "Rock": {
        "Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5,
        "Flying": 2, "Bug": 2, "Steel": 0.5
    },
    "Ghost": {
        "Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5
    },
    "Dragon": {
        "Dragon": 2, "Steel": 0.5, "Fairy": 0
    },
    "Dark": {
        "Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5,
        "Fairy": 0.5
    },
    "Steel": {
        "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2,
        "Rock": 2, "Steel": 0.5, "Fairy": 2
    },
    "Fairy": {
        "Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2,
        "Dark": 2, "Steel": 0.5
    }
}

def main():
    # Save the clean type chart
    with open(os.path.join(DATA_DIR, "typechart_clean.json"), "w") as f:
        json.dump(TYPE_CHART, f, indent=2, ensure_ascii=False)
    
    print(f"Saved official type chart ({len(TYPE_CHART)} types)")
    
    # Verify
    print("\nVerification:")
    print(f"  Fire vs Grass: {TYPE_CHART['Fire']['Grass']} (should be 2)")
    print(f"  Water vs Fire: {TYPE_CHART['Water']['Fire']} (should be 2)")
    print(f"  Electric vs Ground: {TYPE_CHART['Electric']['Ground']} (should be 0)")
    print(f"  Ground vs Flying: {TYPE_CHART['Ground']['Flying']} (should be 0)")
    print(f"  Dragon vs Fairy: {TYPE_CHART['Dragon']['Fairy']} (should be 0)")
    print(f"  Normal vs Ghost: {TYPE_CHART['Normal']['Ghost']} (should be 0)")

if __name__ == "__main__":
    main()
