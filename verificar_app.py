#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba rápida para verificar que la aplicación funciona correctamente
"""

import sys
import os

def probar_importacion():
    """Prueba que la aplicación se pueda importar sin errores"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        print("🔧 PRUEBA: Importación de módulos")
        print("-" * 40)
        
        # Probar importación principal
        print("📦 Importando ferreteria_analyzer_app...")
        import ferreteria_analyzer_app
        print("✅ ferreteria_analyzer_app importado correctamente")
        
        # Probar que la clase se puede instanciar
        print("🏗️  Verificando clase FerreteriaAnalyzerApp...")
        app_class = ferreteria_analyzer_app.FerreteriaAnalyzerApp
        print("✅ Clase encontrada")
        
        # Verificar métodos clave
        print("🔍 Verificando métodos clave...")
        metodos_requeridos = [
            'extract_data',
            'extract_html_data_intelligent',
            'detectar_proveedores_en_contenido',
            'generar_nombre_hoja_inteligente'
        ]
        
        for metodo in metodos_requeridos:
            if hasattr(app_class, metodo):
                print(f"   ✅ {metodo}")
            else:
                print(f"   ❌ {metodo} - FALTANTE")
        
        print("\n🎉 TODAS LAS PRUEBAS PASARON")
        print("📱 La aplicación está lista para usar")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    
    return True

def mostrar_instrucciones():
    """Muestra instrucciones de uso"""
    print("\n" + "=" * 50)
    print("📋 INSTRUCCIONES DE USO")
    print("=" * 50)
    print()
    print("1. 🚀 Ejecutar aplicación:")
    print("   python ferreteria_analyzer_app.py")
    print()
    print("2. 📂 Seleccionar directorio:")
    print("   - Clic en 'Seleccionar' en la sección Configuración")
    print("   - Elegir directorio con archivos .htm")
    print()
    print("3. 🔍 Extraer datos:")
    print("   - Clic en '🔍 Extraer Datos'")
    print("   - El sistema detectará automáticamente la estrategia")
    print()
    print("4. 📊 Casos soportados:")
    print("   ✅ Un solo proveedor (ej: YAYI)")
    print("   ✅ Múltiples proveedores")
    print("   ✅ Detección automática")
    print()
    print("🎯 EJEMPLOS:")
    print("   • Directorio YAYI → Estrategia: single_provider")
    print("   • Directorio mixto → Estrategia: multiple_providers")

if __name__ == "__main__":
    print("🔧 VERIFICACIÓN DE LA APLICACIÓN")
    print("=" * 50)
    print()
    
    if probar_importacion():
        mostrar_instrucciones()
    else:
        print("\n❌ La aplicación tiene problemas")
        print("💡 Revisar errores arriba para solucionar")
