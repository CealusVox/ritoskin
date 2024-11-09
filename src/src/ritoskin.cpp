#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <regex>

namespace fs = std::filesystem;

// Function declarations
void process_bin_file(const fs::path& bin_file_path);
void convert_bin_to_py(const fs::path& file_path);
void modify_py_file(const fs::path& file_path);
void convert_py_to_bin(const fs::path& file_path);
bool find_bin_file(const fs::path& dir, const std::string& filename, fs::path& result);
void process_folder(const fs::path& folder_path, const std::string& bin_file_name);

int main() {
    try {
        // Step 1: Define the current directory
        fs::path current_dir = fs::current_path();

        // Step 2: Find the folder that is not named "resources"
        std::cout << "RitoSkin - by Nylish" << "\n";
        std::cout << "Looking for folders in the current directory...\n";

        std::vector<fs::path> non_resource_folders;
        for (const auto& entry : fs::directory_iterator(current_dir)) {
            if (fs::is_directory(entry) && entry.path().filename() != "resources" && entry.path().filename() != "images") {
                non_resource_folders.push_back(entry.path());
            }
        }

        if (non_resource_folders.empty()) {
            std::cout << "No folder found beside 'resources'. Exiting.\n";
            return 1;
        }

        // Use the first folder found
        fs::path folder_path = non_resource_folders[0];
        std::cout << "Selected folder: \"" << folder_path.filename().string() << "\"\n";

        // Step 3: Check for 'data/characters' folder inside the selected folder
        // Delete "assets" folder if it exists
        fs::path assets_folder = folder_path / "assets";
        if (fs::exists(assets_folder) && fs::is_directory(assets_folder)) {
            std::cout << "Found 'assets' folder at \"" << assets_folder.string() << "\". Deleting...\n";
            fs::remove_all(assets_folder);
            std::cout << "'assets' folder deleted.\n";
        }

        // Delete all files and directories besides "data" folder
        fs::path data_folder = folder_path / "data";
        for (const auto& entry : fs::directory_iterator(folder_path)) {
            if (entry.is_regular_file() || (entry.is_directory() && entry != data_folder)) {
                fs::remove_all(entry.path());
                std::cout << "Deleted all junk files\n";
            }
        }

        fs::path characters_folder = folder_path / "data" / "characters";
        if (!fs::is_directory(characters_folder)) {
            std::cout << "No 'data/characters' folder found inside '" << folder_path.filename().string() << "'. Exiting.\n";
            return 1;
        }

        // Step 4: Get the name of the .bin file from the user
        std::string bin_file_name;
        std::cout << "Type the name of the .bin file you want to process (e.g., skin16.bin): ";
        std::cin >> bin_file_name;

        // Step 5: Define the path to the converter executable
        fs::path converter_path = fs::path("../resources/bin/ritobin_cli.exe");
        if (!fs::exists(converter_path)) {
            std::cout << "Error: Converter not found at \"" << converter_path.string() << "\"\n";
            return 1;
        }

        // New step: Find and process subfolders in the characters directory
        std::vector<fs::path> character_subfolders;
        for (const auto& entry : fs::directory_iterator(characters_folder)) {
            if (fs::is_directory(entry)) {
                character_subfolders.push_back(entry.path());
            }
        }

        if (character_subfolders.empty()) {
            std::cout << "No subfolders found in 'data/characters'. Exiting.\n";
            return 1;
        }

        std::cout << "Found " << character_subfolders.size() << " subfolder(s) in 'data/characters':\n";
        for (const auto& subfolder : character_subfolders) {
            std::cout << "- " << subfolder.filename().string() << "\n";
        }

        // Process all found subfolders
        for (const auto& subfolder : character_subfolders) {
            process_folder(subfolder, bin_file_name);
        }

    } catch (const std::exception& e) {
        std::cout << "An error occurred: " << e.what() << "\n";
        return 1;
    }

    std::cout << "RitoSkin - by Nylish" << "\n";
    std::cout << "You can close the window!";
    std::cin.ignore();
    std::cin.get();

    return 0;
}

