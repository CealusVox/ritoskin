cmake_minimum_required(VERSION 3.13)

project(ritoskin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories (if necessary)
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Add the ThreadPool source file
set(SOURCE_FILES
    src/main.cpp
    # src/ThreadPool.cpp
)

# Add executable
add_executable(ritoskin ${SOURCE_FILES})

# Link libraries
target_link_libraries(ritoskin PRIVATE ritobin_lib Threads::Threads)
