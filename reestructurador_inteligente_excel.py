#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REESTRUCTURADOR INTELIGENTE DE DATOS PARA EXCEL
===============================================
Analiza el JSON estructurado y reorganiza los datos de manera inteligente
antes de exportar a Excel, identificando correctamente tipos de datos
"""

import json
import pandas as pd
import re
import os
from datetime import datetime
from analizador_datos_inteligente import AnalizadorDatosInteligente

class ReestructuradorInteligenteExcel:
    def __init__(self):
        self.analizador = AnalizadorDatosInteligente()
        self.tipos_columna = {
            'CODIGO': ['codigo', 'sku', 'ref', 'art', 'item'],
            'DESCRIPCION': ['descripcion', 'producto', 'articulo', 'detalle'],
            'PRECIO': ['precio', 'cost', 'valor', 'importe'],
            'CANTIDAD': ['cantidad', 'stock', 'qty', 'unidades'],
            'MARCA': ['marca', 'brand', 'fabricante'],
            'CATEGORIA': ['categoria', 'tipo', 'rubro', 'familia'],
            'UNIDAD': ['unidad', 'medida', 'um', 'unit'],
            'MONEDA': ['moneda', 'currency', 'divisa'],
            'PROVEEDOR': ['proveedor', 'supplier', 'distribuidor']
        }
    
    def reestructurar_datos_inteligente(self, ruta_json_datos):
        """Reestructura los datos del JSON de manera inteligente para Excel"""
        print("🧠 INICIANDO REESTRUCTURACIÓN INTELIGENTE DE DATOS")
        print("=" * 55)
        
        # Cargar datos originales
        with open(ruta_json_datos, 'r', encoding='utf-8') as f:
            datos_originales = json.load(f)
        
        # Realizar análisis inteligente
        print("🔍 Analizando datos con AnalizadorDatosInteligente...")
        analisis = self.analizador.analizar_datos_estructurados(ruta_json_datos)
        
        if not analisis:
            print("❌ No se pudo realizar el análisis inteligente")
            return None
        
        print("✅ Análisis completado. Reestructurando datos...")
        
        # Reestructurar por proveedor
        datos_reestructurados = {}
        
        for hoja in datos_originales.get('hojas', []):
            nombre_hoja = hoja.get('hoja', '')
            proveedor = self._identificar_proveedor(nombre_hoja, analisis)
            
            print(f"📋 Procesando: {nombre_hoja} → Proveedor: {proveedor}")
            
            datos_estructurados = self._procesar_hoja_inteligente(hoja, proveedor, analisis)
            
            if datos_estructurados:
                if proveedor not in datos_reestructurados:
                    datos_reestructurados[proveedor] = []
                datos_reestructurados[proveedor].extend(datos_estructurados)
        
        # Generar DataFrames optimizados por proveedor
        dfs_optimizados = {}
        for proveedor, productos in datos_reestructurados.items():
            if productos:
                df = self._crear_dataframe_optimizado(productos, proveedor)
                dfs_optimizados[proveedor] = df
                print(f"✅ {proveedor}: {len(df)} productos estructurados")
        
        return dfs_optimizados
    
    def _identificar_proveedor(self, nombre_hoja, analisis):
        """Identifica el proveedor de la hoja usando el análisis inteligente"""
        proveedores_conocidos = analisis.get('proveedores_identificados', {})
        
        # Buscar proveedor en el nombre de la hoja
        for proveedor in proveedores_conocidos.keys():
            if proveedor.upper() in nombre_hoja.upper():
                return proveedor
        
        # Si no se encuentra, extraer del nombre de la hoja
        if '_' in nombre_hoja:
            return nombre_hoja.split('_')[0]
        
        return nombre_hoja
    
    def _procesar_hoja_inteligente(self, hoja, proveedor, analisis):
        """Procesa una hoja identificando inteligentemente cada columna"""
        productos_estructurados = []
        
        for tabla in hoja.get('tablas', []):
            filas = tabla.get('filas', [])
            if not filas:
                continue
            
            # Analizar la primera fila para identificar encabezados
            posible_encabezado = filas[0] if filas else []
            mapa_columnas = self._mapear_columnas_inteligente(posible_encabezado)
            
            # Determinar si la primera fila es encabezado
            es_encabezado = self._es_fila_encabezado(posible_encabezado)
            inicio_datos = 1 if es_encabezado else 0
            
            print(f"   📊 Tabla con {len(filas)} filas, encabezado: {es_encabezado}")
            print(f"   🗂️  Columnas mapeadas: {len(mapa_columnas)}")
            
            # Procesar cada fila de datos
            for i, fila in enumerate(filas[inicio_datos:], inicio_datos):
                producto = self._extraer_producto_inteligente(
                    fila, mapa_columnas, proveedor, posible_encabezado if es_encabezado else None
                )
                
                if producto and self._es_producto_valido(producto):
                    productos_estructurados.append(producto)
        
        return productos_estructurados
    
    def _mapear_columnas_inteligente(self, fila_encabezado):
        """Mapea inteligentemente las columnas basándose en contenido"""
        mapa = {}
        
        for i, celda in enumerate(fila_encabezado):
            if not celda:
                continue
                
            celda_str = str(celda).strip().upper()
            
            # Identificar tipo de columna por contenido
            for tipo, palabras_clave in self.tipos_columna.items():
                for palabra in palabras_clave:
                    if palabra.upper() in celda_str:
                        mapa[i] = tipo
                        break
                if i in mapa:
                    break
            
            # Si no se identifica, usar heurísticas adicionales
            if i not in mapa:
                if any(palabra in celda_str for palabra in ['$', 'PESO', 'DOLAR', 'USD', 'ARS']):
                    mapa[i] = 'PRECIO'
                elif any(palabra in celda_str for palabra in ['COD', 'SKU', 'REF']):
                    mapa[i] = 'CODIGO'
                elif len(celda_str) > 10:  # Descripción larga
                    mapa[i] = 'DESCRIPCION'
        
        return mapa
    
    def _es_fila_encabezado(self, fila):
        """Determina si una fila es encabezado basándose en patrones"""
        if not fila:
            return False
        
        texto_fila = ' '.join(str(celda).upper() for celda in fila if celda)
        
        # Palabras típicas de encabezados
        palabras_encabezado = [
            'CODIGO', 'DESCRIPCION', 'PRECIO', 'CANTIDAD', 'STOCK',
            'PRODUCTO', 'ARTICULO', 'COSTO', 'MARCA', 'MODELO'
        ]
        
        coincidencias = sum(1 for palabra in palabras_encabezado if palabra in texto_fila)
        
        # Si tiene muchas palabras típicas de encabezado, probablemente lo sea
        return coincidencias >= 2
    
    def _extraer_producto_inteligente(self, fila, mapa_columnas, proveedor, encabezados=None):
        """Extrae un producto de una fila usando mapeo inteligente"""
        producto = {
            'PROVEEDOR': proveedor,
            'CODIGO': None,
            'DESCRIPCION': None,
            'PRECIO': None,
            'CANTIDAD': None,
            'MARCA': None,
            'CATEGORIA': None,
            'UNIDAD': None,
            'MONEDA': None,
            'FILA_ORIGINAL': fila[:10]  # Para referencia
        }
        
        # Usar mapeo de columnas si existe
        for i, celda in enumerate(fila):
            if i in mapa_columnas and celda:
                tipo_columna = mapa_columnas[i]
                valor_limpio = self._limpiar_valor(celda, tipo_columna)
                if valor_limpio:
                    producto[tipo_columna] = valor_limpio
        
        # Si no hay mapeo, usar análisis de contenido
        if not any(producto[k] for k in ['CODIGO', 'DESCRIPCION', 'PRECIO']):
            producto = self._analizar_fila_sin_mapeo(fila, proveedor)
        
        # Post-procesamiento inteligente
        producto = self._mejorar_producto_post_analisis(producto)
        
        return producto
    
    def _analizar_fila_sin_mapeo(self, fila, proveedor):
        """Analiza una fila sin mapeo de columnas usando patrones"""
        producto = {
            'PROVEEDOR': proveedor,
            'CODIGO': None,
            'DESCRIPCION': None,
            'PRECIO': None,
            'CANTIDAD': None,
            'MARCA': None,
            'CATEGORIA': None,
            'UNIDAD': None,
            'MONEDA': None,
            'FILA_ORIGINAL': fila[:10]
        }
        
        descripcion_candidata = ""
        
        for celda in fila:
            if not celda:
                continue
                
            celda_str = str(celda).strip()
            
            # Detectar precios
            if not producto['PRECIO'] and self._es_precio(celda_str):
                precio_info = self._extraer_precio_y_moneda(celda_str)
                producto['PRECIO'] = precio_info['precio']
                producto['MONEDA'] = precio_info['moneda']
            
            # Detectar códigos
            elif not producto['CODIGO'] and self._es_codigo(celda_str):
                producto['CODIGO'] = celda_str
            
            # Detectar cantidades
            elif not producto['CANTIDAD'] and self._es_cantidad(celda_str):
                cantidad_info = self._extraer_cantidad_y_unidad(celda_str)
                producto['CANTIDAD'] = cantidad_info['cantidad']
                producto['UNIDAD'] = cantidad_info['unidad']
            
            # Acumular para descripción
            elif len(celda_str) > 3:
                if descripcion_candidata:
                    descripcion_candidata += " " + celda_str
                else:
                    descripcion_candidata = celda_str
        
        # Asignar descripción si no se encontró una específica
        if not producto['DESCRIPCION'] and descripcion_candidata:
            producto['DESCRIPCION'] = descripcion_candidata[:200]  # Limitar longitud
        
        return producto
    
    def _es_precio(self, texto):
        """Determina si un texto contiene un precio"""
        patrones_precio = [
            r'\$\s*[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*\$',
            r'ARS\s*[\d,]+\.?\d*',
            r'USD\s*[\d,]+\.?\d*',
            r'PESO[\S\s]*[\d,]+',
            r'DOLAR[\S\s]*[\d,]+'
        ]
        
        return any(re.search(patron, texto, re.IGNORECASE) for patron in patrones_precio)
    
    def _es_codigo(self, texto):
        """Determina si un texto es un código de producto"""
        # Códigos típicos: letras y números, guiones, etc.
        patrones_codigo = [
            r'^[A-Z]{2,}\d{3,}$',  # ABC123
            r'^\d{3,}[A-Z]{2,}$',  # 123ABC
            r'^[A-Z0-9\-]{4,15}$', # ABC-123-XYZ
            r'^STN\d+$',           # STN7418
        ]
        
        texto_limpio = texto.strip().upper()
        return any(re.match(patron, texto_limpio) for patron in patrones_codigo)
    
    def _es_cantidad(self, texto):
        """Determina si un texto contiene cantidad"""
        patrones_cantidad = [
            r'STOCK[\s:]*\d+',
            r'QTY[\s:]*\d+',
            r'\d+\s*(UND|UNIT|PCS|KG|GR|LT|ML)',
            r'x\s*\d+'
        ]
        
        return any(re.search(patron, texto, re.IGNORECASE) for patron in patrones_cantidad)
    
    def _extraer_precio_y_moneda(self, texto):
        """Extrae precio y moneda de un texto"""
        resultado = {'precio': None, 'moneda': None}
        
        # Buscar patrones de precio con moneda
        patrones = [
            (r'\$\s*([\d,]+\.?\d*)', 'USD'),
            (r'USD\s*([\d,]+\.?\d*)', 'USD'),
            (r'ARS\s*([\d,]+\.?\d*)', 'ARS'),
            (r'PESO[\S\s]*([\d,]+\.?\d*)', 'ARS'),
            (r'([\d,]+\.?\d*)\s*\$', 'USD'),
            (r'([\d,]+\.?\d*)', 'ARS')  # Por defecto ARS si no se especifica
        ]
        
        for patron, moneda in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                precio_str = match.group(1).replace(',', '')
                try:
                    precio = float(precio_str)
                    resultado['precio'] = precio
                    resultado['moneda'] = moneda
                    break
                except ValueError:
                    continue
        
        return resultado
    
    def _extraer_cantidad_y_unidad(self, texto):
        """Extrae cantidad y unidad de un texto"""
        resultado = {'cantidad': None, 'unidad': None}
        
        patrones = [
            (r'(\d+)\s*(UND|UNIT|PCS)', r'\1', r'\2'),
            (r'(\d+)\s*(KG|GR|LT|ML)', r'\1', r'\2'),
            (r'STOCK[\s:]*(\d+)', r'\1', 'UND'),
            (r'x\s*(\d+)', r'\1', 'UND')
        ]
        
        for patron_cantidad, grupo_cant, grupo_unidad in patrones:
            match = re.search(patron_cantidad, texto, re.IGNORECASE)
            if match:
                try:
                    resultado['cantidad'] = int(match.group(1))
                    if isinstance(grupo_unidad, str):
                        resultado['unidad'] = grupo_unidad
                    else:
                        resultado['unidad'] = match.group(2) if match.lastindex >= 2 else 'UND'
                    break                
                except (ValueError, IndexError):
                    continue
        
        return resultado
    
    def _limpiar_valor(self, valor, tipo_columna):
        """Limpia un valor según su tipo de columna"""
        if not valor:
            return None
        
        valor_str = str(valor).strip()
        
        # Limpiar caracteres problemáticos para Excel
        caracteres_problematicos = ['☻', '☺', '♠', '♣', '♥', '♦', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08']
        for char in caracteres_problematicos:
            valor_str = valor_str.replace(char, '')
        
        if tipo_columna == 'PRECIO':
            precio_info = self._extraer_precio_y_moneda(valor_str)
            return precio_info['precio']
        elif tipo_columna == 'CODIGO':
            return valor_str.upper()
        elif tipo_columna == 'DESCRIPCION':
            return valor_str[:200]  # Limitar longitud
        elif tipo_columna == 'CANTIDAD':
            cantidad_info = self._extraer_cantidad_y_unidad(valor_str)
            return cantidad_info['cantidad']
        else:
            return valor_str
    
    def _mejorar_producto_post_analisis(self, producto):
        """Mejora el producto después del análisis inicial"""
        # Si no hay descripción pero hay código, usar código como base
        if not producto['DESCRIPCION'] and producto['CODIGO']:
            producto['DESCRIPCION'] = producto['CODIGO']
        
        # Detectar marca en la descripción
        if producto['DESCRIPCION'] and not producto['MARCA']:
            marcas_conocidas = ['STANLEY', 'DEWALT', 'MAKITA', 'BOSCH', 'TRUPER', 'BAHCO']
            for marca in marcas_conocidas:
                if marca in producto['DESCRIPCION'].upper():
                    producto['MARCA'] = marca
                    break
        
        # Asignar moneda por defecto si hay precio sin moneda
        if producto['PRECIO'] and not producto['MONEDA']:
            producto['MONEDA'] = 'ARS'
        
        return producto
    
    def _es_producto_valido(self, producto):
        """Determina si un producto tiene datos suficientes para ser válido"""
        # Un producto es válido si tiene al menos descripción o código
        return bool(producto.get('DESCRIPCION') or producto.get('CODIGO'))
    def _crear_dataframe_optimizado(self, productos, proveedor):
        """Crea un DataFrame optimizado para el proveedor"""
        if not productos:
            return pd.DataFrame()
        
        # Definir columnas estándar
        columnas_ordenadas = [
            'PROVEEDOR', 'CODIGO', 'DESCRIPCION', 'PRECIO', 'MONEDA',
            'CANTIDAD', 'UNIDAD', 'MARCA', 'CATEGORIA'
        ]
        
        # Crear DataFrame
        df = pd.DataFrame(productos)
        
        # Limpiar caracteres problemáticos en todas las columnas de texto
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).apply(self._limpiar_caracteres_excel)
        
        # Reordenar columnas
        columnas_existentes = [col for col in columnas_ordenadas if col in df.columns]
        df = df[columnas_existentes]
        
        # Limpiar datos
        df = df.dropna(subset=['DESCRIPCION'], how='all')  # Eliminar filas sin descripción
        df = df.drop_duplicates(subset=['CODIGO', 'DESCRIPCION'], keep='first')  # Eliminar duplicados
        
        # Ordenar por código y descripción
        df = df.sort_values(['CODIGO', 'DESCRIPCION'], na_position='last')
        
        return df
    
    def _limpiar_caracteres_excel(self, texto):
        """Limpia caracteres problemáticos para Excel"""
        if pd.isna(texto) or texto == 'nan':
            return None
        
        texto_str = str(texto)
        
        # Caracteres problemáticos para Excel
        caracteres_problematicos = ['☻', '☺', '♠', '♣', '♥', '♦', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x0B', '\x0C', '\x0E', '\x0F', '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1A', '\x1B', '\x1C', '\x1D', '\x1E', '\x1F']
        
        for char in caracteres_problematicos:
            texto_str = texto_str.replace(char, '')
        
        # Limpiar caracteres de control adicionales
        texto_str = ''.join(char for char in texto_str if ord(char) >= 32 or char in '\t\n\r')
        
        return texto_str.strip() if texto_str.strip() else None
    
    def exportar_excel_reestructurado(self, dfs_optimizados, ruta_salida):
        """Exporta los DataFrames reestructurados a Excel"""
        print(f"\n📊 EXPORTANDO EXCEL REESTRUCTURADO: {ruta_salida}")
        print("=" * 50)
        
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            # Crear hoja de resumen
            resumen_data = []
            for proveedor, df in dfs_optimizados.items():
                resumen_data.append({
                    'PROVEEDOR': proveedor,
                    'PRODUCTOS': len(df),
                    'CON_PRECIO': len(df[df['PRECIO'].notna()]) if 'PRECIO' in df.columns else 0,
                    'CON_CODIGO': len(df[df['CODIGO'].notna()]) if 'CODIGO' in df.columns else 0,
                    'CALIDAD_DATOS': f"{(len(df[df['PRECIO'].notna()]) / len(df) * 100):.1f}%" if 'PRECIO' in df.columns and len(df) > 0 else "0%"
                })
            
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='RESUMEN', index=False)
            print("✅ Hoja RESUMEN creada")
            
            # Exportar cada proveedor
            for proveedor, df in dfs_optimizados.items():
                nombre_hoja = proveedor[:31]  # Límite de Excel
                df.to_excel(writer, sheet_name=nombre_hoja, index=False)
                print(f"✅ {proveedor}: {len(df)} productos exportados")
        
        print(f"\n🎉 EXCEL REESTRUCTURADO GUARDADO: {ruta_salida}")
        return ruta_salida

def main():
    """Función de prueba"""
    reestructurador = ReestructuradorInteligenteExcel()
    
    archivo_datos = "datos_extraidos_app.json"
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró {archivo_datos}")
        return
    
    # Reestructurar datos
    dfs_optimizados = reestructurador.reestructurar_datos_inteligente(archivo_datos)
    
    if dfs_optimizados:
        # Exportar a Excel
        ruta_salida = f"ferreteria_reestructurada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        reestructurador.exportar_excel_reestructurado(dfs_optimizados, ruta_salida)
    else:
        print("❌ No se pudieron reestructurar los datos")

if __name__ == "__main__":
    main()
