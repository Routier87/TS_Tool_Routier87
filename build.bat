@echo off
echo ========================================
echo   CONSTRUCTION TS_Tool_Routier.exe
echo   Développé par ROUTIER87
echo ========================================
echo.

echo 1. Installation des dépendances...
pip install pyinstaller PyQt6 --quiet

echo.
echo 2. Construction de l'exécutable...
pyinstaller --noconfirm --clean --onefile ^
            --name="TS_Tool_Routier" ^
            --windowed ^
            --icon=NONE ^
            --add-data="README.txt;." ^
            app.py

echo.
echo 3. Préparation du dossier final...
if exist "TS_Tool_Routier_Final" rmdir /s /q "TS_Tool_Routier_Final"
mkdir "TS_Tool_Routier_Final"
copy "dist\TS_Tool_Routier.exe" "TS_Tool_Routier_Final\"
copy "README.txt" "TS_Tool_Routier_Final\"

echo.
echo ========================================
echo   ✅ CONSTRUCTION TERMINÉE !
echo ========================================
echo.
echo 📁 L'exécutable est dans : TS_Tool_Routier_Final\
echo.
echo 🎮 Pour l'utiliser :
echo   1. Déplacez le dossier où vous voulez
echo   2. Lancez TS_Tool_Routier.exe
echo   3. Modifiez l'offset argent après vos tests
echo.
pause
