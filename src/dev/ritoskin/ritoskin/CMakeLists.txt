cmake_minimum_required(VERSION 3.13)

project(ritoskin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(ritoskin src/main.cpp)
target_link_libraries(ritoskin PRIVATE ritobin_lib)