#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "KF6::Archive" for configuration "Debug"
set_property(TARGET KF6::Archive APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(KF6::Archive PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libKF6Archive.6.14.0.dylib"
  IMPORTED_SONAME_DEBUG "/Users/baegdaeseong/scopy/staging/dependencies/lib/libKF6Archive.6.dylib"
  )

list(APPEND _cmake_import_check_targets KF6::Archive )
list(APPEND _cmake_import_check_files_for_KF6::Archive "${_IMPORT_PREFIX}/lib/libKF6Archive.6.14.0.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
