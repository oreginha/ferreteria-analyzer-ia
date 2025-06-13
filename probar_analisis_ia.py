#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRUEBA DEL ANÁLISIS CON IA - Verificación específica del método prepare_data_summary
====================================================================================
"""
import os
import sys

def probar_analisis_ia():
    """Prueba específica del método prepare_data_summary"""
    print("🧪 PRUEBA DEL ANÁLISIS CON IA")
    print("=" * 50)
    
    # Agregar al path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from ferreteria_analyzer_app import FerreteriaAnalyzerApp
        import tkinter as tk
        
        print("✅ Importación exitosa de FerreteriaAnalyzerApp")
        
        # Crear instancia de prueba
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal para prueba
        
        app = FerreteriaAnalyzerApp(root)
        print("✅ Instancia de aplicación creada")
        
        # Verificar que el método prepare_data_summary existe
        if hasattr(app, 'prepare_data_summary'):
            print("✅ Método prepare_data_summary encontrado")
            
            # Probar con datos vacíos
            summary_empty = app.prepare_data_summary()
            print(f"✅ Prueba con datos vacíos: {summary_empty[:50]}...")
            
            # Cargar datos si existe un archivo
            datos_file = "datos_extraidos_app.json"
            if os.path.exists(datos_file):
                import json
                with open(datos_file, 'r', encoding='utf-8') as f:
                    app.current_data = json.load(f)
                print(f"✅ Datos cargados desde {datos_file}")
                
                # Probar con datos reales
                summary_real = app.prepare_data_summary()
                print("✅ Resumen generado con datos reales:")
                print("-" * 30)
                lines = summary_real.split('\n')[:10]  # Primeras 10 líneas
                for line in lines:
                    print(f"   {line}")
                if len(summary_real.split('\n')) > 10:
                    print("   ... (resumen truncado)")
            else:
                print(f"⚠️  No se encontró {datos_file} para prueba con datos reales")
            
        else:
            print("❌ Método prepare_data_summary NO encontrado")
            return False
        
        root.destroy()
        
        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 VERIFICACIÓN ESPECÍFICA - ANÁLISIS CON IA")
    print("=" * 60)
    
    success = probar_analisis_ia()
    
    print("\n📋 RESUMEN:")
    if success:
        print("✅ El método prepare_data_summary funciona correctamente")
        print("✅ El análisis con IA debería funcionar sin errores")
        print("\n💡 Para probar análisis completo:")
        print("   1. Ejecutar: python ferreteria_analyzer_app.py")
        print("   2. Configurar API Key de Gemini")
        print("   3. Extraer datos")
        print("   4. Hacer clic en '🤖 Analizar con IA'")
    else:
        print("❌ Hay problemas con el método prepare_data_summary")
        print("💡 Revisar la implementación del método")

if __name__ == "__main__":
    main()
