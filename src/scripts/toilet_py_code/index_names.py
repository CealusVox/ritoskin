import json
import requests
import shutil
import zipfile
from pathlib import Path
import logging
from typing import List, Tuple, Set
import io

# Set up logging
log_file = "process_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SkinOrganizer:
    def __init__(self, source_dir: str, output_dir: str, cache_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.champion_data = {}
        self.unprocessed_files = set()
        
    def get_champion_data(self, champion_id: str) -> dict:
        """Get detailed champion data including skins and chromas."""
        cache_file = self.cache_dir / f"{champion_id}.json"
        
        # Check if the data is already cached
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # If not cached, request from API
        url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champion_id}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Save the data to cache
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting champion data for ID {champion_id}: {e}")
            return None

    def get_chroma_preview_url(self, champion_id: str, chroma_id: str) -> str:
        """Get the URL for a chroma preview image."""
        return f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-chroma-images/{champion_id}/{chroma_id}.png"
    def modify_zip_info_json(self, zip_path: Path, new_name: str) -> bool:
        """Modify the info.json inside the ZIP file to update the Name parameter."""
        temp_path = zip_path.with_suffix('.temp')
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_read:
                with zipfile.ZipFile(temp_path, 'w') as zip_write:
                    for item in zip_read.infolist():
                        data = zip_read.read(item.filename)
                        
                        if item.filename.endswith('META/info.json'):
                            # Modify JSON content
                            json_data = json.loads(data.decode('utf-8'))
                            json_data['Name'] = new_name
                            modified_data = json.dumps(json_data, indent=2).encode('utf-8')
                            
                            # Create new ZipInfo to preserve metadata
                            new_info = zipfile.ZipInfo(item.filename)
                            new_info.date_time = item.date_time
                            new_info.compress_type = item.compress_type
                            
                            zip_write.writestr(new_info, modified_data)
                        else:
                            zip_write.writestr(item, data)
            
            # Replace original with modified file
            zip_path.unlink()
            temp_path.rename(zip_path)
            return True
            
        except Exception as e:
            logger.error(f"Error modifying ZIP {zip_path}: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False
    def create_chroma_readme(self, champion_dir: Path, champion_id: str, skin_name: str, chromas: List[dict]):
        """Create README.md file with chroma previews using direct CDN links."""
        chroma_dir = champion_dir / "chromas" / skin_name
        chroma_dir.mkdir(parents=True, exist_ok=True)
        readme_path = chroma_dir / "README.md"
        
        content = [
            f"# {skin_name} Chromas\n",  # Single newline after title
            "| Preview | Chroma ID |",
            "|---------|-----------|"
        ]
        
        # Add chroma rows without extra newlines
        for chroma in chromas:
            chroma_id = str(chroma['id'])
            image_url = self.get_chroma_preview_url(champion_id, chroma_id)
            content.append(f"| ![{chroma_id}]({image_url}) | {chroma_id} |")
        
        # Join with single newlines
        readme_content = '\n'.join(content)
        readme_path.write_text(readme_content)
        logger.info(f"Created README for {skin_name} chromas")

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters"""
        
        # Remove other invalid characters for Windows filenames
        invalid_chars = '<>:"/\\|?*'
        
        for char in invalid_chars:
            filename = filename.replace(char, ' ')
        
        # Remove multiple spaces and trim
        while '  ' in filename:
            filename = filename.replace('  ', ' ')
        return filename.strip()

    def process_champion_folder(self, champion_folder: Path) -> Tuple[bool, Set[Path]]:
        champion_id = champion_folder.name
        unprocessed_files = set()
        
        # Index all available files
        available_files = {
            int(f.stem): {
                'path': f,
                'processed': False,
                'reason': None
            } for f in champion_folder.glob("*.fantome")
            if f.stem.isdigit()
        }
        
        if not available_files:
            logger.warning(f"No .fantome files found in {champion_folder}")
            return True, unprocessed_files
    
        # Get champion data
        champion_data = self.get_champion_data(champion_id)
        if not champion_data or 'skins' not in champion_data:
            reason = "Invalid or missing champion data"
            logger.error(f"{reason} for champion ID {champion_id}")
            unprocessed_files.update(f['path'] for f in available_files.values())
            return False, unprocessed_files
    
        champion_name = champion_data.get('name', champion_id)
        logger.info(f"\nProcessing champion: {champion_name} (ID: {champion_id})")
    
        # Create mapping using actual skin/chroma IDs
        expected_files = {}
        skin_chromas = {}  # Track chromas for each skin
        
        for skin in champion_data['skins']:
            skin_id = str(skin['id'])
            skin_num = int(skin_id[-3:]) if len(skin_id) >= 3 else int(skin_id)
            skin_name = self.sanitize_filename(skin['name'])
            
            expected_files[skin_num] = {
                'type': 'skin',
                'name': skin_name,
                'id': skin_id
            }
            
            # Initialize chromas list for this skin
            if 'chromas' in skin:
                skin_chromas[skin_name] = skin['chromas']
                for chroma in skin['chromas']:
                    chroma_id = str(chroma['id'])
                    chroma_num = int(chroma_id[-3:]) if len(chroma_id) >= 3 else int(chroma_id)
                    
                    expected_files[chroma_num] = {
                        'type': 'chroma',
                        'skin_name': skin_name,
                        'chroma_id': chroma_id
                    }
    
        # Process files
        champion_dir = self.output_dir / self.sanitize_filename(champion_name)
        champion_dir.mkdir(parents=True, exist_ok=True)
        (champion_dir / "chromas").mkdir(exist_ok=True)

        processed_chromas = {}

        # Compare and process
        for file_num, file_data in available_files.items():
            try:
                if file_num not in expected_files:
                    file_data['reason'] = f"No matching skin/chroma found for file number {file_num}"
                    continue
                
                expected = expected_files[file_num]
                
                if expected['type'] == 'skin':
                    skin_name = expected['name']
                    output_path = champion_dir / f"{skin_name}.zip"
                    shutil.copy2(file_data['path'], output_path)
                    
                    # Modify the ZIP file to update skin name
                    if self.modify_zip_info_json(output_path, skin_name):
                        file_data['processed'] = True
                        logger.info(f"Processed and renamed skin: {skin_name}")
                    
                elif expected['type'] == 'chroma':
                    skin_name = expected['skin_name']
                    chroma_id = expected['chroma_id']
                    
                    chroma_dir = champion_dir / "chromas" / skin_name
                    chroma_dir.mkdir(parents=True, exist_ok=True)
                    chroma_path = chroma_dir / f"{skin_name} {chroma_id}.zip"
                    shutil.copy2(file_data['path'], chroma_path)
                    
                    # Modify the ZIP file to update chroma name
                    if self.modify_zip_info_json(chroma_path, f"{skin_name} {chroma_id}"):
                        file_data['processed'] = True
                        if skin_name not in processed_chromas:
                            processed_chromas[skin_name] = []
                        processed_chromas[skin_name].append(chroma_id)
                        logger.info(f"Processed and renamed chroma: {skin_name} {chroma_id}")
                    
            except Exception as e:
                file_data['reason'] = f"Error during processing: {str(e)}"
                logger.error(f"Error processing file {file_num}: {str(e)}", exc_info=True)
    
        # Create README files for chromas
        for skin_name, chromas in skin_chromas.items():
            # Only create README if we processed any chromas for this skin
            if skin_name in processed_chromas and processed_chromas[skin_name]:
                self.create_chroma_readme(champion_dir, champion_id, skin_name, chromas)
    
        # Log processing summary
        logger.info(f"\nProcessing summary for champion {champion_name}:")
        for file_num in sorted(available_files.keys()):
            file_data = available_files[file_num]
            if not file_data['processed']:
                logger.warning(f"File {file_num} not processed: {file_data['reason']}")
                unprocessed_files.add(file_data['path'])
                
        return True, unprocessed_files

def main():
    # Replace these paths with your actual paths
    source_dir = Path("output")
    output_dir = Path("organized_skins")
    cache_dir = Path("cache")
    
    # Get all champion folders
    champion_folders = [f for f in source_dir.iterdir() if f.is_dir() and f.name.isdigit()]
    
    logger.info(f"Starting to process all champions")
    
    total_processed = 0
    all_unprocessed_files = set()
    
    organizer = SkinOrganizer(source_dir, output_dir, cache_dir)
    
    for folder in champion_folders:
        try:
            success, unprocessed_files = organizer.process_champion_folder(folder)
            if success:
                total_processed += 1
            all_unprocessed_files.update(unprocessed_files)
        except Exception as e:
            logger.error(f"Error processing champion folder {folder}: {str(e)}")
            # If there's an error processing the folder, add all its fantome files to unprocessed
            all_unprocessed_files.update(f for f in folder.glob("*.fantome"))
    
    # Write unprocessed files to a text file
    if all_unprocessed_files:
        unprocessed_path = output_dir / "unprocessed_files.txt"
        with open(unprocessed_path, 'w') as f:
            for file_path in sorted(all_unprocessed_files):
                f.write(f"{file_path}\n")
        logger.info(f"Wrote list of {len(all_unprocessed_files)} unprocessed files to {unprocessed_path}")
    
    logger.info(f"Finished processing. Organized {total_processed} champions")

if __name__ == "__main__":
    main()