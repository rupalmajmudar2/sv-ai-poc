@echo off
REM Vector Database Explorer Scripts
REM Windows batch file to run vector database exploration commands

echo ================================================
echo SportzVillage Vector Database Explorer
echo ================================================

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:menu
echo.
echo What would you like to do?
echo 1. Explore vector database collections
echo 2. Test semantic search (predefined queries)
echo 3. Test custom semantic search query
echo 4. Show database statistics
echo 5. Populate/refresh vector database
echo 6. Reset vector database (DANGER!)
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto explore
if "%choice%"=="2" goto test_search
if "%choice%"=="3" goto custom_search
if "%choice%"=="4" goto stats
if "%choice%"=="5" goto populate
if "%choice%"=="6" goto reset
if "%choice%"=="7" goto exit
echo Invalid choice. Please try again.
goto menu

:explore
echo.
echo ================================================
echo Exploring Vector Database Collections
echo ================================================
python scripts\explore_vectordb.py
pause
goto menu

:test_search
echo.
echo ================================================
echo Testing Semantic Search
echo ================================================
python scripts\test_semantic_search.py
pause
goto menu

:custom_search
echo.
echo ================================================
echo Custom Semantic Search
echo ================================================
set /p query="Enter your search query: "
python scripts\test_semantic_search.py --query "%query%"
pause
goto menu

:stats
echo.
echo ================================================
echo Vector Database Statistics
echo ================================================
python scripts\manage_vectordb.py stats
pause
goto menu

:populate
echo.
echo ================================================
echo Populating Vector Database
echo ================================================
python scripts\manage_vectordb.py populate
pause
goto menu

:reset
echo.
echo ================================================
echo DANGER: Reset Vector Database
echo ================================================
python scripts\manage_vectordb.py reset
pause
goto menu

:exit
echo.
echo Goodbye!
pause