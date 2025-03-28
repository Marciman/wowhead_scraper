# json_to_lua.py
import json

def convert_to_lua():
    with open('wowhead_pets.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lua_output = """-- Auto-generierte Pet-Daten von Wowhead
HRT_Data = {
    pets = {
"""
    
    for pet in data:
        lua_output += f"""        {{
            id = {pet['id']},
            name = "{pet['name']}",
            family = "{pet['family']}",
            icon = "{pet['icon']}",
            level = "{pet['level']}",
            abilities = "{pet['abilities']}",
            diet = "{pet['diet']}",
            exotic = {"true" if pet['exotic'] else "false"},
            popularity = {pet['popularity']},
            zone = "{pet['zone']}",
            spawn = "{pet['spawn']}"
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