void process_folder(const fs::path& folder_path, const std::string& bin_file_name) {
    std::cout << "Processing folder: " << folder_path << "\n";

    // Delete all .bin files in the folder
    for (const auto& entry : fs::directory_iterator(folder_path)) {
        if (entry.path().extension() == ".bin") {
            fs::remove(entry.path());
        }
    }
    std::cout << "All .bin files deleted.\n";

    // Search for the .bin file in the folder
    fs::path found_file_path;
    if (find_bin_file(folder_path, bin_file_name, found_file_path)) {
        std::cout << "Found " << bin_file_name << " at \"" << found_file_path.string() << "\"\n";
        process_bin_file(found_file_path);
    } else {
        std::cout << bin_file_name << " not found in \"" << folder_path.string() << "\". Skipping this folder.\n";
    }
}

bool find_bin_file(const fs::path& dir, const std::string& filename, fs::path& result) {
    for (const auto& entry : fs::directory_iterator(dir)) {
        if (fs::is_directory(entry) && entry.path().filename() != "animations") {
            if (find_bin_file(entry.path(), filename, result)) {
                return true;
            }
        } else if (fs::is_regular_file(entry) && entry.path().filename() == filename) {
            result = entry.path();
            return true;
        }
    }
    return false;
}

void process_bin_file(const fs::path& bin_file_path) {
    try {
        // Step 6: Convert .bin to .py
        std::cout << "Converting " << bin_file_path << " to .py...\n";
        convert_bin_to_py(bin_file_path);

        fs::path py_file_path = bin_file_path;
        py_file_path.replace_extension(".py");

        // Step 7: Modify the .py file
        std::cout << "Modifying " << py_file_path << "...\n";
        modify_py_file(py_file_path);

        // Step 8: Convert .py back to .bin
        std::cout << "Converting " << py_file_path << " back to .bin...\n";
        convert_py_to_bin(py_file_path);

        // Rename the final .bin file to skin0.bin
        fs::path new_bin_file_path = bin_file_path.parent_path() / "skin0.bin";

        // Check if skin0.bin already exists and delete it if so
        if (fs::exists(new_bin_file_path)) {
            fs::remove(new_bin_file_path);
        }

        fs::rename(bin_file_path, new_bin_file_path);
        std::cout << "Renamed file to " << new_bin_file_path << "\n";

        // Cleanup: Delete any files that are not skin0.bin or skin0.py
        std::cout << "Cleaning up unnecessary files...\n";
        for (const auto& entry : fs::directory_iterator(bin_file_path.parent_path())) {
            if (entry.path().filename() != "skin0.bin" && entry.path().filename() != "skin0.py") {
                fs::remove(entry.path());
            }
        }
    } catch (const std::exception& e) {
        std::cout << "An error occurred: " << e.what() << "\n";
    }
}

void convert_bin_to_py(const fs::path& file_path) {
    std::string command = "..\\resources\\bin\\ritobin_cli.exe \"" + file_path.string() + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        throw std::runtime_error("Failed to convert .bin to .py");
    }
}

void modify_py_file(const fs::path& file_path) {
    std::ifstream input_file(file_path);
    if (!input_file.is_open()) {
        throw std::runtime_error("Failed to open input file: " + file_path.string());
    }

    std::ofstream output_file(file_path.string() + ".tmp");
    if (!output_file.is_open()) {
        input_file.close();
        throw std::runtime_error("Failed to open temporary output file");
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
        std::cout << "No modifications were necessary in " << file_path << "\n";
    }
}

void convert_py_to_bin(const fs::path& file_path) {
    std::string command = "..\\resources\\bin\\ritobin_cli.exe \"" + file_path.string() + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        throw std::runtime_error("Failed to convert .py to .bin");
    }
}
