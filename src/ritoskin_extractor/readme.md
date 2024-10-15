# RitoSkin Extractor

## Overview
**RitoSkin Extractor** is a program designed to automate the processing of champion skins for *League of Legends*. It handles `.bin` files associated with skins, converts them to `.py` format for modification, and then reconverts them back to `.bin`. After processing, the skins are neatly organized into a defined folder structure, making it easy to manage and apply modifications.

### What does it do?
- The program recursively scans the `[champion]/skins/skin*.bin` folder to locate all files named `skin*.bin`.
- It processes these files, extracting all skins and chromas of a champion.
- The skins are then moved into a new directory structure based on the champion’s name and skin number.

### How to use it?
1. Use **Obsidian** to extract `.wad` files of a champion (or multiple champions).
2. Place the `champion` or `champions` folder containing your extracted data in the same directory as the executable.
3. The program will process each champion in the `process_champions` folder and extract the skins into a new folder called `skins_extracted` within each champion’s directory.
4. After running, check the `skins_extracted` folder for each champion to find the processed skins, organized by number.

## Error Reference:
- **20**: Related to the champion folder.
- **21**: Related to processing the `.bin` file.
- **22**: Related to converting `.bin` to `.py`.
- **23**: Related to the `.py` file path.
- **24**: Related to the temporary `.py` file.
- **25**: Related to converting `.py` back to `.bin`.

### Reference:
- [nlohmann](https://github.com/nlohmann/json)
- [ritobin](https://github.com/moonshadow565/ritobin)

## Tutorial
- [ritoskin-extractor](https://www.youtube.com/playlist?list=PLmfRqBUHwQjJtdoNPbyCKIGC9F4Hog7ov)

