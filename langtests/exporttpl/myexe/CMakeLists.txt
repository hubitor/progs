# Exe 

FILE(GLOB SRCS *.h *.cpp *.inl *.hpp)

ADD_EXECUTABLE(myexe ${SRCS})
IF(WIN32)
    SET_TARGET_PROPERTIES(myexe PROPERTIES DEBUG_POSTFIX "_d")
ENDIF(WIN32)

# ---

INCLUDE_DIRECTORIES( ${PROJECT_SOURCE_DIR}/mydll )

TARGET_LINK_LIBRARIES(myexe mydll )
