"""
Demo del Pipeline Completo - Análisis de Ferretería con IA
=========================================================

Este script demuestra todo el pipeline de procesamiento:
1. Extracción de datos desde archivos HTML
2. Purificación de datos con IA
3. Análisis y estructuración
4. Exportación a Excel

Autor: Asistente IA
Fecha: 12 de junio de 2025
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def mostrar_bienvenida():
    """Muestra una ventana de bienvenida explicando el pipeline"""
    
    ventana = tk.Tk()
    ventana.title("🔧 Pipeline Completo - Análisis de Ferretería con IA")
    ventana.geometry("800x600")
    ventana.configure(bg='#f0f0f0')
    
    # Frame principal
    main_frame = ttk.Frame(ventana, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Título
    titulo = ttk.Label(main_frame, text="🔧 Sistema de Análisis de Ferretería con IA", 
                       font=('Arial', 18, 'bold'))
    titulo.pack(pady=(0, 20))
    
    # Descripción del pipeline
    descripcion = """
🎯 PIPELINE COMPLETO DE PROCESAMIENTO:

1️⃣ EXTRACCIÓN DE DATOS
   • Selecciona directorio con archivos HTML (Excel convertido)
   • Extrae automáticamente productos, precios y descripciones
   • Identifica categorías y códigos de productos

2️⃣ PURIFICACIÓN CON IA 🧹
   • Elimina texto irrelevante y duplicados
   • Estructura los datos en formato estándar
   • Valida códigos y precios automáticamente
   • Agrupa productos por categorías

3️⃣ ANÁLISIS INTELIGENTE 🤖
   • Análisis de precios y tendencias
   • Identificación de productos destacados
   • Sugerencias de optimización
   • Detección de inconsistencias

4️⃣ EXPORTACIÓN ESTRUCTURADA 📊
   • Genera Excel con múltiples hojas
   • Resumen ejecutivo automático
   • Datos organizados por categorías
   • Formato profesional y fácil lectura

🚀 BENEFICIOS:
   • Procesamiento automático y rápido
   • Datos limpios y estructurados
   • Análisis inteligente con IA
   • Exportación lista para usar
"""
    
    text_widget = tk.Text(main_frame, wrap=tk.WORD, width=80, height=25, 
                         font=('Consolas', 10), bg='white', fg='#333')
    text_widget.insert(tk.END, descripcion)
    text_widget.config(state=tk.DISABLED)
    
    # Scrollbar para el texto
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    # Frame para el texto y scrollbar
    text_frame = ttk.Frame(main_frame)
    text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
      # Botones
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    def abrir_app_principal():
        ventana.destroy()
        # Cambiar al directorio correcto y ejecutar
        app_path = current_dir / "ferreteria_analyzer_app.py"
        os.system(f'cd "{current_dir}" ; python "{app_path}"')
    
    def abrir_launcher():
        ventana.destroy()
        launcher_path = current_dir.parent / "YAYI FULL - 3 FEBRERO_archivos" / "launcher_app.py"
        if launcher_path.exists():
            os.system(f'python "{launcher_path}"')
        else:
            messagebox.showwarning("Archivo no encontrado", f"No se encontró el launcher en: {launcher_path}")
    
    def mostrar_estadisticas():
        mostrar_stats_proyecto()
    
    ttk.Button(button_frame, text="🚀 Abrir Aplicación Principal", 
               command=abrir_app_principal, width=25).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="🎬 Ver Demo Visual", 
               command=abrir_launcher, width=20).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="📊 Estadísticas", 
               command=mostrar_estadisticas, width=15).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="❌ Cerrar", 
               command=ventana.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    # Centrar ventana
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - (ventana.winfo_width() // 2)
    y = (ventana.winfo_screenheight() // 2) - (ventana.winfo_height() // 2)
    ventana.geometry(f"+{x}+{y}")
    
    ventana.mainloop()

def mostrar_stats_proyecto():
    """Muestra estadísticas del proyecto"""
    
    stats_window = tk.Toplevel()
    stats_window.title("📊 Estadísticas del Proyecto")
    stats_window.geometry("600x500")
    stats_window.configure(bg='#f0f0f0')
    
    frame = ttk.Frame(stats_window, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Título
    ttk.Label(frame, text="📊 Estadísticas del Proyecto", 
              font=('Arial', 16, 'bold')).pack(pady=(0, 20))
    
    # Contar archivos
    archivos_py = len(list(current_dir.glob("*.py")))
    archivos_json = len(list(current_dir.glob("*.json")))
    archivos_xlsx = len(list(current_dir.glob("*.xlsx")))
    
    # Estadísticas
    stats_text = f"""
🔧 ARCHIVOS DEL PROYECTO:
   • Scripts Python: {archivos_py}
   • Archivos JSON: {archivos_json}
   • Archivos Excel: {archivos_xlsx}

📈 FUNCIONALIDADES IMPLEMENTADAS:
   • ✅ Extracción automática de datos HTML
   • ✅ Purificación inteligente con IA
   • ✅ Análisis de productos y precios
   • ✅ Interfaz gráfica completa
   • ✅ Exportación a Excel estructurado
   • ✅ Detección de duplicados
   • ✅ Validación de datos
   • ✅ Categorización automática

🚀 MEJORAS IMPLEMENTADAS:
   • ✅ Pipeline completo integrado
   • ✅ Purificación en tiempo real
   • ✅ UI mejorada con nuevos botones
   • ✅ Exportación multi-hoja
   • ✅ Análisis con IA integrado
   • ✅ Manejo de errores robusto

💡 TECNOLOGÍAS UTILIZADAS:
   • Python 3.x
   • Tkinter para UI
   • pandas para datos
   • openpyxl para Excel
   • BeautifulSoup para HTML
   • JSON para almacenamiento
   • Threading para UI responsiva

🎯 ESTADO: PROYECTO COMPLETADO ✅
"""
    
    text_widget = tk.Text(frame, wrap=tk.WORD, width=70, height=25, 
                         font=('Consolas', 9), bg='white', fg='#333')
    text_widget.insert(tk.END, stats_text)
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    ttk.Button(frame, text="Cerrar", command=stats_window.destroy).pack(pady=10)

def verificar_archivos_necesarios():
    """Verifica que todos los archivos necesarios estén presentes"""
    
    archivos_requeridos = [
        "ferreteria_analyzer_app.py",
        "extraer_datos.py",
        "data_analyzer.py"
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not (current_dir / archivo).exists():
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        messagebox.showerror("Archivos Faltantes", 
                           f"Faltan los siguientes archivos:\n" + 
                           "\n".join(archivos_faltantes))
        return False
    
    return True

def main():
    """Función principal"""
    print("🔧 Iniciando Demo del Pipeline Completo...")
    print("📁 Directorio de trabajo:", current_dir)
    
    # Verificar archivos
    if not verificar_archivos_necesarios():
        return
    
    # Mostrar bienvenida
    mostrar_bienvenida()

if __name__ == "__main__":
    main()
