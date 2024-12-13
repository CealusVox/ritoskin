cmake_minimum_required(VERSION 3.10)

project(ritoskin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
endif()

# Find and link Threads package (if needed)
find_package(Threads REQUIRED)

add_subdirectory(ritobin_lib)
add_subdirectory(ritoskin)
