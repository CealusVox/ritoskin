'''
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The rights go to scarlet and nylish.
Contact discord: nylish.me
'''

import os
import subprocess
import shutil

def write_config_info(skin_name: str, file):
    import json
    config_info = {
        "Author": "scarlet 🐼 & nylish & kobzar",
        "Description": "Made with 💖",
        "Heart": "",
        "Name": skin_name,
        "Version": "1.0.0"
    }
    json.dump(config_info, file, indent=4)

def convert_to_wad(input_folder, exe_path, wad_name):
    root_dir = os.getcwd()

    try:
        # Construct and run command
        command = f'"{exe_path}" "{input_folder}"'
        result = subprocess.run(command,
                              check=True,
                              shell=True,
                              capture_output=True,
                              text=True)

        print(f"Converter output: {result.stdout}")
        if result.stderr:
            print(f"Converter errors: {result.stderr}")

        # Check possible wad file locations including root
        possible_paths = [
            os.path.join(root_dir, f"{wad_name}.wad"),
            os.path.join(root_dir, f"{wad_name}.wad.client"),
            os.path.join(input_folder, f"{wad_name}.wad"),
            os.path.join(input_folder, f"{wad_name}.wad.client"),
        ]

        for wad_path in possible_paths:
            if os.path.exists(wad_path):
                print(f"Found WAD file at: {wad_path}")
                return wad_path

        raise Exception(f"WAD file not found in any expected location: {possible_paths}")

    except subprocess.CalledProcessError as e:
        print(f"Converter error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Errors: {e.stderr}")
        return None

def create_structure(skin_name, wad_path):
    """Create folder structure and move WAD file"""
    root_dir = os.getcwd()
    target_dir = os.path.join(root_dir)
    wad_dir = os.path.join(target_dir, "WAD")
    meta_dir = os.path.join(target_dir, "META")

    # Create directories
    os.makedirs(wad_dir, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)

    # Move WAD file, handling .wad.client extension
    target_path = os.path.join(wad_dir, os.path.basename(wad_path))
    if target_path.endswith('.wad.client'):
        new_target_path = os.path.join(wad_dir, os.path.basename(wad_path).capitalize())
        shutil.move(wad_path, new_target_path)
    else:
        shutil.move(wad_path, target_path)
    # print(f"Moved WAD file to: {target_path}")

    # Create config file
    with open(os.path.join(meta_dir, 'config.json'), 'w') as config:
        write_config_info(skin_name, config)

def create_zip_folder(WAD_FOLDER, META_FOLDER, skin_name: str):
    import zipfile
    with zipfile.ZipFile(skin_name + '.zip', 'w') as zipf:
        for folder_name in [WAD_FOLDER, META_FOLDER]:
            for root, dirs, files in os.walk(folder_name):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.join(folder_name, '..'))
                    zipf.write(file_path, arcname)
        print(f"Created zip file '{skin_name}.zip' with META and WAD folders.")

def main():
    # Find the only folder in the current directory
    current_directory = os.getcwd()
    folders = [f for f in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, f))]
    if len(folders) != 1:
        raise Exception("There should be exactly one folder in the current directory.")
    input_folder = os.path.join(current_directory, folders[0])
    exe_path = "league-wad-packer.exe"
    skin_name = f"{folders[0]}"

    # Convert to WAD
    wad_path = convert_to_wad(input_folder, exe_path, skin_name)
    if wad_path:
        create_structure(skin_name, wad_path)
        print("Folder structure created successfully.")
    else:
        print("Conversion failed, folder structure not created.")

    WAD_FOLDER = "WAD"
    META_FOLDER = "META"
    create_zip_folder(WAD_FOLDER, META_FOLDER, skin_name)

    # Remove WAD and META folders
    shutil.rmtree(WAD_FOLDER)
    shutil.rmtree(META_FOLDER)
    print(f"Removed folders '{WAD_FOLDER}' and '{META_FOLDER}'.")

    print("Done!")

if __name__ == "__main__":
    main()
