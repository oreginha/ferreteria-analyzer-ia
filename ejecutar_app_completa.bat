@echo off
echo ================================================
echo    🔧 FERRETERIA ANALYZER - PIPELINE COMPLETO
echo ================================================
echo.
echo Este script ejecuta la aplicación principal
echo del analizador de ferretería con IA integrada.
echo.
echo Funcionalidades disponibles:
echo  - Extracción de datos desde HTML
echo  - Purificación inteligente de datos
echo  - Análisis con IA
echo  - Exportación a Excel estructurado
echo.
echo ================================================
echo.

cd /d "d:\Documentos y Archivos\Excel\PLANILLA FERRETERIA _archivos"
python ferreteria_app_modular.py

echo.
echo ================================================
echo Aplicación cerrada. Presiona cualquier tecla...
pause > nul
