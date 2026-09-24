#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "VGM::ClhepVGM" for configuration "RelWithDebInfo"
set_property(TARGET VGM::ClhepVGM APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(VGM::ClhepVGM PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libClhepVGM.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libClhepVGM.so"
  )

list(APPEND _cmake_import_check_targets VGM::ClhepVGM )
list(APPEND _cmake_import_check_files_for_VGM::ClhepVGM "${_IMPORT_PREFIX}/lib/libClhepVGM.so" )

# Import target "VGM::BaseVGM" for configuration "RelWithDebInfo"
set_property(TARGET VGM::BaseVGM APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(VGM::BaseVGM PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libBaseVGM.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libBaseVGM.so"
  )

list(APPEND _cmake_import_check_targets VGM::BaseVGM )
list(APPEND _cmake_import_check_files_for_VGM::BaseVGM "${_IMPORT_PREFIX}/lib/libBaseVGM.so" )

# Import target "VGM::XmlVGM" for configuration "RelWithDebInfo"
set_property(TARGET VGM::XmlVGM APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(VGM::XmlVGM PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libXmlVGM.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libXmlVGM.so"
  )

list(APPEND _cmake_import_check_targets VGM::XmlVGM )
list(APPEND _cmake_import_check_files_for_VGM::XmlVGM "${_IMPORT_PREFIX}/lib/libXmlVGM.so" )

# Import target "VGM::Geant4GM" for configuration "RelWithDebInfo"
set_property(TARGET VGM::Geant4GM APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(VGM::Geant4GM PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libGeant4GM.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libGeant4GM.so"
  )

list(APPEND _cmake_import_check_targets VGM::Geant4GM )
list(APPEND _cmake_import_check_files_for_VGM::Geant4GM "${_IMPORT_PREFIX}/lib/libGeant4GM.so" )

# Import target "VGM::RootGM" for configuration "RelWithDebInfo"
set_property(TARGET VGM::RootGM APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(VGM::RootGM PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libRootGM.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libRootGM.so"
  )

list(APPEND _cmake_import_check_targets VGM::RootGM )
list(APPEND _cmake_import_check_files_for_VGM::RootGM "${_IMPORT_PREFIX}/lib/libRootGM.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
