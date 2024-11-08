import os
import requests

API_URL = "https://api.github.com/repos/CommunityDragon/Data/contents/hashes/lol"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEST_DIR = os.path.join(ROOT_DIR, 'resources', 'bin', 'hashes')

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    local_filename = url.split('/')[-1]
    local_filepath = os.path.join(dest_folder, local_filename)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filepath

def get_files_list(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    files = response.json()
    return [file['download_url'] for file in files if file['type'] == 'file']

def update_hashes():
    files_to_download = get_files_list(API_URL)
    for file_url in files_to_download:
        print(f"Downloading {file_url}...")
        download_file(file_url, DEST_DIR)
        print(f"Downloaded {file_url.split('/')[-1]} to {DEST_DIR}")

if __name__ == "__main__":
    update_hashes()
