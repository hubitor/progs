# Example of compiled problem using "gauss"

FILE(GLOB SRCS *.h *.cpp *.inl *.hpp)

ADD_EXECUTABLE(gauss_app ${SRCS})
MACRO_DebugPostfix(gauss_app)

TARGET_LINK_LIBRARIES(gauss_app gauss)
TARGET_INCLUDE_DIRECTORIES(gauss_app PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_test(NAME gauss_app
         COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/run.py --nogui ${EXECUTABLE_OUTPUT_PATH}/gauss_app
         WORKING_DIRECTORY ${PROJECT_BINARY_DIR})