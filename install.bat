@echo off
echo ====================================================
echo    Instalador - Analizador de Planillas Ferreteria
echo ====================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    echo.
    echo Por favor instala Python desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

REM Verificar si pip está disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no está disponible
    echo.
    echo Instala pip siguiendo las instrucciones en:
    echo https://pip.pypa.io/en/stable/installation/
    pause
    exit /b 1
)

echo ✓ pip encontrado
echo.

REM Instalar dependencias
echo Instalando dependencias...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Falló la instalación de dependencias
    echo.
    echo Intenta ejecutar manualmente:
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ✓ Dependencias instaladas correctamente
echo.

REM Crear acceso directo (opcional)
echo ¿Deseas crear un acceso directo en el escritorio? (S/N)
set /p create_shortcut=

if /i "%create_shortcut%"=="S" (
    echo Creando acceso directo...
    
    REM Crear archivo .bat para ejecutar la aplicación
    echo @echo off > "%~dp0ejecutar_app.bat"
    echo cd /d "%~dp0" >> "%~dp0ejecutar_app.bat"
    echo python ferreteria_analyzer_app.py >> "%~dp0ejecutar_app.bat"
    echo pause >> "%~dp0ejecutar_app.bat"
    
    echo ✓ Acceso directo creado: ejecutar_app.bat
)

echo.
echo ====================================================
echo              INSTALACIÓN COMPLETADA
echo ====================================================
echo.
echo Para ejecutar la aplicación:
echo   1. Abre una terminal en esta carpeta
echo   2. Ejecuta: python ferreteria_analyzer_app.py
echo   3. O usa el archivo ejecutar_app.bat (si lo creaste)
echo.
echo IMPORTANTE:
echo - Necesitarás una API Key de Google Gemini
echo - Obtén tu API Key en: https://makersuite.google.com/app/apikey
echo - Configúrala en la aplicación o en config.ini
echo.
echo ¡Disfruta usando el analizador!
echo.
pause
