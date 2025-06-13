"""
Script de prueba de la extracción corregida
========================================
"""

from extraer_datos import extraer_datos_html
import json

def test_extraccion():
    print("🧪 PROBANDO EXTRACCIÓN DE DATOS")
    print("=" * 50)
    
    # Probar con el directorio YAYI
    directorio = "d:/Documentos y Archivos/YAYI FULL - 3 FEBRERO_archivos"
    
    print(f"📁 Directorio de prueba: {directorio}")
    
    try:
        resultado = extraer_datos_html(directorio)
        
        if resultado:
            print("\n✅ EXTRACCIÓN EXITOSA")
            print(f"📊 Resumen:")
            print(f"   • Hojas procesadas: {resultado['resumen']['total_hojas']}")
            print(f"   • Total productos: {resultado['resumen']['total_productos']}")
            
            print(f"\n📋 Detalles por hoja:")
            for i, hoja in enumerate(resultado['hojas'][:5]):  # Mostrar primeras 5
                print(f"   {i+1}. {hoja['nombre']}: {hoja['total_productos']} productos")
                
                # Mostrar algunos productos de ejemplo
                if hoja['productos']:
                    print(f"      Ejemplos:")
                    for j, producto in enumerate(hoja['productos'][:3]):
                        desc = producto['descripcion'][:50] + "..." if len(producto['descripcion']) > 50 else producto['descripcion']
                        print(f"        - {desc}")
                        if j >= 2:  # Solo mostrar 3 ejemplos
                            break
            
            if len(resultado['hojas']) > 5:
                print(f"   ... y {len(resultado['hojas']) - 5} hojas más")
            
            # Guardar resultado para verificación
            with open('test_extraccion_resultado.json', 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Resultado guardado en 'test_extraccion_resultado.json'")
            
        else:
            print("❌ EXTRACCIÓN FALLÓ")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_extraccion()
