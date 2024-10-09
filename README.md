# RitoSkin - A Tool for Custom Skins in League of Legends
- Some of the source code is now available in the `dev` folder.
- The release version will include all necessary files for the project to function correctly.
- If you're cloning the repository, please ensure that you add the `bin` folder to the `resources` directory.

## Table of Contents
- [Preface](#preface)
- [Purpose](#purpose)
- [Functionality](#functionality)
    - [Important Note](#important-note)
- [Usage Instructions](#usage-instructions)
    - [Steps](#steps)
    - [Video Tutorial](#video-tutorial)
- [Resources](#resources)
- [Contact](#contact)

## Preface
- Please ensure you read the entire README before using this project.
- Contributions through pull requests are welcome and highly appreciated.
- If you have any questions or concerns about the project, feel free to contact me.

## Purpose
- Custom skins and skin hacks are prevalent in the community.
- While custom skins are permitted by Riot Games, skin hacks are strictly prohibited.
- Unfortunately, some individuals exploit this by charging for custom skins or selling unauthorized skin hacks on the black market.
- Riot Games should either allow free access to official skins or take stronger measures to prevent unauthorized use.
- Custom artist-made skins can cost up to $300, while official chroma skins may be priced around $200, raising questions of fairness and accessibility.

## Functionality
- This repository contains two projects: one is the source code where all the backend work is done, and the other is the compiled version of the project.
- **`ritoskin`** - A C++ project that uses a scraping method to retrieve skin data, modify it, and convert it to a default skin.
- **`ritoskin_gui`** - The GUI (Graphical User Interface) version of the `ritoskin` project.
- **`ritoskin_extractor`** - A program designed to automate the processing of champion skins. After processing, the skins are neatly organized into a defined folder structure, making it easy to manage and apply modifications.
- **`resources`** - This folder contains the files/scripts necessary for the project to function.

### Important Note
- **`receive_champion_data.py`** - To retrieve the entire set of champion data, we can use the Data Dragon (DDragon) service provided by Riot Games. Each champion has a similar JSON file hosted at a similar URL. However, fetching all champion data requires accessing the specific JSON file for each champion.
- **`scrap_tex_to_dds.py`** - (Patch 14.19) This script was developed as a solution to Riot Games' new method of encrypting the skin icon art (from `.dds` to `.tex`), which made it almost impossible to retrieve the skin icon art from the game files (used to identify the champion skin), causing the icon to appear as a black square in the game.

## Usage Instructions
- Download and extract the project.
- You can also compile the "ritoskin" project using the "ritoskin.cpp" file with the command: `g++ -std=c++17 ritoskin.cpp -o ritoskin -static`

### Steps
1. Use the .wad reader to extract the champion files.
2. Place the extracted files in a folder named after the champion, and move the folder to the "ritoskin" directory.
3. Run the "scrap_tex_to_dds.py" script to retrieve the skin icon art.
4. Execute "ritoskin.exe" to obtain the skin data, modify it, and convert it to a default skin.
5. Use the custom skin loader to load the skin into the game.

### Video Tutorial
- TODO:  A video tutorial will be available soon.

## Resources
- [Obsidian](https://github.com/Crauzer/Obsidian)
- [cslol-manager](https://github.com/LeagueToolkit/cslol-manager)
- [ritobin](https://github.com/moonshadow565/ritobin)

## Contact
- Discord: `nylish.me`

### To-do:
- ~~Implement relative path access for `resources`~~
- Translate the project to Rust
- Port the project to macOS (handle file paths)
- Improve the user-friendly frontend version
- Recreate cslol-manager (Rust)
- ritoskin_lol_wildrift (30% wip, Kotlin)
- More features to be announced (TBA)

### Source Code:
- This is a **work in progress (WIP)** project.
- The codebase is somewhat messy at the moment (C++, Rust, C3, Lua).
- However, the available `.exe` files are stable and reliable.
- Feel free to use it at your own discretion!
