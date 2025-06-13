#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar muestra de datos purificados
"""

import json


def mostrar_muestra_avanzada():
    """Muestra una muestra avanzada de los datos purificados"""
    try:
        with open('datos_purificados.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        productos = datos.get('productos', [])
        metadata = datos.get('metadata', {})
        
        print("📊 REPORTE DE DATOS PURIFICADOS")
        print("=" * 60)
        print(f"📋 Planilla original: {metadata.get('planilla_original', 'N/A')}")
        print(f"🏪 Proveedor: {metadata.get('proveedor', 'N/A')}")
        print(f"📅 Fecha purificación: {metadata.get('fecha_purificacion', 'N/A')}")
        print(f"📦 Total productos: {metadata.get('total_productos', 'N/A'):,}")
        print(f"⚡ Eficiencia: {metadata.get('eficiencia_purificacion', 'N/A')}")
        print()
        
        # Analizar tipos de datos
        campos_encontrados = {}
        productos_con_codigo = 0
        productos_con_precio = 0
        productos_con_descripcion = 0
        
        for producto in productos:
            for campo in producto.keys():
                if campo not in campos_encontrados:
                    campos_encontrados[campo] = 0
                campos_encontrados[campo] += 1
            
            if 'codigo' in producto:
                productos_con_codigo += 1
            if 'precios' in producto:
                productos_con_precio += 1
            if 'descripcion' in producto:
                productos_con_descripcion += 1
        
        print("📈 ANÁLISIS DE CAMPOS:")
        print("-" * 30)
        for campo, cantidad in sorted(campos_encontrados.items()):
            porcentaje = (cantidad / len(productos)) * 100 if productos else 0
            print(f"  {campo}: {cantidad:,} ({porcentaje:.1f}%)")
        
        print()
        print("🎯 RESUMEN DE COMPLETITUD:")
        print("-" * 30)
        print(f"  Con código: {productos_con_codigo:,} ({(productos_con_codigo/len(productos)*100):.1f}%)")
        print(f"  Con precio: {productos_con_precio:,} ({(productos_con_precio/len(productos)*100):.1f}%)")
        print(f"  Con descripción: {productos_con_descripcion:,} ({(productos_con_descripcion/len(productos)*100):.1f}%)")
        
        print()
        print("🔍 MUESTRA DE PRODUCTOS COMPLETOS:")
        print("-" * 40)
        
        # Buscar productos más completos
        productos_completos = []
        for i, producto in enumerate(productos):
            if 'codigo' in producto and 'descripcion' in producto and 'precios' in producto:
                productos_completos.append((i, producto))
                if len(productos_completos) >= 10:
                    break
        
        for i, (idx, producto) in enumerate(productos_completos[:5]):
            print(f"Producto {idx + 1} (completo):")
            for clave, valor in producto.items():
                if clave == 'precios' and isinstance(valor, list):
                    print(f"  {clave}: {', '.join(valor[:3])}{'...' if len(valor) > 3 else ''}")
                elif isinstance(valor, str) and len(valor) > 50:
                    print(f"  {clave}: {valor[:50]}...")
                else:
                    print(f"  {clave}: {valor}")
            print("-" * 30)
        
        print()
        print("💎 MUESTRA DE PRODUCTOS CON DIFERENTES CARACTERÍSTICAS:")
        print("-" * 50)
        
        # Buscar diferentes tipos de productos
        tipos_muestra = {
            'con_medida': None,
            'con_iva': None,
            'solo_descripcion': None,
            'precio_alto': None
        }
        
        for producto in productos:
            if 'medida' in producto and tipos_muestra['con_medida'] is None:
                tipos_muestra['con_medida'] = producto
            elif 'iva' in producto and tipos_muestra['con_iva'] is None:
                tipos_muestra['con_iva'] = producto
            elif len(producto) == 3 and 'descripcion' in producto and tipos_muestra['solo_descripcion'] is None:
                tipos_muestra['solo_descripcion'] = producto
            elif 'precios' in producto and tipos_muestra['precio_alto'] is None:
                try:
                    precios = producto['precios']
                    if any(float(p.replace(',', '.')) > 10000 for p in precios if p.replace(',', '.').replace('.', '').isdigit()):
                        tipos_muestra['precio_alto'] = producto
                except:
                    pass
        
        for tipo, producto in tipos_muestra.items():
            if producto:
                print(f"{tipo.replace('_', ' ').title()}:")
                for clave, valor in producto.items():
                    if clave == 'precios' and isinstance(valor, list):
                        print(f"  {clave}: {', '.join(valor[:2])}{'...' if len(valor) > 2 else ''}")
                    else:
                        print(f"  {clave}: {valor}")
                print("-" * 25)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    mostrar_muestra_avanzada()
