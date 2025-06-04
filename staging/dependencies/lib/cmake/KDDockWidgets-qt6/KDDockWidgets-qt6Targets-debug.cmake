#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "KDAB::kddockwidgets" for configuration "Debug"
set_property(TARGET KDAB::kddockwidgets APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(KDAB::kddockwidgets PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_DEBUG "spdlog::spdlog"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libkddockwidgets-qt6.2.1.1.dylib"
  IMPORTED_SONAME_DEBUG "@rpath/libkddockwidgets-qt6.2.1.dylib"
  )

list(APPEND _cmake_import_check_targets KDAB::kddockwidgets )
list(APPEND _cmake_import_check_files_for_KDAB::kddockwidgets "${_IMPORT_PREFIX}/lib/libkddockwidgets-qt6.2.1.1.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
