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

int main() {
    try {
        fs::path current_dir = fs::current_path();
        fs::path champions_folder = current_dir / "process_champions";

        if (!fs::exists(champions_folder) || !fs::is_directory(champions_folder)) {
            std::cout << "'process_champions' was not found in the current directory\n";
            std::cout << "Make sure it exist, or create if necessary!\n";
            return 1;
        }

        fs::path temp_dir = fs::current_path() / "champion_data";
        if (!fs::exists(temp_dir)) {
            fs::create_directories(temp_dir);
            std::cout << "Created /champion_data directory.\n";
        }

        std::cout << "============================================\n";
        std::cout << "RitoSkin Extractor - by Nylish\n";
        std::cout << "Processing champions from folder: " << champions_folder << "\n";
        std::cout << "============================================\n";

        std::string python_command = "python ../resources/receive_champion_data.py";
        int result = std::system(python_command.c_str());
        if (result != 0) {
            std::cout << "Error running receive_champion_data.py\n";
            return 1;
        }

        for (const auto& entry : fs::directory_iterator(champions_folder)) {
            if (fs::is_directory(entry)) {
                process_champion_folder(entry.path());
            }
        }
        std::cout << "============================================\n";
        std::cout << "Process Complete!\n";

    } catch (const std::exception& e) {
        std::cout << "Error [20] " << e.what() << "\n";
        return 1;
    }

    std::cout << "Everything went well, congrats!\n";
    std::cout << "RitoSkin Extractor - by Nylish\n";
    std::cin.ignore();
    std::cin.get();

    return 0;
}

bool load_skin_data(const fs::path& champion_data_file, std::map<int, std::string>& skins) {
    std::ifstream file(champion_data_file);
    if (!file.is_open()) {
        std::cout << "Could not open skin data file: " << champion_data_file << "\n";
        return false;
    }

    json skin_data;
    file >> skin_data;

    for (const auto& skin : skin_data) {
        int skin_num = skin["num"];
        std::string skin_name = skin["name"];
        skins[skin_num] = skin_name;
    }
    return true;
}

void process_champion_folder(const fs::path& champion_folder) {
    std::string champion_name = champion_folder.filename().string();
    std::cout << "Processing champion: " << champion_name << "\n";
    std::cout << "============================================\n";

    fs::path extracted_skins_folder = champion_folder / "skins_extracted";
    fs::create_directories(extracted_skins_folder);

    fs::path characters_folder = champion_folder / "skins";
    fs::path skins_data_dir = fs::current_path() / "champion_data";
    fs::path champion_data_file = skins_data_dir / (champion_name + ".json");

    std::map<int, std::string> skins;
    if (!load_skin_data(champion_data_file, skins)) {
        std::cout << "Skipping renaming for " << champion_name << " due to missing skin data.\n";
        return;
    }

    std::vector<fs::path> skin_files;
    if (fs::exists(characters_folder) && fs::is_directory(characters_folder)) {
        for (const auto& entry : fs::recursive_directory_iterator(characters_folder)) {
            if (entry.path().extension() == ".bin" && entry.path().filename().string().find("skin") == 0) {
                skin_files.push_back(entry.path());
            }
        }
    }

    std::sort(skin_files.begin(), skin_files.end());

    fs::path current_skin_folder;
    for (size_t i = 0; i < skin_files.size(); ++i) {
        if (skins.find(i) != skins.end()) {
            current_skin_folder = extracted_skins_folder / skins[i];
            fs::create_directories(current_skin_folder);
            std::cout << "Created folder for skin: " << skins[i] << "\n";
        }

        fs::path output_folder = current_skin_folder.empty() ? extracted_skins_folder : current_skin_folder;
        
        fs::path numbered_folder = output_folder / std::to_string(i);
        fs::create_directories(numbered_folder);

        process_bin_file(skin_files[i], numbered_folder, champion_name, i);
    }
}

void process_bin_file(const fs::path& bin_file_path, const fs::path& output_folder, const std::string& champion_name, int skin_number) {
    try {
        std::cout << "Convert " << bin_file_path << " in .py...\n";
        convert_bin_to_py(bin_file_path);

        fs::path py_file_path = bin_file_path;
        py_file_path.replace_extension(".py");

        std::cout << "Modify " << py_file_path << "...\n";
        modify_py_file(py_file_path);

        std::cout << "Convert " << py_file_path << " in .bin...\n";
        convert_py_to_bin(py_file_path);

        std::string new_champion_folder_name = champion_name + "_" + std::to_string(skin_number);
        fs::path new_bin_file_path = output_folder / new_champion_folder_name / "data" / "characters" / champion_name / "skins" / "skin0.bin";
        
        fs::create_directories(new_bin_file_path.parent_path());
        fs::rename(bin_file_path, new_bin_file_path);
        std::cout << "File renamed & moved to " << new_bin_file_path << "\n";

        fs::remove(py_file_path);

    } catch (const std::exception& e) {
        std::cout << "Error [21] " << e.what() << "\n";
    }
}

void convert_bin_to_py(const fs::path& file_path) {
    // https://github.com/moonshadow565/ritobin
    std::string command = "..\\resources\\bin\\ritobin_cli.exe \"" + file_path.string() + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        throw std::runtime_error("Error[22]");
    }
}

void modify_py_file(const fs::path& file_path) {
    std::ifstream input_file(file_path);
    if (!input_file.is_open()) {
        throw std::runtime_error("Error[23] " + file_path.string());
    }

    std::ofstream output_file(file_path.string() + ".tmp");
    if (!output_file.is_open()) {
        input_file.close();
        throw std::runtime_error("Error[24]");
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
        std::cout << "Modification not needed " << file_path << "\n";
    }
}

void convert_py_to_bin(const fs::path& file_path) {
    std::string command = "..\\resources\\bin\\ritobin_cli.exe \"" + file_path.string() + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        throw std::runtime_error("Error[25]");
    }
}