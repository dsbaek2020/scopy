#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "libm2k::libm2k" for configuration "RelWithDebInfo"
set_property(TARGET libm2k::libm2k APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(libm2k::libm2k PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libm2k.0.9.0.dylib"
  IMPORTED_SONAME_RELWITHDEBINFO "@rpath/libm2k.0.9.0.dylib"
  )

list(APPEND _cmake_import_check_targets libm2k::libm2k )
list(APPEND _cmake_import_check_files_for_libm2k::libm2k "${_IMPORT_PREFIX}/lib/libm2k.0.9.0.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
