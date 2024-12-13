#include <cstdlib>
#include <ritobin/bin_io.hpp>
#include <ritobin/bin_unhash.hpp>
#include <optional>
#include <filesystem>
#include <iostream>
#include <fstream>
#include <regex>
#include <map>

// Include platform-specific headers for setting binary mode on Windows
#ifdef WIN32
#include <fcntl.h>
#include <io.h>
static void set_binary_mode(FILE* file) {
    if (_setmode(_fileno(file), O_BINARY) == -1) {
        throw std::runtime_error("Can not change mode to binary!");
    }
}
#else
static void set_binary_mode(FILE*) {}
#endif

using ritobin::Bin;
using ritobin::BinUnhasher;
using ritobin::io::DynamicFormat;
namespace fs = std::filesystem;

// Regular expressions for matching skin files and patterns within them
const std::regex SKIN_FILE_PATTERN(R"(skin\d+\.bin)");
const std::regex SKIN_DATA_PATTERN(R"(("Characters/[^/]+/Skins/Skin)\d+(" *= *SkinCharacterDataProperties *\{))");
const std::regex RESOURCE_RESOLVER_PATTERN(R"(("Characters/[^/]+/Skins/Skin)\d+(/Resources" *= *ResourceResolver *\{))");
const std::regex SKIN_NUMBER_PATTERN(R"(Skin\d+)");

// Check if the filename matches the skin file pattern
bool is_valid_skin_file(const std::string& filename) {
    return std::regex_match(filename, SKIN_FILE_PATTERN);
}

// Find folders related to the given champion folder
std::vector<fs::path> find_related_folders(const fs::path& champion_folder) {
    std::vector<fs::path> related_folders;
    std::string champion_name = champion_folder.filename().string();
    fs::path parent_folder = champion_folder.parent_path();

    // Map of champion names to their alternative folder name prefixes
    std::map<std::string, std::vector<std::string>> champion_alternative_names = {
        // Place special cases here!
        {"heimerdinger", {"heimert"}},
        
    };

    // Prepare a list of prefixes to check for related folders
    std::vector<std::string> prefixes = { champion_name };
    if (champion_alternative_names.find(champion_name) != champion_alternative_names.end()) {
        prefixes.insert(prefixes.end(),
                        champion_alternative_names[champion_name].begin(),
                        champion_alternative_names[champion_name].end());
    }

    for (const auto& entry : fs::directory_iterator(parent_folder)) {
        if (fs::is_directory(entry)
            && entry.path() != champion_folder) {
            std::string entry_name = entry.path().filename().string();
            for (const auto& prefix : prefixes) {
                if (entry_name.find(prefix) == 0) {
                    related_folders.push_back(entry.path());
                    break; // Found a matching prefix, no need to check other prefixes
                }
            }
        }
    }

    return related_folders;
}

// Delete the related folders found
void delete_related_folders(const std::vector<fs::path>& related_folders) {
    for (const auto& folder : related_folders) {
        try {
            fs::remove_all(folder); // Remove all contents of the folder
            std::cout << "Deleted folder: " << folder << "\n";
        } catch (const std::exception& e) {
            std::cerr << "Error deleting folder " << folder << ": " << e.what() << "\n";
        }
    }
}

// Modify the .py file to replace skin numbers with "Skin0"
void modify_py_file(const fs::path& file_path) {
    std::ifstream input_file(file_path, std::ios::in | std::ios::binary);
    if (!input_file.is_open()) {
        throw std::runtime_error("Error opening file: " + file_path.string());
    }

    std::ofstream output_file(file_path.string() + ".tmp", std::ios::out | std::ios::binary);
    if (!output_file.is_open()) {
        input_file.close();
        throw std::runtime_error("Error creating temporary file");
    }

    std::string line;
    bool modified = false;
    while (std::getline(input_file, line)) {
        // Check if the line matches the skin data or resource resolver pattern
        if (std::regex_search(line, SKIN_DATA_PATTERN) || std::regex_search(line, RESOURCE_RESOLVER_PATTERN)) {
            line = std::regex_replace(line, SKIN_NUMBER_PATTERN, "Skin0"); // Replace skin number with "Skin0"
            modified = true;
        }
        output_file << line << '\n';
    }

    input_file.close();
    output_file.close();

    if (modified) {
        fs::rename(file_path.string() + ".tmp", file_path); // Rename temporary file to original file
    } else {
        fs::remove(file_path.string() + ".tmp"); // Remove temporary file if no modifications were made
        std::cout << "!! Error: Outdated Hashes | Skin pattern obfuscated !! " << file_path << "\n";
    }
}

