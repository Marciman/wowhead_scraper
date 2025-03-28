# wowhead_scraper.py
import requests
import json
import re
from bs4 import BeautifulSoup

BASE_URL = "https://www.wowhead.com/de/pets/tameable"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def extract_pet_data(script_content):
    """Extrahiert die vollständige Pet-Liste aus dem JavaScript-Code"""
    match = re.search(r'data: (\[.*?\])', script_content)
    if not match:
        return []
    
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

def get_spell_names(spell_ids):
    """Holt die Namen der Fähigkeiten"""
    # Vereinfachte Version - könnte erweitert werden
    spell_names = []
    for spell_id in spell_ids:
        if spell_id == 16827:   # Beispiel-IDs
            spell_names.append("Wiederbelebung des Begleiters")
        elif spell_id == 160065:
            spell_names.append("Knurren")
        elif spell_id == 280151:
            spell_names.append("Giftspucke")
    return spell_names

def scrape_pets():
    try:
        response = requests.get(BASE_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Finde das Listview-Script mit den Pet-Daten
        script = soup.find('script', string=re.compile('new Listview'))
        if not script:
            raise ValueError("Listview-Daten nicht gefunden")
        
        pets_data = extract_pet_data(script.string)
        if not pets_data:
            raise ValueError("Keine Pet-Daten extrahiert")
        
        # Zusätzliche Details von jeder Pet-Seite holen
        full_pets = []
        for pet in pets_data[:5]:  # Erstmal nur 5 zum Testen
            pet_details = {
                "id": pet["id"],
                "name": pet["name"],
                "family": get_family_name(pet["type"]),
                "icon": f"https://wow.zamimg.com/images/wow/icons/large/{pet['icon']}.jpg",
                "level": f"{pet['minLevel']}-{pet['maxLevel']}",
                "abilities": ", ".join(get_spell_names(pet.get("spells", []))),
                "diet": get_diet_name(pet.get("diet", 0)),
                "exotic": bool(pet.get("exotic", 0)),
                "popularity": pet.get("popularity", 0)
            }
            
            # Hole Zonen-Info von der Detailseite
            zone_info = get_zone_info(pet["id"])
            pet_details.update(zone_info)
            
            full_pets.append(pet_details)
        
        return full_pets
    
    except Exception as e:
        print(f"Fehler beim Scrapen: {str(e)}")
        return []

def get_family_name(family_id):
    """Konvertiert Familien-ID in Namen"""
    families = {
        1: "Wolf", 2: "Aqir", 3: "Spinnentier", 
        # Weitere Familien hier ergänzen
    }
    return families.get(family_id, "Unbekannt")

def get_diet_name(diet_id):
    """Konvertiert Ernährungs-Typ"""
    diets = {
        0: "Keine", 1: "Fleisch", 2: "Fisch", 
        17: "Magie"  # Beispiel für Aqir
    }
    return diets.get(diet_id, "Unbekannt")

def get_zone_info(pet_id):
    """Holt Zonen-Info von der Pet-Detailseite"""
    try:
        url = f"https://www.wowhead.com/de/pet={pet_id}"
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        zone = soup.select_one('.location')
        spawn = soup.find(string=re.compile(r'\(?\d+[,\.]\d+\)?'))
        
        return {
            "zone": zone.text.strip() if zone else "N/A",
            "spawn": spawn.strip() if spawn else "N/A"
        }
    except:
        return {"zone": "N/A", "spawn": "N/A"}

def main():
    pets = scrape_pets()
    with open('wowhead_pets.json', 'w', encoding='utf-8') as f:
        json.dump(pets, f, ensure_ascii=False, indent=2)
    
    print(f"Erfolgreich {len(pets)} Pets gespeichert")

if __name__ == "__main__":
    main()
