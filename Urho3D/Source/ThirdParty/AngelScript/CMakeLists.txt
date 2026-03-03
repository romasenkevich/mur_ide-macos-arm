# Copyright (c) 2008-2023 the Urho3D project
# License: MIT

# Define target name
set (TARGET_NAME AngelScript)

# Define preprocessor macros
if (CLANG_PRE_STANDARD)
    add_definitions (-DCLANG_PRE_STANDARD)
endif ()
if (NOT EXCEPTIONS)
    add_definitions (-DAS_NO_EXCEPTIONS)
endif ()

if (URHO3D_FORCE_AS_MAX_PORTABILITY)
    add_definitions (-DAS_MAX_PORTABILITY)
endif ()

# Define source files
define_source_files (GLOB_CPP_PATTERNS source/*.cpp GLOB_H_PATTERNS include/*.h source/*.h)
if (ARM)
    # ASM отключен на Apple Silicon
    set (ASM_FILES "")
endif ()
#list (APPEND SOURCE_FILES ${ASM_FILES})

# Define dependency libs
set (INCLUDE_DIRS include)

# Setup target
setup_library ()

# Install headers for building and using the Urho3D library (install dependency for Urho3D/Script/APITemplates.h)
install_header_files (DIRECTORY include/ DESTINATION ${DEST_INCLUDE_DIR}/ThirdParty/AngelScript FILES_MATCHING PATTERN *.h)     # Note: the trailing slash is significant