// Process a single .bin file: read, unhash, modify, and write back
void process_bin_file(const fs::path& bin_file_path, const fs::path& extracted_skins_folder, int skin_number, BinUnhasher& unhasher) {
    try {
        std::string filename = bin_file_path.filename().string();
        int file_skin_number = std::stoi(filename.substr(4, filename.find('.') - 4));

        if (file_skin_number != skin_number) {
            std::cerr << "Warning: Mismatch in skin numbering for " << filename
                      << ". File suggests " << file_skin_number
                      << ", but processing as " << skin_number << std::endl;
        }

        // Read bin file
        Bin bin;
        std::ifstream bin_file(bin_file_path, std::ios::binary);
        std::vector<char> bin_data((std::istreambuf_iterator<char>(bin_file)), std::istreambuf_iterator<char>());
        bin_file.close();

        std::cout << "Read bin file: " << bin_file_path << " (" << bin_data.size() << " bytes)\n";

        auto format = DynamicFormat::guess(std::string_view{bin_data.data(), bin_data.size()}, bin_file_path.string());
        if (!format) {
            throw std::runtime_error("Failed to guess format for file: " + bin_file_path.string());
        }
        auto error = format->read(bin, bin_data);
        if (!error.empty()) {
            throw std::runtime_error(error);
        }

        // After reading the bin file and obtaining the input format
        auto output_format = DynamicFormat::get(format->oposite_name());
        if (!output_format) {
            throw std::runtime_error("Failed to get output format for file: " + bin_file_path.string());
        }

        // Before unhashing
        std::cout << "Unhashing bin data...\n";
        unhasher.unhash_bin(bin);
        std::cout << "Unhashing completed.\n";

        // Write py file using the output format
        std::vector<char> py_data;
        error = output_format->write(bin, py_data);
        if (!error.empty()) {
            throw std::runtime_error(error);
        }
        fs::path py_file_path = bin_file_path;
        py_file_path.replace_extension(".py");
        std::ofstream py_file(py_file_path, std::ios::binary);
        py_file.write(py_data.data(), py_data.size());
        py_file.close();

        std::cout << "Wrote py file: " << py_file_path << " (" << py_data.size() << " bytes)\n";

        std::cout << "\n" << "Processing skin " << skin_number << " ...\n";
        modify_py_file(py_file_path);

        // Get the binary format for writing
        auto input_format = DynamicFormat::get(output_format->oposite_name());
        if (!input_format) {
            throw std::runtime_error("Failed to get input format for file: " + py_file_path.string());
        }

        // Use a new Bin object for modified data
        Bin modified_bin;

        // Read modified py file
        std::ifstream modified_py_file(py_file_path, std::ios::binary);
        std::vector<char> modified_py_data((std::istreambuf_iterator<char>(modified_py_file)), std::istreambuf_iterator<char>());
        modified_py_file.close();

        // Parse the modified py data using the text format
        error = output_format->read(modified_bin, modified_py_data);
        if (!error.empty()) {
            throw std::runtime_error(error);
        }

        // Write bin file using the binary format
        std::vector<char> new_bin_data;
        error = input_format->write(modified_bin, new_bin_data);
        if (!error.empty()) {
            throw std::runtime_error(error);
        }
        std::ofstream new_bin_file(bin_file_path, std::ios::binary);
        new_bin_file.write(new_bin_data.data(), new_bin_data.size());
        new_bin_file.close();

        std::cout << "Wrote new bin file: " << bin_file_path << " (" << new_bin_data.size() << " bytes)\n";

        std::string champion_name = bin_file_path.parent_path().parent_path().filename().string();
        std::string main_champion_name = extracted_skins_folder.parent_path().filename().string();
        std::string new_champion_folder_name = main_champion_name + "_" + std::to_string(skin_number);

        fs::path new_folder_structure = extracted_skins_folder / std::to_string(skin_number) / new_champion_folder_name / "data" / "characters" / champion_name / "skins";
        fs::create_directories(new_folder_structure);

        fs::path new_bin_file_path = new_folder_structure / "skin0.bin";
        fs::rename(bin_file_path, new_bin_file_path);
        std::cout << "File renamed & moved to " << new_bin_file_path << "\n";

        // Debug purposes | verify regex pattern | unhasher | bin | py | new_bin
        // fs::remove(py_file_path);

    } catch (const std::exception& e) {
        std::cerr << "Error processing file: " << e.what() << "\n";
    }
}

