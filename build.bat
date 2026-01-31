@echo off
echo =======================================
echo   CONSTRUCTION TS_Tool_Routier.exe
echo =======================================
echo.

echo 1. Installation des dépendances...
pip install pyinstaller PyQt6

echo.
echo 2. Construction de l'exécutable...
pyinstaller --name="TS_Tool_Routier" ^
            --windowed ^
            --icon=resources/icon.ico ^
            --add-data="config.ini;." ^
            --add-data="README.txt;." ^
            --add-data="resources;resources" ^
            --noconfirm ^
            --clean ^
            --onefile ^
            ts_app.py

echo.
echo 3. Copie des fichiers supplémentaires...
copy config.ini dist\
copy README.txt dist\
mkdir dist\logs 2>nul

echo.
echo =======================================
echo   ✅ CONSTRUCTION TERMINÉE !
echo =======================================
echo.
echo L'exécutable est dans : dist\TS_Tool_Routier.exe
echo.
pause
