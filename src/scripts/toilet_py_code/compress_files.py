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
        self.mod_tools_path = self.script_dir.parent / "resources" /  "cslol" / "mod-tools.exe"
        self.game_path = Path(r"C:\Riot Games\League of Legends\Game")

        # Ensure mod-tools.exe exists
        if not self.mod_tools_path.exists():
            raise FileNotFoundError(f"mod-tools.exe not found at: {self.mod_tools_path}")

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    def get_champion_output_dir(self, champion_id):
        """Create and return champion-specific output directory."""
        champion_dir = self.output_dir / champion_id
        champion_dir.mkdir(exist_ok=True)
        return champion_dir

    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

    def zip_skin_folder(self, folder_path, skin_id, champion_id):
        """
        Zip the skin folder and delete the original folder.
        Places the zip in the champion-specific output directory.
        Returns the path to the created zip file.
        """
        try:
            folder_path = Path(folder_path)
            # Get champion-specific output directory
            champion_output_dir = self.get_champion_output_dir(champion_id)
            zip_path = champion_output_dir / f"{skin_id}.fantome"

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

    def download_champion_data(self):
        """Download all champion data from Data Dragon."""
        url = "https://ddragon.leagueoflegends.com/cdn/14.22.1/data/en_US/champion.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading champion data: {e}")
            return None

    def find_data_folder(self, base_path):
        """Find the data folder in the given path."""
        data_path = Path(base_path)
        for path in data_path.rglob('data'):
            if path.is_dir():
                return path
        return None

    def create_info_json(self, dst_path, skin_id):
        """Create info.json file for the skin."""
        info = {
            "Author": "Kobzar and Nylish",
            "Description": "Imported using RitoSkin",
            "Name": f"Skin {skin_id}",
            "Version": "1.0.0"
        }

        meta_folder = Path(dst_path) / "META"
        meta_folder.mkdir(exist_ok=True)

        with open(meta_folder / "info.json", "w") as f:
            json.dump(info, f)

        logger.info(f"Created info.json for Skin {skin_id}")

    def compact_to_fantome(self, champion_folder, skin_id, champion_id):
        """Convert champion skin files to fantome format and create zip."""
        try:
            # Prepare paths
            champion_path = Path(champion_folder).parent
            temp_skin_folder = self.output_dir / "temp" / str(skin_id)
            temp_skin_folder.parent.mkdir(exist_ok=True)
            temp_skin_folder.mkdir(exist_ok=True)

            # Create info.json
            self.create_info_json(temp_skin_folder, skin_id)

            # Prepare command
            command = [
                str(self.mod_tools_path),
                'addwad',
                str(champion_path),
                str(temp_skin_folder),
                '--game:V:\\Riot Games\\League of Legends\\Game',
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
            zip_path = self.zip_skin_folder(temp_skin_folder, skin_id, champion_id)
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

    def process_champion_skins(self, champion_id, champion_name):
        """Process all skins for a given champion."""
        base_path = self.champions_dir / champion_name / "skins_extracted"
        if not base_path.exists():
            logger.error(f"Error: Folder for {champion_name} not found at {base_path}")
            return

        # Process each skin folder
        for folder in base_path.iterdir():
            if folder.is_dir() and folder.name.isdigit():
                skin_id = folder.name
                data_folder = self.find_data_folder(folder)

                if data_folder:
                    logger.info(f"Processing skin ID: {skin_id}")
                    self.compact_to_fantome(data_folder, skin_id, champion_id)
                else:
                    logger.warning(f"No data folder found in {folder.name}")

def main():
    try:
        extractor = SkinExtractor()
        champion_data = extractor.download_champion_data()

        if not champion_data:
            logger.error("Failed to download champion data!")
            return

        champion_folders = [f for f in extractor.champions_dir.iterdir() if f.is_dir() and f.name != "output"]

        if not champion_folders:
            logger.error("No champion folders found!")
            return

        # Create a mapping of champion names to their IDs
        champion_id_map = {champ_data['id']: champ_data['key'] for champ_data in champion_data['data'].values()}

        # Process each champion folder
        for champion_folder in champion_folders:
            champion_name = champion_folder.name
            if champion_name in champion_id_map:
                champion_id = champion_id_map[champion_name]
                logger.info(f"Processing champion: {champion_name} (ID: {champion_id})")
                extractor.process_champion_skins(champion_id, champion_name)
            else:
                logger.warning(f"Champion {champion_name} not found in champion data")

    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()
