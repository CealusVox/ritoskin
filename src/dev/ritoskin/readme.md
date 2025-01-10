You will find all tutorials and tools to help you get started with RitoSkin.

## Getting Started
To get started with RitoSkin, you will need to install the following dependencies:
- gcc/g++
- cmake
- Python 3.6 or higher
- Pip

## Installation
To compile RitoSkin, you will need to run the following command inside `dev/ritoskin`
- mkdir build && cd build
- cmake ..
- cmake --build .

For release, you will need to run the following command inside `dev/ritoskin`:
- mkdir build && cd build
- cmake -DCMAKE_BUILD_TYPE=Release ..
- cmake --build . --config Release

## Usage

- Go into the build directory (`ritoskin/debug/ritoskin.exe`);
- Copy the `ritoskin.exe` and move it into `ritoskin_extractor` folder;
- Run the python script called `update_hashes.py` to receive\update the hashes;
- In `process_champions` folder, you will need to extract the champions folder from `Obsidian`;
- Run the executable and wait for the process to finish;
- You will find in each champion folder a folder called `skins_extracted` with a bunch of folders containing numbers;
- These numbers are the skin id, and inside each folder, you will find `champion_number` folders;
- Drag and drop the `champion_number` folder into the `cslol-manager` application;
- Test the skin in the game;

- Note: Skin number represents the skin id, and each id correspond to a skin and a chroma;

### Unpack | Compile
- Go into the build directory (`ritoskin/debug/ritoskin.exe`)
- Create a folder named `hashes` in the same directory as the executable;
- `hashes` should contain the following files used for unshash the .bin/.py files;
- Create a folder named `process_champions` in the same directory as the executable;
- `process_champions` should contain the champions folder extracted from `Obsidian`;
- Run the executable and wait for the process to finish;

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/nylish/ritoskin/blob/main/LICENSE)
