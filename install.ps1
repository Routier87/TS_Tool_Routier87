Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION TS_Tool_Routier" -ForegroundColor Cyan
Write-Host "  Développé par ROUTIER87" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
Write-Host "1. Vérification de Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Python n'est pas accessible!" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "2. Installation de PyQt6..." -ForegroundColor Yellow
pip install PyQt6 --quiet

Write-Host ""
Write-Host "3. Installation de PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller --quiet

Write-Host ""
Write-Host "4. Création de l'exécutable..." -ForegroundColor Yellow
pyinstaller --noconfirm --clean --onefile `
            --name="TS_Tool_Routier" `
            --windowed `
            --add-data="README.txt;." `
            app.py

Write-Host ""
Write-Host "5. Préparation du dossier final..." -ForegroundColor Yellow
if (Test-Path "TS_Tool_Routier_Final") {
    Remove-Item -Path "TS_Tool_Routier_Final" -Recurse -Force
}
New-Item -ItemType Directory -Path "TS_Tool_Routier_Final" | Out-Null
Copy-Item -Path "dist\TS_Tool_Routier.exe" -Destination "TS_Tool_Routier_Final\" -Force
Copy-Item -Path "README.txt" -Destination "TS_Tool_Routier_Final\" -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ INSTALLATION TERMINÉE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📁 L'exécutable est dans : TS_Tool_Routier_Final\" -ForegroundColor White
Write-Host "📁 Lancez : TS_Tool_Routier_Final\TS_Tool_Routier.exe" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Pour tester maintenant l'application :" -ForegroundColor Yellow
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
pause
