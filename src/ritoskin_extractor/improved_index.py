import os
import sys
import json
import re
import requests
import subprocess
import shutil
from pathlib import Path
import logging
from zipfile import ZipFile

# Constants
GAME_PATH = Path(r"V:\Riot Games\League of Legends\Game")
MOD_TOOLS_EXE = "mod-tools.exe"
CHAMPION_NAME_MAP = {
    "drmundo": "DrMundo",
    'missfortune': 'MissFortune',
    'aurelionsol': 'AurelionSol',
    'jarvaniv': 'JarvanIV',
    'kogmaw': 'KogMaw',
    'reksai': 'RekSai',
    'twistedfate': 'TwistedFate',
    'xinzhao': 'XinZhao',
    'tahmkench': 'TahmKench',
    # add more if needed
}

# Add the resources folder to the system path
script_dir = Path(__file__).parent.absolute()
resources_dir = script_dir.parent / 'resources'
sys.path.append(str(resources_dir))

from receive_champion_data import get_latest_version

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SkinExtractor:
    def __init__(self):
        self.script_dir = script_dir
        self.champions_dir = self.script_dir / "process_champions"
        self.output_dir = self.script_dir / "output"
        self.mod_tools_path = self.script_dir / MOD_TOOLS_EXE
        self.game_path = GAME_PATH
        self.version = get_latest_version()
        
        self._ensure_mod_tools_exists()
        self.output_dir.mkdir(exist_ok=True)

    def _ensure_mod_tools_exists(self):
        if not self.mod_tools_path.exists():
            raise FileNotFoundError(f"{MOD_TOOLS_EXE} not found at: {self.mod_tools_path}")

    def get_champion_output_dir(self, champion_name: str) -> Path:
        """Create and return champion-specific output directory."""
        champion_dir = self.output_dir / champion_name
        champion_dir.mkdir(exist_ok=True)
        return champion_dir

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

    def zip_skin_folder(self, folder_path: Path, champion_name: str) -> Path:
        """Zip the skin folder and delete the original folder."""
        try:
            champion_output_dir = self.get_champion_output_dir(champion_name)
            zip_path = champion_output_dir / f"{folder_path.name}.fantome"
            
            if zip_path.exists():
                zip_path.unlink()
            
            with ZipFile(zip_path, 'w') as zipf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(folder_path)
                        zipf.write(file_path, arcname)
            
            shutil.rmtree(folder_path)
            logger.info(f"Created zip file: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating zip file: {e}")
            raise

    def download_champion_data(self, champion_id: int) -> dict:
        """Download champion data from Community Dragon."""
        url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champion_id}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading data for champion ID {champion_id}: {e}")
            return None

    def get_champion_id(self, champion_name: str) -> int:
        """Get the champion ID from the champion name."""
        url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            champions = response.json()
            normalized_name = champion_name.lower().replace(" ", "")
            
            for champion in champions:
                if champion["alias"].lower() == normalized_name:
                    return champion["id"]
            
            logger.error(f"Champion ID not found for {champion_name}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching champion summary: {e}")
            return None

    def find_data_folder(self, base_path: Path) -> Path:
        """Find the data folder in the given path."""
        for path in base_path.rglob('data'):
            if path.is_dir():
                return path
        return None

    def create_info_json(self, dst_path: Path, skin_name: str):
        """Create info.json file for the skin."""
        info = {
            "Author": "Kobzar & Nylish",
            "Description": "Imported using RitoSkin",
            "Name": skin_name,
            "Version": "1.0"
        }
        
        meta_folder = dst_path / "META"
        meta_folder.mkdir(exist_ok=True)
        
        with open(meta_folder / "info.json", "w") as f:
            json.dump(info, f)
        
        logger.info(f"Created info.json for {skin_name}")

    def compact_to_fantome(self, champion_folder: Path, skin_name: str, champion_name: str) -> bool:
        """Convert champion skin files to fantome format and create zip."""
        try:
            skin_name = self.sanitize_filename(skin_name)
            temp_skin_folder = self.output_dir / "temp" / skin_name
            temp_skin_folder.parent.mkdir(exist_ok=True)
            temp_skin_folder.mkdir(exist_ok=True)
            
            self.create_info_json(temp_skin_folder, skin_name)
            
            command = [
                str(self.mod_tools_path),
                'addwad',
                str(champion_folder.parent),
                str(temp_skin_folder),
                f'--game:{self.game_path}',
                '--noTFT',
                '--removeUNK'
            ]
            
            logger.info(f"Executing command: {' '.join(command)}")
            
            original_dir = os.getcwd()
            os.chdir(self.mod_tools_path.parent)
            
            try:
                result = subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                logger.info(f"Command output: {result.stdout}")
            finally:
                os.chdir(original_dir)
            
            zip_path = self.zip_skin_folder(temp_skin_folder, champion_name)
            logger.info(f"Successfully created skin package: {zip_path}")
            
            temp_dir = self.output_dir / "temp"
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing mod-tools: {e}")
            logger.error(f"Standard output: {e.stdout}")
            logger.error(f"Standard error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def process_champion_skins(self, champion_name: str):
        """Process all skins for a given champion."""
        champion_id = self.get_champion_id(champion_name)
        if not champion_id:
            logger.error(f"Champion ID not found for {champion_name}")
            return

        champion_data = self.download_champion_data(champion_id)
        if not champion_data:
            logger.error(f"Failed to download data for champion ID {champion_id}")
            return

        skins = champion_data["skins"]
        skin_mapping = {str(skin["id"]): skin["name"] for skin in skins}
        for skin in skins:
            if "chromas" in skin:
                for idx, chroma in enumerate(skin["chromas"], start=1):
                    chroma_name = f"{chroma['name']} {idx}"
                    skin_mapping[str(chroma["id"])] = chroma_name

        logger.info(f"Found skins: {skin_mapping}")

        base_path = self.champions_dir / champion_name / "skins_extracted"
        if not base_path.exists():
            logger.error(f"Error: Folder for champion {champion_name} not found at {base_path}")
            return

        for folder in base_path.iterdir():
            if folder.is_dir() and folder.name.isdigit():
                skin_id_suffix = folder.name.zfill(3)
                skin_id = f"{champion_id}{skin_id_suffix}"
                if skin_id in skin_mapping:
                    skin_name = skin_mapping[skin_id]
                    data_folder = self.find_data_folder(folder)
                    
                    if data_folder:
                        logger.info(f"Processing skin: {skin_name}")
                        self.compact_to_fantome(data_folder, skin_name, champion_name)
                    else:
                        logger.warning(f"No data folder found in {folder.name}")
                else:
                    logger.warning(f"Folder {folder.name} does not match any known skin ID. Expected ID: {skin_id}")

def main():
    try:
        extractor = SkinExtractor()
        champion_folders = [f for f in extractor.champions_dir.iterdir() if f.is_dir() and f.name != "output"]
        
        if not champion_folders:
            logger.error("No champion folders found!")
            return
        
        for champion_folder in champion_folders:
            folder_name = champion_folder.name.lower()
            champion_name = CHAMPION_NAME_MAP.get(folder_name, folder_name.capitalize())
            logger.info(f"Processing champion: {champion_name}")
            
            extractor.process_champion_skins(champion_name)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()