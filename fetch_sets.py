#!/usr/bin/env python3
"""Fetch competitive sets data from Smogon for popular Pokemon."""

import json
import os
import re
import sys
import time
import urllib.request

PROXY = "http://127.0.0.1:7890"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Popular Pokemon in Champions format (by usage)
POPULAR_POKEMON = [
    "garchomp", "ragonite", "tyranitar", "metagross", "salamence",
    "gyarados", "charizard", "blaziken", "swampert", "sceptile",
    "lucario", "gengar", "scizor", "ferrothorn", "jellicent",
    "conkeldurr", "toxicroak", "hydrappl", "dragapult", "cinderace",
    "rillaboom", "urshifu", "landorus", "tornadus", "thundurus",
    "kyogre", "groudon", "rayquaza", "dialga", "palkia",
    "calyrex", "zacian", "zamazenta", "eternatus", "koraidon",
    "miraidon", "ironhands", "ironbundle", "fluttermane", "greattusk",
    "screamtail", "brutebonnet", "slitherwing", "sandyshocks",
    "amoonguss", "rotom", "weavile", "hydreigon", "volcarona",
    "excadrill", "kingambit", "baxcalibur", "gholdengo", "clodsire",
    "pawmot", "annihilape", "tatsugiri", "palafin", "dondozo",
    "gliscor", "mamoswine", "clefable", "blissey", "toxapex",
    "slowking", "slowbro", "tapukoko", "tapulele", "tapubulu",
    "tapufini", "necrozma", "solgaleo", "lunala", "xerneas",
    "yveltal", "zygarde", "reshiram", "zekrom", "kyurem",
]

def fetch_url(url):
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    with opener.open(req, timeout=30) as resp:
        return resp.read().decode('utf-8')

def fetch_pokemon_sets(pokemon_name):
    """Fetch sets data for a single Pokemon."""
    url = f"https://www.smogon.com/dex/champions/pokemon/{pokemon_name}/"
    
    try:
        html = fetch_url(url)
    except Exception as e:
        print(f"  Error fetching {pokemon_name}: {e}")
        return None
    
    # Extract dexSettings
    idx = html.find('dexSettings = ')
    if idx < 0:
        print(f"  Could not find dexSettings for {pokemon_name}")
        return None
    
    start = idx + len('dexSettings = ')
    depth = 0
    end = start
    for i in range(start, min(start + 1000000, len(html))):
        if html[i] == '{':
            depth += 1
        elif html[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    try:
        data = json.loads(html[start:end])
    except json.JSONDecodeError:
        print(f"  JSON parse error for {pokemon_name}")
        return None
    
    # Extract strategies
    for rpc in data.get('injectRpcs', []):
        if isinstance(rpc, list) and len(rpc) >= 2:
            cmd = rpc[0]
            if 'dump-pokemon' in cmd:
                pokemon_data = rpc[1]
                strategies = pokemon_data.get('strategies', [])
                
                all_sets = []
                for strat in strategies:
                    format_name = strat.get('format', 'Unknown')
                    movesets = strat.get('movesets', [])
                    
                    for ms in movesets:
                        set_data = {
                            'format': format_name,
                            'name': ms.get('name', 'Unknown'),
                            'pokemon': ms.get('pokemon', pokemon_name),
                            'abilities': ms.get('abilities', []),
                            'items': ms.get('items', []),
                            'natures': ms.get('natures', []),
                            'evconfigs': ms.get('evconfigs', []),
                            'moveslots': ms.get('moveslots', []),
                            'teratypes': ms.get('teratypes', []),
                        }
                        all_sets.append(set_data)
                
                return all_sets
    
    return None

def main():
    # Load existing data if any
    sets_file = os.path.join(DATA_DIR, "pokemon_sets.json")
    if os.path.exists(sets_file):
        with open(sets_file) as f:
            all_sets = json.load(f)
    else:
        all_sets = {}
    
    # Fetch sets for popular Pokemon
    total = len(POPULAR_POKEMON)
    for i, pokemon in enumerate(POPULAR_POKEMON):
        if pokemon in all_sets:
            print(f"[{i+1}/{total}] {pokemon} (cached)")
            continue
        
        print(f"[{i+1}/{total}] Fetching {pokemon}...")
        sets = fetch_pokemon_sets(pokemon)
        
        if sets:
            all_sets[pokemon] = sets
            print(f"  Found {len(sets)} sets")
        else:
            all_sets[pokemon] = []
            print(f"  No sets found")
        
        # Save periodically
        if (i + 1) % 10 == 0:
            with open(sets_file, 'w') as f:
                json.dump(all_sets, f, indent=2, ensure_ascii=False)
            print(f"  Saved progress ({len(all_sets)} Pokemon)")
        
        time.sleep(0.5)  # Rate limit
    
    # Final save
    with open(sets_file, 'w') as f:
        json.dump(all_sets, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Saved sets for {len(all_sets)} Pokemon")
    
    # Stats
    total_sets = sum(len(v) for v in all_sets.values())
    print(f"Total sets: {total_sets}")

if __name__ == "__main__":
    main()
