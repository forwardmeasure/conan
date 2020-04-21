include(FindPackageHandleStandardArgs)
find_package(PkgConfig)

unset(absl_FOUND)
# pkg_check_modules(PC_absl REQUIRED absl)

# Look for absl, relying on the idea that is has a well-defined pkgconfig file
find_path(absl_INCLUDE_DIR
        NAMES absl/algorithm absl/base absl/strings
        HINTS /usr/local/include/absl
        PATHS ${PC_absl_INCLUDE_DIRS})

set (absl_FIND_VERBOSE TRUE)
if(absl_FIND_VERBOSE)
  message("absl_INCLUDE_DIR = ${absl_INCLUDE_DIR}")
  message("PC_absl_LIBDIR = ${PC_absl_LIBDIR}")
  message("PC_absl_LIBRARY_DIRS = ${PC_absl_LIBRARY_DIRS}")
  message("absl_Eigen_INCLUDE_DIR = ${absl_Eigen_INCLUDE_DIR}")
endif()

list(APPEND ABSL_INCLUDE_DIRS ${absl_INCLUDE_DIRS})

set(LIB_BASE_NAME absl)
set(absl_FOUND TRUE)

foreach(COMPONENT IN LISTS absl_FIND_COMPONENTS)
  set(absl_{COMPONENT}_FOUND FALSE)

  find_library(${COMPONENT}_LIBRARY
               NAMES ${COMPONENT}
               HINTS ${PC_absl_LIBDIR} ${PC_absl_LIBRARY_DIRS})

  find_package_handle_standard_args(${COMPONENT}
                                    DEFAULT_MSG
                                    ${COMPONENT}_LIBRARY
                                    absl_INCLUDE_DIR)

  mark_as_advanced(${COMPONENT}_LIBRARY)

  if(${COMPONENT}_FOUND)
    set(absl_{COMPONENT}_FOUND TRUE)

    if(NOT TARGET absl::${COMPOENT})
      add_library(absl::${COMPONENT} SHARED IMPORTED)
      set_target_properties(absl::${COMPONENT}
                            PROPERTIES INTERFACE_INCLUDE_DIRECTORIES
                                       ${absl_INCLUDE_DIR}
                                       IMPORTED_LOCATION
                                       ${${COMPONENT}_LIBRARY} # The DLL, .so or
                                                               # .dylib
                            )
    endif()

    list(APPEND ABSL_LIBRARIES ${${COMPONENT}_LIBRARY})
  else()
    message("absl component ${COMPONENT} not found!")
    set(absl_FOUND FALSE)
  endif()
endforeach()
