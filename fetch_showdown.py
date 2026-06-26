#!/usr/bin/env python3
"""Fetch Pokemon data from Pokemon Showdown GitHub repo."""

import json
import os
import re
import sys
import urllib.request

PROXY = "http://127.0.0.1:7890"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

RAW_DIR = os.path.join(DATA_DIR, "raw")
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data"

def fetch_url(url):
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with opener.open(req, timeout=60) as resp:
        return resp.read().decode('utf-8')

def fetch_file(filename):
    url = f"{BASE_URL}/{filename}"
    print(f"Fetching {filename}...")
    content = fetch_url(url)
    local_path = os.path.join(RAW_DIR, filename)
    with open(local_path, "w") as f:
        f.write(content)
    print(f"  Saved ({len(content)} bytes)")
    return content

def parse_pokedex(ts_content):
    """Parse pokedex.ts to extract Pokemon data."""
    pokemon = {}
    
    # Match each Pokemon entry
    # Pattern: pokemonname: { ... }
    pattern = r'(\w+):\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    # Simpler approach: extract key-value pairs
    lines = ts_content.split('\n')
    current_id = None
    current_data = {}
    brace_depth = 0
    
    for line in lines:
        stripped = line.strip()
        
        # New Pokemon entry
        if brace_depth == 0 and ':' in stripped and stripped.endswith('{'):
            current_id = stripped.split(':')[0].strip()
            current_data = {}
            brace_depth = 1
            continue
        
        if brace_depth > 0:
            brace_depth += stripped.count('{') - stripped.count('}')
            
            if brace_depth == 0:
                # End of entry
                if current_id and current_data.get('name'):
                    pokemon[current_id] = current_data
                current_id = None
                current_data = {}
                continue
            
            # Extract fields
            m = re.match(r'(\w+):\s*(.+),?\s*$', stripped)
            if m:
                key = m.group(1)
                val = m.group(2).rstrip(',').strip()
                
                if key == 'name':
                    current_data['name'] = val.strip('"')
                elif key == 'num':
                    current_data['num'] = int(val)
                elif key == 'types':
                    types_match = re.findall(r'"(\w+)"', val)
                    current_data['types'] = types_match
                elif key == 'baseStats':
                    stats = {}
                    for stat_match in re.finditer(r'(\w+):\s*(\d+)', val):
                        stats[stat_match.group(1)] = int(stat_match.group(2))
                    current_data['baseStats'] = stats
                elif key == 'abilities':
                    abs_match = re.findall(r'"([^"]+)"', val)
                    current_data['abilities'] = abs_match
                elif key == 'otherFormes':
                    formes = re.findall(r'"([^"]+)"', val)
                    current_data['otherFormes'] = formes
    
    return pokemon

def parse_moves(ts_content):
    """Parse moves.ts to extract move data."""
    moves = {}
    lines = ts_content.split('\n')
    current_id = None
    current_data = {}
    brace_depth = 0
    
    for line in lines:
        stripped = line.strip()
        
        if brace_depth == 0 and ':' in stripped and stripped.endswith('{'):
            current_id = stripped.split(':')[0].strip()
            current_data = {}
            brace_depth = 1
            continue
        
        if brace_depth > 0:
            brace_depth += stripped.count('{') - stripped.count('}')
            
            if brace_depth == 0:
                if current_id and current_data.get('name'):
                    moves[current_id] = current_data
                current_id = None
                current_data = {}
                continue
            
            m = re.match(r'(\w+):\s*(.+),?\s*$', stripped)
            if m:
                key = m.group(1)
                val = m.group(2).rstrip(',').strip()
                
                if key == 'name':
                    current_data['name'] = val.strip('"')
                elif key == 'type':
                    current_data['type'] = val.strip('"')
                elif key == 'category':
                    current_data['category'] = val.strip('"')
                elif key == 'power':
                    current_data['power'] = int(val) if val != '0' else 0
                elif key == 'accuracy':
                    current_data['accuracy'] = int(val) if val not in ('true', 'false') else val
                elif key == 'pp':
                    current_data['pp'] = int(val)
                elif key == 'priority':
                    current_data['priority'] = int(val)
                elif key == 'target':
                    current_data['target'] = val.strip('"')
                elif key == 'flags':
                    flags = re.findall(r'(\w+):', val)
                    current_data['flags'] = flags
                elif key == 'description':
                    current_data['description'] = val.strip('"')
    
    return moves

def parse_typechart(ts_content):
    """Parse typechart.ts to extract type effectiveness."""
    chart = {}
    lines = ts_content.split('\n')
    current_type = None
    current_data = {}
    brace_depth = 0
    
    for line in lines:
        stripped = line.strip()
        
        if brace_depth == 0 and ':' in stripped and stripped.endswith('{'):
            current_type = stripped.split(':')[0].strip()
            current_data = {}
            brace_depth = 1
            continue
        
        if brace_depth > 0:
            brace_depth += stripped.count('{') - stripped.count('}')
            
            if brace_depth == 0:
                if current_type:
                    chart[current_type] = current_data
                current_type = None
                current_data = {}
                continue
            
            # Check for damageTaken
            if 'damageTaken' in stripped:
                # Parse the nested damageTaken object
                pass
            
            # Parse damageTaken entries
            m = re.match(r'"?(\w+)"?:\s*"?(\w+)"?,?\s*$', stripped)
            if m:
                target = m.group(1)
                damage = m.group(2)
                current_data[target] = damage
    
    return chart

if __name__ == "__main__":
    # Fetch key data files
    files = ["pokedex.ts", "moves.ts", "typechart.ts"]
    
    for f in files:
        try:
            content = fetch_file(f)
        except Exception as e:
            print(f"  Error fetching {f}: {e}")
            continue
    
    # Parse pokedex
    print("\nParsing pokedex...")
    with open(os.path.join(RAW_DIR, "pokedex.ts")) as f:
        pokedex = parse_pokedex(f.read())
    print(f"  Found {len(pokedex)} Pokemon")
    
    with open(os.path.join(DATA_DIR, "pokedex.json"), "w") as f:
        json.dump(pokedex, f, indent=2, ensure_ascii=False)
    
    # Parse moves
    print("Parsing moves...")
    with open(os.path.join(RAW_DIR, "moves.ts")) as f:
        moves = parse_moves(f.read())
    print(f"  Found {len(moves)} moves")
    
    with open(os.path.join(DATA_DIR, "moves.json"), "w") as f:
        json.dump(moves, f, indent=2, ensure_ascii=False)
    
    print("\nDone! Check data/ directory.")
