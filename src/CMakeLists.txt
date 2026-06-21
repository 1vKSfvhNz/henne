cmake_minimum_required(VERSION 3.15)
project(MIHI_CN_V2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(BUILD_SIMULATION "Build without real hardware" ON)

# Inclusion des sous-répertoires
add_subdirectory(core)
add_subdirectory(scan3d)
add_subdirectory(pattern)
add_subdirectory(ia)
add_subdirectory(hardware)
add_subdirectory(vision)
add_subdirectory(preview)
add_subdirectory(drying)
add_subdirectory(safety)
add_subdirectory(utils)

# Exécutable principal
add_executable(mihi_cn main.cpp)

target_link_libraries(mihi_cn
    mihi_core
    mihi_scan3d
    mihi_pattern
    mihi_ia
    mihi_hardware
    mihi_vision
    mihi_preview
    mihi_drying
    mihi_safety
    mihi_utils
    pthread
)

# Bibliothèques système pour simulation
if(BUILD_SIMULATION)
    target_compile_definitions(mihi_cn PRIVATE SIMULATION_MODE=1)
endif()