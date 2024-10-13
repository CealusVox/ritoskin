import os
import json
import re
import requests
import subprocess
import shutil
from pathlib import Path
import logging
from zipfile import ZipFile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SkinExtractor:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute() 
        self.champions_dir = self.script_dir / "process_champions"
        self.output_dir = self.script_dir / "output"
        self.mod_tools_path = self.script_dir / "mod-tools.exe"
        self.game_path = Path(r"C:\Riot Games\League of Legends\Game")
        
        # Ensure mod-tools.exe exists
        if not self.mod_tools_path.exists():
            raise FileNotFoundError(f"mod-tools.exe not found at: {self.mod_tools_path}")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    def get_champion_output_dir(self, champion_name):
        """Create and return champion-specific output directory."""
        champion_dir = self.output_dir / champion_name
        champion_dir.mkdir(exist_ok=True)
        return champion_dir

    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

    def zip_skin_folder(self, folder_path, champion_name):
        """
        Zip the skin folder and delete the original folder.
        Places the zip in the champion-specific output directory.
        Returns the path to the created zip file.
        """
        try:
            folder_path = Path(folder_path)
            # Get champion-specific output directory
            champion_output_dir = self.get_champion_output_dir(champion_name)
            zip_path = champion_output_dir / f"{folder_path.name}.fantome"
            
            # Remove existing zip if it exists
            if zip_path.exists():
                zip_path.unlink()
            
            # Create the zip file
            with ZipFile(zip_path, 'w') as zipf:
                # Walk through the directory
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        # Get the full path of the file
                        file_path = Path(root) / file
                        # Get the relative path for the archive
                        arcname = file_path.relative_to(folder_path)
                        # Add file to the zip
                        zipf.write(file_path, arcname)
            
            # Delete the original folder
            shutil.rmtree(folder_path)
            
            logger.info(f"Created zip file: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating zip file: {e}")
            raise

    def download_champion_data(self, champion_name):
        """Download champion data from Data Dragon."""
        url = f"https://ddragon.leagueoflegends.com/cdn/14.20.1/data/en_US/champion/{champion_name}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading data for {champion_name}: {e}")
            return None

    def find_data_folder(self, base_path):
        """Find the data folder in the given path."""
        data_path = Path(base_path)
        for path in data_path.rglob('data'):
            if path.is_dir():
                return path
        return None

    def create_info_json(self, dst_path, skin_name):
        """Create info.json file for the skin."""
        info = {
            "Author": "Kobzar and Nylish",
            "Description": "Imported using RitoSkin",
            "Name": skin_name,
            "Version": "1.0.0"
        }
        
        meta_folder = Path(dst_path) / "META"
        meta_folder.mkdir(exist_ok=True)
        
        with open(meta_folder / "info.json", "w") as f:
            json.dump(info, f)
        
        logger.info(f"Created info.json for {skin_name}")

    def list_directory_contents(self, directory):
        try:
            contents = os.listdir(directory)
            logger.info(f"Contents of {directory}: {contents}")
        except Exception as e:
            logger.error(f"Failed to list contents of {directory}: {e}")

    def compact_to_fantome(self, champion_folder, skin_name, champion_name):
        """Convert champion skin files to fantome format and create zip."""
        try:
            # Prepare paths
            champion_path = Path(champion_folder).parent
            skin_name = self.sanitize_filename(skin_name)
            temp_skin_folder = self.output_dir / "temp" / skin_name
            temp_skin_folder.parent.mkdir(exist_ok=True)
            temp_skin_folder.mkdir(exist_ok=True)
            
            # Create info.json
            self.create_info_json(temp_skin_folder, skin_name)
            
            # Prepare command
            command = [
                str(self.mod_tools_path),
                'addwad',
                str(champion_path),
                str(temp_skin_folder),
                '--game:C:\\Riot Games\\League of Legends\\Game',
                '--noTFT',
                '--removeUNK'
            ]
            
            logger.info(f"Executing command: {' '.join(command)}")
            
            # Execute command
            # Change the working directory to where mod-tools.exe is located
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
                # Change back to the original directory
                os.chdir(original_dir)
            
            # Create zip file in champion-specific directory and delete original folder
            zip_path = self.zip_skin_folder(temp_skin_folder, champion_name)
            logger.info(f"Successfully created skin package: {zip_path}")
            
            # Clean up temp directory if it's empty
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

    def process_champion_skins(self, champion_name):
        """Process all skins for a given champion."""
        base_path = self.champions_dir / champion_name / "skins_extracted"
        if not base_path.exists():
            logger.error(f"Error: Folder for {champion_name} not found at {base_path}")
            return

        # Download champion data
        champion_data = self.download_champion_data(champion_name)
        if not champion_data:
            return

        # Create skin mapping
        skins = champion_data["data"][champion_name]["skins"]
        skin_mapping = {str(skin["num"]): skin["name"] for skin in skins}
        logger.info(f"Found skins: {skin_mapping}")

        # Process each skin folder
        for folder in base_path.iterdir():
            if folder.is_dir() and folder.name.isdigit():
                if folder.name in skin_mapping:
                    skin_name = skin_mapping[folder.name]
                    data_folder = self.find_data_folder(folder)
                    
                    if data_folder:
                        logger.info(f"Processing skin: {skin_name}")
                        self.compact_to_fantome(data_folder, skin_name, champion_name)
                    else:
                        logger.warning(f"No data folder found in {folder.name}")
                else:
                    logger.warning(f"Folder {folder.name} does not match any known skin number")

def main():
    try:
        extractor = SkinExtractor()
        champion_folders = [f for f in extractor.champions_dir.iterdir() if f.is_dir() and f.name != "output"]
        
        if not champion_folders:
            logger.error("No champion folders found!")
            return
            
        
        # iterates for every champion folder
        for champion_folder in champion_folders:
            champion_name = champion_folder.name
            logger.info(f"Processing champion: {champion_name}")
            extractor.process_champion_skins(champion_name)
        
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()