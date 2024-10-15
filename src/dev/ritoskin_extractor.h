#ifndef RITOSKIN_EXTRACTOR_H
#define RITOSKIN_EXTRACTOR_H

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <regex>
#include <map>
// https://github.com/nlohmann/json
#include "../resources/json.hpp"

namespace fs = std::filesystem;
using json = nlohmann::json;

std::vector<fs::path> find_related_folders(const fs::path& champion_folder);
void process_champion_folder(const fs::path& champion_folder);
void process_related_folder(const fs::path& related_folder, const fs::path& extracted_skins_folder, const std::string& champion_name);
void process_bin_file(const fs::path& bin_file_path, const fs::path& output_folder, int skin_number);
void convert_bin_to_py(const fs::path& file_path);
void modify_py_file(const fs::path& file_path);
void convert_py_to_bin(const fs::path& file_path);

#endif

