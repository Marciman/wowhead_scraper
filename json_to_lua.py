# json_to_lua.py
import json

def convert_to_lua():
    with open('wowhead_pets.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lua_output = """-- Automatisch generierte Pet-Daten von Wowhead
HRT_Data = {
    pets = {
"""
    
    for pet in data:
        lua_output += f"""        {{
            name = "{pet['name']}",
            zone = "{pet['zone']}",
            rarity = "{pet['rarity']}",
            family = "{pet['family']}",
            ability = "{pet['ability']}",
            icon = "{pet['icon']}",
            modelID = {pet['modelID']},
            spawn = "{pet['spawn']}","""
            
        if 'spawnTime' in pet:
            lua_output += f"""
            spawnTime = "{pet['spawnTime']}","""
            
        lua_output += f"""
            description = "{pet['description']}",
            requirements = "{pet['requirements']}",
        }},
"""
    
    lua_output += """    }
}
return HRT_Data
"""
    
    with open('HRT_Data.lua', 'w', encoding='utf-8') as f:
        f.write(lua_output)

if __name__ == "__main__":
    convert_to_lua()