/**
 * Parse Pokemon Showdown TypeScript data files into JSON.
 * Run: node parse_data.js
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, 'data');
const RAW_DIR = path.join(DATA_DIR, 'raw');

// ─── Pokedex Parser ───────────────────────────────────────────────
function parsePokedex(tsContent) {
    const pokemon = {};
    
    // Remove TypeScript type annotations and comments
    let content = tsContent
        .replace(/\/\*[\s\S]*?\*\//g, '')  // block comments
        .replace(/\/\/.*$/gm, '');           // line comments
    
    // Match each Pokemon entry using a state machine
    const lines = content.split('\n');
    let currentId = null;
    let currentObj = {};
    let depth = 0;
    let inObject = false;
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        // New top-level entry: id: {
        if (!inObject && /^\w+:\s*\{/.test(trimmed)) {
            currentId = trimmed.split(':')[0].trim();
            currentObj = {};
            depth = 1;
            inObject = true;
            continue;
        }
        
        if (!inObject) continue;
        
        // Count braces
        for (const ch of trimmed) {
            if (ch === '{') depth++;
            if (ch === '}') depth--;
        }
        
        if (depth <= 0) {
            // End of entry
            if (currentId && currentObj.name) {
                // Only include standard Pokemon (not past/nonstandard)
                pokemon[currentId] = currentObj;
            }
            currentId = null;
            currentObj = {};
            inObject = false;
            continue;
        }
        
        // Parse key: value pairs
        // name: "Bulbasaur"
        const nameMatch = trimmed.match(/^name:\s*"([^"]+)"/);
        if (nameMatch) { currentObj.name = nameMatch[1]; continue; }
        
        // num: 1
        const numMatch = trimmed.match(/^num:\s*(\d+)/);
        if (numMatch) { currentObj.num = parseInt(numMatch[1]); continue; }
        
        // types: ["Grass", "Poison"]
        const typesMatch = trimmed.match(/^types:\s*\[(.+)\]/);
        if (typesMatch) {
            currentObj.types = typesMatch[1].match(/"([^"]+)"/g)?.map(t => t.replace(/"/g, '')) || [];
            continue;
        }
        
        // baseStats: { hp: 45, atk: 49, ... }
        const statsMatch = trimmed.match(/^baseStats:\s*\{(.+)\}/);
        if (statsMatch) {
            const stats = {};
            const pairs = statsMatch[1].match(/(\w+):\s*(\d+)/g);
            if (pairs) {
                for (const pair of pairs) {
                    const [k, v] = pair.split(':').map(s => s.trim());
                    stats[k] = parseInt(v);
                }
            }
            currentObj.baseStats = stats;
            continue;
        }
        
        // abilities: { 0: "Overgrow", H: "Chlorophyll" }
        const absMatch = trimmed.match(/^abilities:\s*\{(.+)\}/);
        if (absMatch) {
            const abs = [];
            const parts = absMatch[1].match(/\d+:\s*"([^"]+)"/g);
            if (parts) {
                for (const p of parts) {
                    abs.push(p.match(/"([^"]+)"/)[1]);
                }
            }
            const hidden = absMatch[1].match(/H:\s*"([^"]+)"/);
            if (hidden) abs.push(hidden[1] + ' (隐藏)');
            currentObj.abilities = abs;
            continue;
        }
        
        // otherFormes: ["Venusaur-Mega"]
        const formesMatch = trimmed.match(/^otherFormes:\s*\[(.+)\]/);
        if (formesMatch) {
            currentObj.otherFormes = formesMatch[1].match(/"([^"]+)"/g)?.map(f => f.replace(/"/g, '')) || [];
            continue;
        }
        
        // baseSpecies: "Venusaur"
        const baseMatch = trimmed.match(/^baseSpecies:\s*"([^"]+)"/);
        if (baseMatch) { currentObj.baseSpecies = baseMatch[1]; continue; }
        
        // forme: "Mega"
        const formeMatch = trimmed.match(/^forme:\s*"([^"]+)"/);
        if (formeMatch) { currentObj.forme = formeMatch[1]; continue; }
    }
    
    return pokemon;
}

// ─── Moves Parser ─────────────────────────────────────────────────
function parseMoves(tsContent) {
    const moves = {};
    
    let content = tsContent
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*$/gm, '');
    
    const lines = content.split('\n');
    let currentId = null;
    let currentObj = {};
    let depth = 0;
    let inObject = false;
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        if (!inObject && /^\w+:\s*\{/.test(trimmed)) {
            currentId = trimmed.split(':')[0].trim();
            currentObj = {};
            depth = 1;
            inObject = true;
            continue;
        }
        
        if (!inObject) continue;
        
        for (const ch of trimmed) {
            if (ch === '{') depth++;
            if (ch === '}') depth--;
        }
        
        if (depth <= 0) {
            if (currentId && currentObj.name) {
                moves[currentId] = currentObj;
            }
            currentId = null;
            currentObj = {};
            inObject = false;
            continue;
        }
        
        const nameMatch = trimmed.match(/^name:\s*"([^"]+)"/);
        if (nameMatch) { currentObj.name = nameMatch[1]; continue; }
        
        const typeMatch = trimmed.match(/^type:\s*"([^"]+)"/);
        if (typeMatch) { currentObj.type = typeMatch[1]; continue; }
        
        const catMatch = trimmed.match(/^category:\s*"([^"]+)"/);
        if (catMatch) { currentObj.category = catMatch[1]; continue; }
        
        const powerMatch = trimmed.match(/^basePower:\s*(\d+)/);
        if (powerMatch) { currentObj.power = parseInt(powerMatch[1]); continue; }
        
        const accMatch = trimmed.match(/^accuracy:\s*(\d+|true|false)/);
        if (accMatch) {
            const v = accMatch[1];
            currentObj.accuracy = v === 'true' ? -1 : v === 'false' ? 0 : parseInt(v);
            continue;
        }
        
        const ppMatch = trimmed.match(/^pp:\s*(\d+)/);
        if (ppMatch) { currentObj.pp = parseInt(ppMatch[1]); continue; }
        
        const priMatch = trimmed.match(/^priority:\s*(-?\d+)/);
        if (priMatch) { currentObj.priority = parseInt(priMatch[1]); continue; }
        
        const targetMatch = trimmed.match(/^target:\s*"([^"]+)"/);
        if (targetMatch) { currentObj.target = targetMatch[1]; continue; }
        
        const descMatch = trimmed.match(/^shortDesc:\s*"([^"]+)"/);
        if (descMatch) { currentObj.description = descMatch[1]; continue; }
    }
    
    return moves;
}

// ─── Type Chart Parser ────────────────────────────────────────────
function parseTypechart(tsContent) {
    const chart = {};
    
    let content = tsContent
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*$/gm, '');
    
    const lines = content.split('\n');
    let currentType = null;
    let currentDmg = {};
    let depth = 0;
    let inType = false;
    let inDmg = false;
    let dmgDepth = 0;
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        if (!inType && /^\w+:\s*\{/.test(trimmed)) {
            currentType = trimmed.split(':')[0].trim();
            currentDmg = {};
            depth = 1;
            inType = true;
            continue;
        }
        
        if (!inType) continue;
        
        // Check for damageTaken block
        if (trimmed === 'damageTaken: {') {
            inDmg = true;
            dmgDepth = 1;
            continue;
        }
        
        if (inDmg) {
            for (const ch of trimmed) {
                if (ch === '{') dmgDepth++;
                if (ch === '}') dmgDepth--;
            }
            
            if (dmgDepth <= 0) {
                inDmg = false;
                continue;
            }
            
            // Parse damage entries: Normal: 0, Fire: 2, etc.
            const dmgMatch = trimmed.match(/(\w+):\s*(\d+)/);
            if (dmgMatch) {
                const target = dmgMatch[1];
                const value = parseInt(dmgMatch[2]);
                // 0 = immune, 1 = normal, 2 = super effective, 3 = resist (0.5), 4 = immune (0)
                // Actually in Showdown: 0 = immune, 1 = normal, 2 = super effective, 3 = 0.5x, 4 = 0x
                // But the actual values are: 0 = immune, 1 = normal, 2 = 2x, 3 = 0.5x
                currentDmg[target] = value;
            }
            continue;
        }
        
        for (const ch of trimmed) {
            if (ch === '{') depth++;
            if (ch === '}') depth--;
        }
        
        if (depth <= 0) {
            if (currentType) {
                chart[currentType] = currentDmg;
            }
            currentType = null;
            currentDmg = {};
            inType = false;
            continue;
        }
    }
    
    return chart;
}

// ─── Main ─────────────────────────────────────────────────────────
try {
    // Parse Pokedex
    console.log('Parsing pokedex.ts...');
    const pokedexContent = fs.readFileSync(path.join(RAW_DIR, 'pokedex.ts'), 'utf-8');
    const pokedex = parsePokedex(pokedexContent);
    console.log(`  Found ${Object.keys(pokedex).length} Pokemon`);
    fs.writeFileSync(path.join(DATA_DIR, 'pokedex.json'), JSON.stringify(pokedex, null, 2));
    
    // Parse Moves
    console.log('Parsing moves.ts...');
    const movesContent = fs.readFileSync(path.join(RAW_DIR, 'moves.ts'), 'utf-8');
    const moves = parseMoves(movesContent);
    console.log(`  Found ${Object.keys(moves).length} moves`);
    fs.writeFileSync(path.join(DATA_DIR, 'moves.json'), JSON.stringify(moves, null, 2));
    
    // Parse Typechart
    console.log('Parsing typechart.ts...');
    const typechartContent = fs.readFileSync(path.join(RAW_DIR, 'typechart.ts'), 'utf-8');
    const typechart = parseTypechart(typechartContent);
    console.log(`  Found ${Object.keys(typechart).length} types`);
    fs.writeFileSync(path.join(DATA_DIR, 'typechart.json'), JSON.stringify(typechart, null, 2));
    
    console.log('\nDone! Check data/ directory.');
    
    // Quick stats
    const stdPokemon = Object.values(pokedex).filter(p => !p.forme || p.forme === 'Base');
    console.log(`\nStats:`);
    console.log(`  Total Pokemon: ${Object.keys(pokedex).length}`);
    console.log(`  Base forms: ${stdPokemon.length}`);
    console.log(`  Total moves: ${Object.keys(moves).length}`);
    console.log(`  Types: ${Object.keys(typechart).length}`);
    
} catch (e) {
    console.error('Error:', e.message);
    process.exit(1);
}
