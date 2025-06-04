# CMakeLists.txt - Modified for macOS Native Build in Qt Creator with Qwt and libiio

cmake_minimum_required(VERSION 3.9)
project(scopy VERSION 2.1.0 LANGUAGES CXX)

set(SCOPY_RELEASE_PHASE -dev)
set(SCOPY_VERSION ${PROJECT_VERSION}${SCOPY_RELEASE_PHASE})

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING "Build type" FORCE)
endif()

find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
  message(STATUS "Using ccache")
  set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
else()
  message(STATUS "Not using ccache")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Insert custom PREFIX_PATH for macOS local installations
set(CMAKE_PREFIX_PATH
  "/Users/baegdaeseong/Qt/6.8.3/macos"
  "/usr/local/lib/cmake"
  "/usr/local/qwt-6.3.0/lib/cmake"
  ${CMAKE_PREFIX_PATH}
)

list(INSERT CMAKE_MODULE_PATH 0 ${PROJECT_SOURCE_DIR}/cmake/Modules)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_definitions(QT_MESSAGELOGCONTEXT)

include(GNUInstallDirs)

# Use Qt6 explicitly
find_package(Qt6 REQUIRED COMPONENTS Widgets LinguistTools)

file(GLOB SRC_LIST *.cpp *.cc)
file(GLOB HEADER_LIST *.h *.hpp)
file(GLOB UI_LIST *.ui)
set(PROJECT_SOURCES ${SRC_LIST} ${HEADER_LIST} ${UI_LIST})

include(ScopyWhatsNew)
set(FOLDER ${CMAKE_SOURCE_DIR}/resources/whatsnew/)
set(RESOURCE_FILE ${CMAKE_SOURCE_DIR}/resources/whatsnew/whatsnew.qrc)
generate_whats_new("${RESOURCE_FILE}" "${FOLDER}")
file(GLOB WHATS_NEW_RESOURCES resources/whatsnew/whatsnew.qrc)
qt_add_resources(SCOPY_RESOURCES ${WHATS_NEW_RESOURCES})

include(ScopyAbout)
configure_about(./resources/about)
file(GLOB SCOPY_RESOURCE_FILES gui/res/resources.qrc resources/aboutpage.qrc)
find_file(SCOPY_ICON_ICO icon.ico PATHS ${CMAKE_SOURCE_DIR}/gui/res)

include(ScopyStyle)
generate_style("--core" ${CMAKE_CURRENT_SOURCE_DIR}/gui/style ${CMAKE_CURRENT_SOURCE_DIR}/gui/include/gui)

option(ENABLE_TRANSLATION "Enable translation" ON)
include(ScopyTranslation)
if(ENABLE_TRANSLATION)
  generate_translations()
  qt_add_resources(SCOPY_RESOURCES ${CMAKE_BINARY_DIR}/translations.qrc)
endif()

qt_add_resources(SCOPY_RESOURCES ${SCOPY_RESOURCE_FILES})

find_path(IIO_INCLUDE_DIRS NAMES iio.h HINTS ${CMAKE_INSTALL_PREFIX}/include /usr/local/include REQUIRED)
find_library(IIO_LIBRARIES NAMES iio libiio HINTS ${CMAKE_INSTALL_PREFIX}/lib /usr/local/lib REQUIRED)

set(SCOPY_DEPENDENCIES ${IIO_LIBRARIES})

add_subdirectory(common)
add_subdirectory(iioutil)
add_subdirectory(gui)
add_subdirectory(gr-util)
add_subdirectory(pluginbase)
add_subdirectory(core)
add_subdirectory(plugins)
add_subdirectory(iio-widgets)

add_executable(${PROJECT_NAME}
  ${PROJECT_SOURCES}
  ${SCOPY_RESOURCES}
  ${SCOPY_DEPENDENCIES}
)

target_include_directories(${PROJECT_NAME} PUBLIC scopy-gui scopy-core)
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Widgets ${SCOPY_DEPENDENCIES} scopy-core scopy-gui)

target_compile_options(${PROJECT_NAME} PUBLIC -Wall)
target_compile_options(${PROJECT_NAME} PUBLIC -Werror=return-type -Werror=uninitialized -Werror=init-self -Werror=switch)

set(CMAKE_VERBOSE_MAKEFILE ON)

# macOS specific bundle settings
if(APPLE)
  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/apple/Info.plist.cmakein ${CMAKE_CURRENT_BINARY_DIR}/Info.plist COPYONLY)
  set_target_properties(${PROJECT_NAME} PROPERTIES
    MACOSX_BUNDLE TRUE
    MACOSX_BUNDLE_GUI_IDENTIFIER scopy
    MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_BINARY_DIR}/Info.plist
  )
endif()

