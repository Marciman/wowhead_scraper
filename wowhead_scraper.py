# wowhead_scraper.py
import requests
from bs4 import BeautifulSoup
import json
import re
import time

BASE_URL = "https://www.wowhead.com/de/hunter-pets"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

def scrape_pet_page(url):
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pet_data = {}
        
        # Name (Haupttitel)
        name_element = soup.select_one('.heading-size-1')
        pet_data['name'] = name_element.text.strip() if name_element else "N/A"
        
        # Zone (In Zonenbeschreibung oder Karte)
        zone_element = soup.select_one('.location')
        pet_data['zone'] = zone_element.text.strip() if zone_element else "N/A"
        
        # Seltenheit (In den Tags oder Beschreibung)
        rarity_element = soup.select_one('.q')
        pet_data['rarity'] = rarity_element.text.strip() if rarity_element else "Gewöhnlich"
        
        # Familie (z.B. "Geistbestie", "Katzentier", etc.)
        family_element = soup.select_one('a[href*="/de/hunter-pets/family="]')
        pet_data['family'] = family_element.text.strip() if family_element else "N/A"
        
        # Fähigkeiten (Tooltip mit Fähigkeit oder Extra-Block)
        abilities = []
        for ability in soup.select('.listview-cleartext[href*="/de/spell="]'):
            abilities.append(ability.text.strip())
        pet_data['ability'] = ", ".join(abilities) if abilities else "N/A"
        
        # Icon und Model ID (In eingebettetem JS)
        script_content = soup.find('script', string=re.compile('modelViewer.setModel'))
        model_id = re.search(r'modelViewer\.setModel\((\d+)', script_content.string).group(1) if script_content else "N/A"
        pet_data['modelID'] = model_id
        pet_data['icon'] = f"https://wow.zamimg.com/images/wow/icons/large/creatureportrait_{model_id}.jpg"
        
        # Spawn-Koordinaten (z.B. "(31,55)")
        spawn_text = soup.find(string=re.compile(r'\(?\d+[,\.]\d+\)?'))
        pet_data['spawn'] = spawn_text.strip() if spawn_text else "N/A"
        
        # Spawn-Zeit (In Beschreibung oder extra Info, z.B. "6-12h")
        spawn_time = soup.find(string=re.compile(r'\d+[-–]\d+[hH]'))
        pet_data['spawnTime'] = spawn_time.strip() if spawn_time else "N/A"
        
        # Beschreibung (Kurzer Text bei Wowhead)
        description_element = soup.select_one('.wowhead-tooltip .q0')
        pet_data['description'] = description_element.text.strip() if description_element else "N/A"
        
        # Voraussetzungen ("Kann nur gezähmt werden von...")
        req_element = soup.find(string=re.compile(r'Kann nur gezähmt werden von'))
        pet_data['requirements'] = req_element.strip() if req_element else "Keine"
        
        return pet_data
    
    except Exception as e:
        print(f"Fehler beim Scrapen von {url}: {str(e)}")
        return None

def scrape_pet_links():
    try:
        response = requests.get(BASE_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pet_links = []
        for link in soup.select('a.listview-cleartext[href*="/de/npc="]'):
            pet_links.append(f"https://www.wowhead.com{link['href']}")
        
        return list(set(pet_links))  # Duplikate entfernen
    
    except Exception as e:
        print(f"Fehler beim Sammeln der Pet-Links: {str(e)}")
        return []

def main():
    pet_links = scrape_pet_links()
    print(f"{len(pet_links)} Pet-Seiten gefunden")
    
    pets = []
    for i, link in enumerate(pet_links, 1):
        # 1-2 Sekunden Wartezeit zwischen den Anfragen
        if i > 1:
            time.sleep(1.5)
            
        pet_data = scrape_pet_page(link)
        if pet_data:
            pets.append(pet_data)
            print(f"{i}/{len(pet_links)}: {pet_data['name']} gescraped")
    
    with open('wowhead_pets.json', 'w', encoding='utf-8') as f:
        json.dump(pets, f, ensure_ascii=False, indent=2)
    
    print(f"Erfolgreich {len(pets)} Pets gesammelt")

if __name__ == "__main__":
    main()