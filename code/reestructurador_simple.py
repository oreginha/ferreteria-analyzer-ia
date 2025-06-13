#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REESTRUCTURADOR INTELIGENTE SIMPLIFICADO
========================================
Versión simplificada que funciona correctamente
"""

import json
import pandas as pd
import re
import os
from datetime import datetime

def limpiar_caracteres_excel(texto):
    """Limpia caracteres problemáticos para Excel"""
    if pd.isna(texto) or texto == 'nan' or not texto:
        return None
    
    texto_str = str(texto)
    
    # Caracteres problemáticos para Excel
    caracteres_problematicos = ['☻', '☺', '♠', '♣', '♥', '♦']
    for char in caracteres_problematicos:
        texto_str = texto_str.replace(char, '')
    
    # Limpiar caracteres de control
    texto_str = ''.join(char for char in texto_str if ord(char) >= 32 or char in '\t\n\r')
    
    return texto_str.strip() if texto_str.strip() else None

def extraer_precio(texto):
    """Extrae precio de un texto"""
    if not texto:
        return None
    
    patrones = [
        r'\$\s*([\d,]+\.?\d*)',
        r'([\d,]+\.?\d*)\s*\$',
        r'USD\s*([\d,]+\.?\d*)',
        r'ARS\s*([\d,]+\.?\d*)',
        r'([\d,]+\.?\d*)'
    ]
    
    for patron in patrones:
        match = re.search(patron, str(texto), re.IGNORECASE)
        if match:
            try:
                precio_str = match.group(1).replace(',', '')
                return float(precio_str)
            except (ValueError, IndexError):
                continue
    
    return None

def es_codigo_producto(texto):
    """Determina si un texto es un código de producto"""
    if not texto:
        return False
    
    texto_str = str(texto).strip().upper()
    
    # Patrones típicos de códigos
    patrones_codigo = [
        r'^[A-Z]{2,}\d{3,}$',     # ABC123
        r'^\d{3,}[A-Z]{2,}$',     # 123ABC
        r'^[A-Z0-9\-]{4,15}$',    # ABC-123-XYZ
        r'^STN\d+$'               # STN7418
    ]
    
    return any(re.match(patron, texto_str) for patron in patrones_codigo)

def procesar_fila_inteligente(fila, proveedor):
    """Procesa una fila identificando inteligentemente los tipos de datos"""
    producto = {
        'PROVEEDOR': proveedor,
        'CODIGO': None,
        'DESCRIPCION': None,
        'PRECIO': None,
        'CANTIDAD': None,
        'MARCA': None,
        'MONEDA': 'ARS'
    }
    
    descripcion_partes = []
    
    for celda in fila:
        if not celda:
            continue
        
        celda_limpia = limpiar_caracteres_excel(celda)
        if not celda_limpia:
            continue
        
        # Detectar precio
        precio = extraer_precio(celda_limpia)
        if precio and not producto['PRECIO']:
            producto['PRECIO'] = precio
            if '$' in str(celda) or 'USD' in str(celda).upper():
                producto['MONEDA'] = 'USD'
        
        # Detectar código
        elif es_codigo_producto(celda_limpia) and not producto['CODIGO']:
            producto['CODIGO'] = celda_limpia.upper()
        
        # Detectar marca conocida
        elif not producto['MARCA']:
            marcas_conocidas = ['STANLEY', 'DEWALT', 'MAKITA', 'BOSCH', 'TRUPER']
            for marca in marcas_conocidas:
                if marca in str(celda).upper():
                    producto['MARCA'] = marca
                    break
        
        # Acumular para descripción
        if len(str(celda_limpia)) > 3:
            descripcion_partes.append(celda_limpia)
    
    # Crear descripción
    if descripcion_partes:
        producto['DESCRIPCION'] = ' '.join(descripcion_partes)[:200]
    
    # Validar producto
    if producto['DESCRIPCION'] or producto['CODIGO']:
        return producto
    
    return None

def reestructurar_datos_simple(archivo_json):
    """Reestructura los datos de manera simple pero efectiva"""
    print("🔄 REESTRUCTURANDO DATOS DE MANERA INTELIGENTE")
    print("=" * 50)
    
    # Cargar datos
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    resultados_por_proveedor = {}
    
    for hoja in datos.get('hojas', []):
        nombre_hoja = hoja.get('hoja', '')
        
        # Identificar proveedor
        proveedor = nombre_hoja.split('_')[0] if '_' in nombre_hoja else nombre_hoja
        proveedor = proveedor.upper()
        
        print(f"📋 Procesando: {nombre_hoja} → {proveedor}")
        
        productos = []
        
        for tabla in hoja.get('tablas', []):
            filas = tabla.get('filas', [])
            
            # Determinar si hay encabezado (primera fila con palabras clave)
            encabezado_detectado = False
            if filas:
                primera_fila_texto = ' '.join(str(celda).upper() for celda in filas[0] if celda)
                palabras_encabezado = ['CODIGO', 'DESCRIPCION', 'PRECIO', 'PRODUCTO', 'ARTICULO']
                if any(palabra in primera_fila_texto for palabra in palabras_encabezado):
                    encabezado_detectado = True
            
            inicio = 1 if encabezado_detectado else 0
            
            for fila in filas[inicio:]:
                if fila and any(celda for celda in fila):  # Fila no vacía
                    producto = procesar_fila_inteligente(fila, proveedor)
                    if producto:
                        productos.append(producto)
        
        if productos:
            if proveedor not in resultados_por_proveedor:
                resultados_por_proveedor[proveedor] = []
            resultados_por_proveedor[proveedor].extend(productos)
            print(f"✅ {len(productos)} productos procesados")
    
    return resultados_por_proveedor

def crear_excel_reestructurado(datos_por_proveedor, archivo_salida):
    """Crea el archivo Excel reestructurado"""
    print(f"\n📊 CREANDO EXCEL REESTRUCTURADO: {archivo_salida}")
    print("=" * 50)
    
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        # Crear hoja de resumen
        resumen_data = []
        total_productos = 0
        
        for proveedor, productos in datos_por_proveedor.items():
            df = pd.DataFrame(productos)
            
            # Limpiar caracteres problemáticos
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(limpiar_caracteres_excel)
            
            # Eliminar duplicados y filas vacías
            df = df.dropna(subset=['DESCRIPCION'], how='all')
            df = df.drop_duplicates(subset=['CODIGO', 'DESCRIPCION'], keep='first')
            
            # Estadísticas
            con_precio = len(df[df['PRECIO'].notna()]) if 'PRECIO' in df.columns else 0
            con_codigo = len(df[df['CODIGO'].notna()]) if 'CODIGO' in df.columns else 0
            
            resumen_data.append({
                'PROVEEDOR': proveedor,
                'PRODUCTOS': len(df),
                'CON_PRECIO': con_precio,
                'CON_CODIGO': con_codigo,
                'CALIDAD': f"{(con_precio / len(df) * 100):.1f}%" if len(df) > 0 else "0%"
            })
            
            # Exportar hoja del proveedor
            nombre_hoja = proveedor[:31]  # Límite Excel
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            total_productos += len(df)
            print(f"✅ {proveedor}: {len(df)} productos exportados")
        
        # Crear hoja de resumen
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='RESUMEN', index=False)
        
        print(f"✅ Resumen creado")
        print(f"🎉 TOTAL: {total_productos} productos reestructurados")
    
    return archivo_salida

def main():
    """Función principal"""
    print("🧠 REESTRUCTURADOR INTELIGENTE SIMPLIFICADO")
    print("=" * 50)
    
    archivo_datos = "datos_extraidos_app.json"
    
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        return
    
    try:
        # Reestructurar datos
        datos_reestructurados = reestructurar_datos_simple(archivo_datos)
        
        if datos_reestructurados:
            # Crear archivo Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_salida = f"ferreteria_reestructurada_{timestamp}.xlsx"
            
            crear_excel_reestructurado(datos_reestructurados, archivo_salida)
            
            print(f"\n🎉 REESTRUCTURACIÓN COMPLETADA")
            print(f"📁 Archivo generado: {archivo_salida}")
            
        else:
            print("❌ No se pudieron reestructurar los datos")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
