cmake_minimum_required(VERSION 2.6)

PROJECT(MKLcode CXX)

LIST(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}")

# -- MKL/BLAS/LAPACK --

# sous win+msvc+mkl: executer "C:\Program Files (x86)\Intel\Composer XE\mkl\bin\intel64\mklvars_intel64.bat"
# (si ca plante ici, verifier que le VS est en mode x64 si necessaire)


#FIND_PACKAGE(BLAS REQUIRED) # inutile: FIND_LAPACK fait un FIND_BLAS
FIND_PACKAGE(LAPACK REQUIRED) 
find_path(MKL_INCLUDE_DIR "mkl_types.h")  

MESSAGE(STATUS "LAPACK_LIBRARIES=${LAPACK_LIBRARIES}")  
MESSAGE(STATUS "LAPACK_LINKER_FLAGS=${LAPACK_LINKER_FLAGS}")  
MESSAGE(STATUS "BLA_VENDOR=${BLA_VENDOR}")  
MESSAGE(STATUS "BLA_STATIC=${BLA_STATIC}")  

# program

FILE(GLOB SRCS *.h *.cpp *.inl *.hpp)
ADD_EXECUTABLE(MKLcode ${SRCS})
INCLUDE_DIRECTORIES( ${MKL_INCLUDE_DIR} )
TARGET_LINK_LIBRARIES(MKLcode ${LAPACK_LIBRARIES})
