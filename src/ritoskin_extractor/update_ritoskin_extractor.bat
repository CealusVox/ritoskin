@echo off
setlocal

REM Get the current script directory
set "scriptDir=%~dp0"

REM Define the relative path to the source file and output executable name
set "sourceFile=%scriptDir%..\src\ritoskin_extractor.cpp"
set "outputExe=ritoskin_extractor.exe"

REM Run the script to sync hashes
REM python "%scriptDir%..\dev\ritoskin_sync_hashes.py"

REM Compile the source file
g++ -std=c++17 -static -o "%scriptDir%\%outputExe%" "%sourceFile%"

REM Check if the compilation was successful
if exist "%scriptDir%\%outputExe%" (
    echo RitoSkin - Compilation successful.
    echo Executable created at %scriptDir%
) else (
    echo Compilation failed.
    echo Please check the RitoSkin source code for errors.
)

endlocal
pause