// Process related folders to handle additional skin files
void process_related_folder(const fs::path& related_folder, const fs::path& extracted_skins_folder, const std::string& champion_name, BinUnhasher& unhasher) {
    std::string related_name = related_folder.filename().string();
    std::cout << "Processing related folder: " << related_name << "\n";

    fs::path characters_folder = related_folder / "skins";
    if (fs::exists(characters_folder) && fs::is_directory(characters_folder)) {
        for (const auto& entry : fs::recursive_directory_iterator(characters_folder)) {
            if (entry.path().extension() == ".bin" && entry.path().filename().string().find("skin") == 0) {
                std::string filename = entry.path().filename().string();
                if (is_valid_skin_file(filename)) {
                    int skin_number = std::stoi(filename.substr(4, filename.find('.') - 4));
                    process_bin_file(entry.path(), extracted_skins_folder, skin_number, unhasher);
                } else {
                    std::cerr << "Warning: Invalid skin file name format: " << filename << std::endl;
                }
            }
        }
    }
}

// Process the main champion folder and handle all skin files within it
void process_champion_folder(const fs::path& champion_folder, BinUnhasher& unhasher) {
    std::string champion_name = champion_folder.filename().string();
    std::cout << "Processing champion: " << champion_name << "\n";
    std::cout << "============================================\n";

    fs::path extracted_skins_folder = champion_folder / "skins_extracted";
    fs::create_directories(extracted_skins_folder); // Create directory for extracted skins

    fs::path characters_folder = champion_folder / "skins";

    std::map<int, std::vector<fs::path>> skin_map;
    if (fs::exists(characters_folder) && fs::is_directory(characters_folder)) {
        for (const auto& entry : fs::recursive_directory_iterator(characters_folder)) {
            if (entry.path().extension() == ".bin" && entry.path().filename().string().find("skin") == 0) {
                std::string filename = entry.path().filename().string();
                if (is_valid_skin_file(filename)) {
                    int skin_number = std::stoi(filename.substr(4, filename.find('.') - 4));
                    skin_map[skin_number].push_back(entry.path());
                } else {
                    std::cerr << "Warning: Invalid skin file name format: " << filename << std::endl;
                }
            }
        }
    }

    std::cout << "Found " << skin_map.size() << " valid skin files for " << champion_name << std::endl;
    for (const auto& [number, paths] : skin_map) {
        std::cout << "  Skin " << number << ": " << paths.size() << " files\n";
    }

    for (const auto& [number, paths] : skin_map) {
        for (const auto& path : paths) {
            process_bin_file(path, extracted_skins_folder, number, unhasher);
        }
    }

    std::vector<fs::path> related_folders = find_related_folders(champion_folder);
    for (const auto& related_folder : related_folders) {
        process_related_folder(related_folder, extracted_skins_folder, champion_name, unhasher);
    }

    delete_related_folders(related_folders); // Delete related folders after processing
}

int main(int argc, char** argv) {
    try {
        fs::path current_dir = fs::current_path();
        fs::path champions_folder = current_dir / "process_champions";

        if (!fs::exists(champions_folder) || !fs::is_directory(champions_folder)) {
            std::cerr << "'process_champions' was not found in the current directory\n";
            std::cerr << "Make sure it exists, or create if necessary!\n";
            return 1;
        }

        std::cout << "============================================\n";
        std::cout << "RitoSkin Extractor - by Nylish\n";
        std::cout << "Processing champions from folder: " << champions_folder << "\n";
        std::cout << "============================================\n";

        fs::path exe_dir = fs::path(argv[0]).parent_path();
        fs::path hashes_dir = exe_dir / "hashes";

        if (!fs::exists(hashes_dir) || !fs::is_directory(hashes_dir)) {
            std::cerr << "'hashes' directory was not found in the executable directory\n";
            return 1;
        }

        BinUnhasher unhasher;
        unhasher.load_fnv1a_CDTB((hashes_dir / "hashes.binentries.txt").string());
        unhasher.load_fnv1a_CDTB((hashes_dir / "hashes.binhashes.txt").string());
        unhasher.load_fnv1a_CDTB((hashes_dir / "hashes.bintypes.txt").string());
        unhasher.load_fnv1a_CDTB((hashes_dir / "hashes.binfields.txt").string());
        unhasher.load_xxh64_CDTB((hashes_dir / "hashes.game.txt").string());
        unhasher.load_xxh64_CDTB((hashes_dir / "hashes.lcu.txt").string());

        for (const auto& entry : fs::directory_iterator(champions_folder)) {
            if (fs::is_directory(entry)) {
                process_champion_folder(entry.path(), unhasher);
            }
        }
        std::cout << "============================================\n";
        std::cout << "Process Complete!\n";
        std::cout << "Everything went well? Congrats!\n";
        std::cout << "RitoSkin Extractor - by Nylish\n";
        std::cin.ignore();
        std::cin.get();

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
