#!/usr/bin/env python3
"""Fetch Pokemon data from Smogon for Champions format."""

import json
import os
import sys
import time
import urllib.request

# Proxy settings
PROXY = "http://127.0.0.1:7890"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_url(url):
    """Fetch URL with proxy."""
    proxy_handler = urllib.request.ProxyHandler({
        'http': PROXY,
        'https': PROXY,
    })
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    })
    with opener.open(req, timeout=30) as resp:
        return resp.read().decode('utf-8')

def fetch_smogon_dex():
    """Fetch the full Smogon dex data for Champions format."""
    print("Fetching Smogon dex data...")
    # The Smogon dex page embeds all data as JSON in dexSettings
    url = "https://www.smogon.com/dex/champions/"
    html = fetch_url(url)
    
    # Extract dexSettings JSON
    marker = 'dexSettings = '
    idx = html.find(marker)
    if idx == -1:
        print("ERROR: Could not find dexSettings in page")
        return None
    
    # Find the JSON object
    start = idx + len(marker)
    # Find matching closing brace
    depth = 0
    end = start
    for i, c in enumerate(html[start:], start):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    json_str = html[start:end]
    data = json.loads(json_str)
    
    # Save raw dex settings
    with open(os.path.join(DATA_DIR, "smogon_dex_raw.json"), "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved raw dex data ({len(json_str)} bytes)")
    return data

def extract_pokemon_data(dex_data):
    """Extract Pokemon data from dex settings."""
    pokemon_list = []
    
    # The data is in injectRpcs format
    for rpc in dex_data.get("injectRpcs", []):
        if isinstance(rpc, list) and len(rpc) >= 2:
            cmd = rpc[0]
            if "dump-basics" in cmd:
                basics = rpc[1]
                for p in basics.get("pokemon", []):
                    if p.get("isNonstandard") in ("Standard", None) or "Champions" in p.get("oob", {}).get("genfamily", []):
                        pokemon_list.append(p)
    
    # If no Pokemon found, try alternative structure
    if not pokemon_list:
        for rpc in dex_data.get("injectRpcs", []):
            if isinstance(rpc, list) and len(rpc) >= 2:
                if isinstance(rpc[1], dict) and "pokemon" in rpc[1]:
                    for p in rpc[1]["pokemon"]:
                        pokemon_list.append(p)
    
    print(f"Extracted {len(pokemon_list)} Pokemon")
    return pokemon_list

def fetch_type_chart():
    """Fetch type effectiveness chart from PokeAPI."""
    print("Fetching type chart from PokeAPI...")
    
    type_names = [
        "normal", "fire", "water", "electric", "grass", "ice",
        "fighting", "poison", "ground", "flying", "psychic",
        "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"
    ]
    
    chart = {}
    for atk_type in type_names:
        url = f"https://pokeapi.co/api/v2/type/{atk_type}"
        data = json.loads(fetch_url(url))
        
        chart[atk_type] = {}
        for relation in data.get("damage_relations", {}).get("double_damage_to", []):
            chart[atk_type][relation["name"]] = 2.0
        for relation in data.get("damage_relations", {}).get("half_damage_to", []):
            chart[atk_type][relation["name"]] = 0.5
        for relation in data.get("damage_relations", {}).get("no_damage_to", []):
            chart[atk_type][relation["name"]] = 0.0
        
        time.sleep(0.2)  # Rate limit
    
    with open(os.path.join(DATA_DIR, "type_chart.json"), "w") as f:
        json.dump(chart, f, indent=2)
    
    print(f"Saved type chart ({len(chart)} types)")
    return chart

if __name__ == "__main__":
    # Step 1: Fetch Smogon dex
    dex_data = fetch_smogon_dex()
    if dex_data:
        pokemon_list = extract_pokemon_data(dex_data)
        with open(os.path.join(DATA_DIR, "pokemon_raw.json"), "w") as f:
            json.dump(pokemon_list, f, indent=2)
        print(f"Saved {len(pokemon_list)} Pokemon to pokemon_raw.json")
    
    # Step 2: Fetch type chart
    fetch_type_chart()
    
    print("\nDone! Data saved to data/ directory.")
