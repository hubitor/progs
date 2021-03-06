@echo off
:: Ligne de commande qui va bien pour compiler mes brols
::
:: Utilisation:
::    - installer les libs (dans c:\local p. expl.)
::    - definir la variable d'env MYLOCAL  (=c:\local p. expl. )
::    - double cliquer sur myenv.bat
::    - cd build
::    - cmake -G "Visual Studio 14 2015 Win64" ..
::    - cmake --build . --config Release -- -j6
::    - ctest -C Release
:: Incredibuild (http://www.incredibuild.com/webhelp/#BuildConsole.html)
::    - BuildConsole Waves.sln /rebuild /cfg="Release|x64"

set PATH=%PATH%;%MYLOCAL%\swigwin-3.0.12
set INCLUDE=%MYLOCAL%\include;%MYLOCAL%\MUMPS\include;%MYLOCAL%\eigen-3.3.2
set LIB=%MYLOCAL%\MUMPS\lib

:: ok (MKL + VS en ligne de commande)
:: call "C:\Program Files (x86)\IntelSWTools\compilers_and_libraries\windows\mkl\bin\mklvars.bat" intel64 vs2015
:: call "C:\Program Files (x86)\IntelSWTools\compilers_and_libraries\windows\tbb\bin\tbbvars.bat" intel64 vs2015
:: %comspec% /k "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"
%comspec% /E:ON /V:ON /K ""C:\Program Files (x86)\IntelSWTools\compilers_and_libraries_2018.1.156\windows\bin\ipsxe-comp-vars.bat" intel64 vs2017"