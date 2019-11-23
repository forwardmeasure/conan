include(FindPackageHandleStandardArgs)
find_package(PkgConfig)

unset(ONNX_FOUND)

# Look for ONNX, relying on the idea that is has a well-defiend pkgconfig file
find_path(ONNX_INCLUDE_DIR
        NAMES
            onnx.pb.h
        HINTS
            /usr/local/include/onnx
        PATHS
            ${PC_ONNX_INCLUDE_DIRS})

if (NOT ONNX_FIND_QUIETLY)
    message("ONNX_INCLUDE_DIR = ${ONNX_INCLUDE_DIR}")
    message("PC_ONNX_LIBDIR = ${PC_ONNX_LIBDIR}")
    message("PC_ONNX_LIBRARY_DIRS = ${PC_ONNX_LIBRARY_DIRS}")
endif()

set(LIB_BASE_NAME ONNX)
set(ONNX_FOUND TRUE)

foreach (COMPONENT IN LISTS ONNX_FIND_COMPONENTS)
    set(ONNX_{COMPONENT}_FOUND FALSE)

    find_library(${COMPONENT}_LIBRARY
            NAMES ${COMPONENT}
            HINTS ${PC_ONNX_LIBDIR} ${PC_ONNX_LIBRARY_DIRS})

    find_package_handle_standard_args(${COMPONENT} DEFAULT_MSG
            ${COMPONENT}_LIBRARY ONNX_INCLUDE_DIR)

    message("${COMPONENT}_LIBRARY = " ${${COMPONENT}_LIBRARY})
    mark_as_advanced(${COMPONENT}_LIBRARY)

    if (${COMPONENT}_FOUND)
        set(ONNX_{COMPONENT}_FOUND TRUE)

        if (NOT TARGET ONNX::${COMPOENT})
            add_library(ONNX::${COMPONENT} SHARED IMPORTED)
            set_target_properties(ONNX::${COMPONENT} PROPERTIES
                    INTERFACE_INCLUDE_DIRECTORIES ${ONNX_INCLUDE_DIR}
                    IMPORTED_LOCATION ${${COMPONENT}_LIBRARY} # The DLL, .so or .dylib
                    )
        endif()

        list(APPEND ONNX_LIBRARIES ${${COMPONENT}_LIBRARY})
    else ()
        message("ONNX component ${COMPONENT} not found!")
        set(ONNX_FOUND FALSE)
    endif ()
endforeach ()
