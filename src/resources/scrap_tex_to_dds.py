import os
import shutil

def find_skin_numbers(hud_folder, champion_folder):
    skin_numbers = []
    for file in os.listdir(hud_folder):
        if file.startswith(f"{champion_folder}_circle_") and file.endswith(".tex"):
            num = file.split('_')[2].split('.')[0]
            # Add a zero in front of single-digit numbers
            num = num.zfill(2)
            skin_numbers.append(num)
    return skin_numbers

def copy_splash_art(skins_folder, skin_numbers, output_folder, champion_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for num in skin_numbers:
        skin_folder = os.path.join(skins_folder, f"skin{num}")
        splash_art_file = f"{champion_folder}loadscreen_{str(int(num))}.dds"
        splash_art_path = os.path.join(skin_folder, splash_art_file)

        # Check for the primary splash art file
        if os.path.exists(splash_art_path):
            shutil.copy(splash_art_path, os.path.join(output_folder, splash_art_file))
            print(f"Copied: {splash_art_file} to {output_folder}")
        else:
            print(f"Could not find splash art for {champion_folder}_{num}")

        # Check for the secondary splash art file
        secondary_splash_art_file = f"{champion_folder}loadscreen_{str(int(num))}.skins_{champion_folder}_skin{num}.dds"
        secondary_splash_art_path = os.path.join(skin_folder, secondary_splash_art_file)

        if os.path.exists(secondary_splash_art_path):
            shutil.copy(secondary_splash_art_path, os.path.join(output_folder, secondary_splash_art_file))
            print(f"Copied: {secondary_splash_art_file}")

def main():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)
    ritoskin_gui_directory = os.path.join(parent_directory, "ritoskin_gui")

    folders = [folder for folder in next(os.walk(ritoskin_gui_directory))[1] if folder != "resources"]
    if not folders:
        raise Exception("No valid champion folder found\n Please make sure the folder name is the same as the champion name")
    champion_folder = folders[0]

    hud_folder = os.path.join(ritoskin_gui_directory, champion_folder, "assets", "characters", champion_folder, "hud")
    skins_folder = os.path.join(ritoskin_gui_directory, champion_folder, "assets", "characters", champion_folder, "skins")
    output_folder = os.path.join(ritoskin_gui_directory, "images")

    print(f"Champion folder detected: {champion_folder}")
    print(f"Hud folder: {hud_folder}")
    print(f"Skins folder: {skins_folder}")

    skin_numbers = find_skin_numbers(hud_folder, champion_folder)

    copy_splash_art(skins_folder, skin_numbers, output_folder, champion_folder)

if __name__ == "__main__":
    main()
