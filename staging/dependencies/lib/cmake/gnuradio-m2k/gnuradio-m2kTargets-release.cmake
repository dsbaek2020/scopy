#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "gnuradio::gnuradio-m2k" for configuration "Release"
set_property(TARGET gnuradio::gnuradio-m2k APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(gnuradio::gnuradio-m2k PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgnuradio-m2k.1.0.0.0.dylib"
  IMPORTED_SONAME_RELEASE "/Users/baegdaeseong/scopy/staging/dependencies/lib/libgnuradio-m2k.1.0.0.dylib"
  )

list(APPEND _cmake_import_check_targets gnuradio::gnuradio-m2k )
list(APPEND _cmake_import_check_files_for_gnuradio::gnuradio-m2k "${_IMPORT_PREFIX}/lib/libgnuradio-m2k.1.0.0.0.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
