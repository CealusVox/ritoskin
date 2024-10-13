/*
 * Copyright (c) 2024 nylish
 * All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "ritoskin_extractor.h"
#include <regex>
#include <map>

bool is_valid_skin_file(const std::string& filename) {
    std::regex pattern(R"(skin\d+\.bin)");
    return std::regex_match(filename, pattern);
}
/*
    TODO: DataDragon is Case Sensitive and has some issues related with champions name.
    For example: Dr Mundo is "DrMundo" in DataDragon, but this program 
    returns as drmundo and my python reads exacly the folder name.

    I've tried to capitalize the first letter and works at most of the cases
    except for some champions that has this issue.

    We probably need a dictionary to match with the Data Dragon sensitive case names.
*/
int main() {
    try {
        fs::path current_dir = fs::current_path();
        fs::path champions_folder = current_dir / "process_champions";

        if (!fs::exists(champions_folder) || !fs::is_directory(champions_folder)) {
            std::cout << "'process_champions' was not found in the current directory\n";
            std::cout << "Make sure it exists, or create if necessary!\n";
            return 1;
        }

        std::cout << "============================================\n";
        std::cout << "RitoSkin Extractor - by Nylish\n";
        std::cout << "Processing champions from folder: " << champions_folder << "\n";
        std::cout << "============================================\n";

        for (const auto& entry : fs::directory_iterator(champions_folder)) {
            if (fs::is_directory(entry)) {
                process_champion_folder(entry.path());
            }
        }
        std::cout << "============================================\n";
        std::cout << "Process Complete!\n";

    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << "\n";
        return 1;
    }

    std::cout << "Everything went well, congrats!\n";
    std::cout << "RitoSkin Extractor - by Nylish\n";
    std::cin.ignore();
    std::cin.get();

    return 0;
}

void process_champion_folder(const fs::path& champion_folder) {
    std::string champion_name = champion_folder.filename().string();
    std::cout << "Processing champion: " << champion_name << "\n";
    std::cout << "============================================\n";

    fs::path extracted_skins_folder = champion_folder / "skins_extracted";
    fs::create_directories(extracted_skins_folder);

    fs::path characters_folder = champion_folder / "skins";

    std::map<int, fs::path> skin_map;
    if (fs::exists(characters_folder) && fs::is_directory(characters_folder)) {
        for (const auto& entry : fs::recursive_directory_iterator(characters_folder)) {
            if (entry.path().extension() == ".bin" && entry.path().filename().string().find("skin") == 0) {
                std::string filename = entry.path().filename().string();
                if (is_valid_skin_file(filename)) {
                    int skin_number = std::stoi(filename.substr(4, filename.find('.') - 4));
                    skin_map[skin_number] = entry.path();
                } else {
                    std::cout << "Warning: Invalid skin file name format: " << filename << std::endl;
                }
            }
        }
    }

    std::cout << "Found " << skin_map.size() << " valid skin files for " << champion_name << std::endl;
    for (const auto& [number, path] : skin_map) {
        std::cout << "  Skin " << number << ": " << path.filename().string() << std::endl;
    }

    for (const auto& [number, path] : skin_map) {
        fs::path skin_folder = extracted_skins_folder / std::to_string(number);
        fs::create_directories(skin_folder);
        process_bin_file(path, skin_folder, number);
    }
}

void process_bin_file(const fs::path& bin_file_path, const fs::path& output_folder, int skin_number) {
    try {
        std::string filename = bin_file_path.filename().string();
        int file_skin_number = std::stoi(filename.substr(4, filename.find('.') - 4));
        
        if (file_skin_number != skin_number) {
            std::cout << "Warning: Mismatch in skin numbering for " << filename 
                      << ". File suggests " << file_skin_number 
                      << ", but processing as " << skin_number << std::endl;
        }

        convert_bin_to_py(bin_file_path);

        fs::path py_file_path = bin_file_path;
        py_file_path.replace_extension(".py");

        std::cout << "Processing skin " << skin_number << " ...\n";
        modify_py_file(py_file_path);

        convert_py_to_bin(py_file_path);

        std::string champion_name = bin_file_path.parent_path().parent_path().filename().string();
        
        std::string new_champion_folder_name = champion_name + "_" + std::to_string(skin_number);
        fs::path new_folder_structure = output_folder / new_champion_folder_name / "data" / "characters" / champion_name / "skins";
        fs::create_directories(new_folder_structure);

        fs::path new_bin_file_path = new_folder_structure / "skin0.bin";
        fs::rename(bin_file_path, new_bin_file_path);
        std::cout << "File renamed & moved to " << new_bin_file_path << "\n";

        fs::remove(py_file_path);

    } catch (const std::exception& e) {
        std::cout << "Error processing file: " << e.what() << "\n";
    }
}

void convert_bin_to_py(const fs::path& file_path) {
    std::string command = "..\\resources\\bin\\ritobin_cli.exe \"" + file_path.string() + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        throw std::runtime_error("Error converting bin to py");
    }
}

void modify_py_file(const fs::path& file_path) {
    std::ifstream input_file(file_path);
    if (!input_file.is_open()) {
        throw std::runtime_error("Error opening file: " + file_path.string());
    }

    std::ofstream output_file(file_path.string() + ".tmp");
    if (!output_file.is_open()) {
        input_file.close();
        throw std::runtime_error("Error creating temporary file");
    }

    std::string line;
    std::regex skin_data_pattern(R"(("Characters/[^/]+/Skins/Skin)\d+(" *= *SkinCharacterDataProperties *\{))");
    std::regex resource_resolver_pattern(R"(("Characters/[^/]+/Skins/Skin)\d+(/Resources" *= *ResourceResolver *\{))");

    bool modified = false;
    while (std::getline(input_file, line)) {
        std::string modified_line = line;
        if (std::regex_search(line, skin_data_pattern) || std::regex_search(line, resource_resolver_pattern)) {
            modified_line = std::regex_replace(line, std::regex(R"(Skin\d+)"), "Skin0");
            modified = true;
        }
        output_file << modified_line << '\n';
    }

    input_file.close();
    output_file.close();

    if (modified) {
        fs::rename(file_path.string() + ".tmp", file_path);
    } else {
        fs::remove(file_path.string() + ".tmp");
        std::cout << "Modification not needed for " << file_path << "\n";
    }
}

void convert_py_to_bin(const fs::path& file_path) {
    std::string command = "..\\resources\\bin\\ritobin_cli.exe \"" + file_path.string() + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        throw std::runtime_error("Error converting py to bin");
    }
}