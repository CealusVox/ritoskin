import requests
import os
import json

BASE_URL = "https://ddragon.leagueoflegends.com"
VERSIONS_URL = f"{BASE_URL}/api/versions.json"
OUTPUT_DIR = "champion_data"

def create_output_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fetch_json(url):
    response = requests.get(url)
    return response.json()

def get_latest_version():
    versions = fetch_json(VERSIONS_URL)
    return versions[0]

def get_champion_list(version):
    url = f"{BASE_URL}/cdn/{version}/data/en_US/champion.json"
    return fetch_json(url)['data']

def extract_skin_data(champion_json, champion_key):
    return [
        {
            'id': skin['id'],
            'num': skin['num'],
            'name': skin['name']
        }
        for skin in champion_json['data'][champion_key]['skins']
    ]

def save_skin_data(champion_key, skin_data):
    with open(f"{OUTPUT_DIR}/{champion_key}.json", "w", encoding='utf-8') as f:
        json.dump(skin_data, f, indent=4)

def process_champion(champion_key, version):
    url = f"{BASE_URL}/cdn/{version}/data/en_US/champion/{champion_key}.json"
    champion_json = fetch_json(url)
    skin_data = extract_skin_data(champion_json, champion_key)
    save_skin_data(champion_key, skin_data)
    print(f"Extracted skins for {champion_key}")

def main():
    create_output_directory()
    latest_version = get_latest_version()
    print(f"Using latest version: {latest_version}")
    champions_data = get_champion_list(latest_version)
    
    for champion in champions_data.values():
        process_champion(champion['id'], latest_version)
    
    print("All skin data has been extracted!")

if __name__ == "__main__":
    main()