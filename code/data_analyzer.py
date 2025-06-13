#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de análisis avanzado para el Analizador de Planillas de Ferretería
Incluye funcionalidades adicionales de procesamiento y análisis de datos
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
import numpy as np
from collections import Counter, defaultdict

class FerreteriaDataAnalyzer:
    def __init__(self, data_file=None):
        self.data = None
        self.processed_data = None
        
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, data_file):
        """Carga datos desde archivo JSON"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Datos cargados: {len(self.data.get('hojas', []))} hojas")
            return True
        except Exception as e:
            print(f"❌ Error cargando datos: {str(e)}")
            return False
    
    def extract_products_data(self):
        """Extrae y estructura los datos de productos"""
        if not self.data:
            return None
        
        products = []
        
        for hoja in self.data['hojas']:
            proveedor = hoja['hoja']
            
            for tabla in hoja['tablas']:
                if not tabla['filas']:
                    continue
                
                # Intentar identificar encabezados
                headers = self.identify_headers(tabla['filas'])
                data_rows = tabla['filas'][1:] if headers else tabla['filas']
                
                for row in data_rows[:1000]:  # Limitar para performance
                    if not any(cell.strip() for cell in row):
                        continue
                    
                    product = self.parse_product_row(row, headers, proveedor)
                    if product:
                        products.append(product)
        
        self.processed_data = pd.DataFrame(products)
        return self.processed_data
    
    def identify_headers(self, filas):
        """Identifica la fila de encabezados"""
        header_keywords = ['codigo', 'descripcion', 'precio', 'producto', 'numero', 'marca']
        
        for i, fila in enumerate(filas[:5]):
            text = ' '.join(fila).lower()
            matches = sum(1 for keyword in header_keywords if keyword in text)
            if matches >= 2:
                return fila
        
        return None
    
    def parse_product_row(self, row, headers, proveedor):
        """Parsea una fila de producto"""
        if len(row) < 2:
            return None
        
        product = {
            'proveedor': proveedor,
            'codigo': '',
            'descripcion': '',
            'precio': 0.0,
            'moneda': 'ARS',
            'marca': '',
            'stock': '',
            'categoria': ''
        }
        
        # Estrategias de parsing según el proveedor
        if proveedor == 'CRIMARAL':
            product.update(self.parse_crimaral_row(row))
        elif proveedor == 'ANCAIG':
            product.update(self.parse_ancaig_row(row))
        elif proveedor == 'HERRAMETAL':
            product.update(self.parse_herrametal_row(row))
        else:
            product.update(self.parse_generic_row(row))
        
        # Categorización automática
        product['categoria'] = self.categorize_product(product['descripcion'])
        
        return product if product['descripcion'] else None
    
    def parse_crimaral_row(self, row):
        """Parser específico para CRIMARAL"""
        return {
            'codigo': row[0] if len(row) > 0 else '',
            'descripcion': row[1] if len(row) > 1 else '',
            'marca': row[2] if len(row) > 2 else '',
            'precio': self.extract_price(row[3] if len(row) > 3 else ''),
            'moneda': 'USD'
        }
    
    def parse_ancaig_row(self, row):
        """Parser específico para ANCAIG"""
        return {
            'codigo': row[0] if len(row) > 0 else '',
            'descripcion': row[1] if len(row) > 1 else '',
            'precio': self.extract_price(row[3] if len(row) > 3 else ''),
            'moneda': 'ARS'
        }
    
    def parse_herrametal_row(self, row):
        """Parser específico para HERRAMETAL"""
        return {
            'codigo': row[0] if len(row) > 0 else '',
            'descripcion': row[1] if len(row) > 1 else '',
            'precio': self.extract_price(row[3] if len(row) > 3 else ''),
            'moneda': 'ARS'
        }
    
    def parse_generic_row(self, row):
        """Parser genérico"""
        return {
            'codigo': row[0] if len(row) > 0 else '',
            'descripcion': row[1] if len(row) > 1 else '',
            'precio': self.extract_price(row[2] if len(row) > 2 else ''),
            'moneda': 'ARS'
        }
    
    def extract_price(self, price_text):
        """Extrae precio numérico del texto"""
        if not price_text:
            return 0.0
        
        # Remover símbolos de moneda y espacios
        price_clean = re.sub(r'[^\d,.]', '', str(price_text))
        
        # Convertir comas a puntos para decimales
        price_clean = price_clean.replace(',', '.')
        
        try:
            return float(price_clean)
        except:
            return 0.0
    
    def categorize_product(self, descripcion):
        """Categoriza productos automáticamente"""
        if not descripcion:
            return 'Sin categoría'
        
        desc_lower = descripcion.lower()
        
        categories = {
            'Riego': ['aspersor', 'manguera', 'riego', 'goteo', 'spray'],
            'Herramientas': ['llave', 'destornillador', 'martillo', 'alicate', 'pinza'],
            'Químicos': ['diluyente', 'solvente', 'pintura', 'barniz', 'thinner'],
            'Aceites': ['aceite', 'lubricante', 'grasa', 'fluido'],
            'Plásticos': ['abrazadera', 'tubo', 'caño', 'conexión', 'fitting'],
            'Herrajes': ['tornillo', 'tuerca', 'arandela', 'bulón', 'clavo'],
            'Eléctrico': ['cable', 'interruptor', 'enchufe', 'lámpara', 'led'],
            'Construcción': ['cemento', 'arena', 'ladrillos', 'cal', 'yeso']
        }
        
        for category, keywords in categories.items():
            if any(keyword in desc_lower for keyword in keywords):
                return category
        
        return 'Otros'
    
    def generate_price_analysis(self):
        """Genera análisis de precios"""
        if self.processed_data is None:
            self.extract_products_data()
        
        if self.processed_data.empty:
            return "No hay datos procesados para analizar"
        
        df = self.processed_data
        analysis = []
        
        # Estadísticas generales
        analysis.append("📊 ANÁLISIS DE PRECIOS")
        analysis.append("=" * 50)
        
        # Por proveedor
        analysis.append("\n🏪 ANÁLISIS POR PROVEEDOR:")
        for proveedor in df['proveedor'].unique():
            prov_data = df[df['proveedor'] == proveedor]
            prices = prov_data[prov_data['precio'] > 0]['precio']
            
            if not prices.empty:
                analysis.append(f"\n{proveedor}:")
                analysis.append(f"  • Productos: {len(prov_data)}")
                analysis.append(f"  • Precio promedio: ${prices.mean():.2f}")
                analysis.append(f"  • Precio mínimo: ${prices.min():.2f}")
                analysis.append(f"  • Precio máximo: ${prices.max():.2f}")
        
        # Por categoría
        analysis.append("\n📂 ANÁLISIS POR CATEGORÍA:")
        for categoria in df['categoria'].unique():
            cat_data = df[df['categoria'] == categoria]
            prices = cat_data[cat_data['precio'] > 0]['precio']
            
            if not prices.empty:
                analysis.append(f"\n{categoria}:")
                analysis.append(f"  • Productos: {len(cat_data)}")
                analysis.append(f"  • Precio promedio: ${prices.mean():.2f}")
        
        # Top productos más caros
        analysis.append("\n💰 TOP 10 PRODUCTOS MÁS CAROS:")
        top_expensive = df.nlargest(10, 'precio')[['descripcion', 'proveedor', 'precio']]
        for idx, row in top_expensive.iterrows():
            analysis.append(f"  {row['descripcion'][:50]}... - {row['proveedor']} - ${row['precio']:.2f}")
        
        return "\n".join(analysis)
    
    def generate_supplier_comparison(self):
        """Genera comparación entre proveedores"""
        if self.processed_data is None:
            self.extract_products_data()
        
        df = self.processed_data
        comparison = []
        
        comparison.append("🔄 COMPARACIÓN DE PROVEEDORES")
        comparison.append("=" * 50)
        
        # Tabla comparativa
        for proveedor in df['proveedor'].unique():
            prov_data = df[df['proveedor'] == proveedor]
            total_products = len(prov_data)
            avg_price = prov_data[prov_data['precio'] > 0]['precio'].mean()
            categories = prov_data['categoria'].nunique()
            
            comparison.append(f"\n{proveedor}:")
            comparison.append(f"  📦 Total productos: {total_products}")
            comparison.append(f"  💰 Precio promedio: ${avg_price:.2f}")
            comparison.append(f"  📂 Categorías: {categories}")
            
            # Top 3 categorías
            top_cats = prov_data['categoria'].value_counts().head(3)
            comparison.append("  📋 Top categorías:")
            for cat, count in top_cats.items():
                comparison.append(f"     • {cat}: {count} productos")
        
        return "\n".join(comparison)
    
    def find_similar_products(self, search_term, limit=10):
        """Encuentra productos similares"""
        if self.processed_data is None:
            self.extract_products_data()
        
        df = self.processed_data
        search_lower = search_term.lower()
        
        # Buscar en descripciones
        matches = df[df['descripcion'].str.lower().str.contains(search_lower, na=False)]
        
        if matches.empty:
            return f"No se encontraron productos con '{search_term}'"
        
        results = []
        results.append(f"🔍 PRODUCTOS SIMILARES A '{search_term}':")
        results.append("=" * 50)
        
        for idx, row in matches.head(limit).iterrows():
            results.append(f"\n📦 {row['descripcion']}")
            results.append(f"    🏪 Proveedor: {row['proveedor']}")
            results.append(f"    💰 Precio: ${row['precio']:.2f} {row['moneda']}")
            results.append(f"    📂 Categoría: {row['categoria']}")
            if row['codigo']:
                results.append(f"    🏷️ Código: {row['codigo']}")
        
        return "\n".join(results)
    
    def export_processed_data(self, filename):
        """Exporta datos procesados"""
        if self.processed_data is None:
            self.extract_products_data()
        
        try:
            if filename.endswith('.xlsx'):
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    self.processed_data.to_excel(writer, sheet_name='Productos', index=False)
                    
                    # Hoja de resumen por proveedor
                    summary = self.processed_data.groupby('proveedor').agg({
                        'precio': ['count', 'mean', 'min', 'max'],
                        'categoria': 'nunique'
                    }).round(2)
                    summary.to_excel(writer, sheet_name='Resumen_Proveedores')
                    
                    # Hoja de resumen por categoría
                    cat_summary = self.processed_data.groupby('categoria').agg({
                        'precio': ['count', 'mean', 'min', 'max']
                    }).round(2)
                    cat_summary.to_excel(writer, sheet_name='Resumen_Categorias')
            
            elif filename.endswith('.csv'):
                self.processed_data.to_csv(filename, index=False, encoding='utf-8')
            
            elif filename.endswith('.json'):
                self.processed_data.to_json(filename, orient='records', force_ascii=False, indent=2)
            
            return f"✅ Datos exportados a: {filename}"
            
        except Exception as e:
            return f"❌ Error exportando: {str(e)}"
    
    def generate_visualizations(self, output_dir):
        """Genera visualizaciones de datos"""
        if self.processed_data is None:
            self.extract_products_data()
        
        df = self.processed_data
        plt.style.use('seaborn-v0_8')
        
        # 1. Distribución de productos por proveedor
        plt.figure(figsize=(12, 6))
        supplier_counts = df['proveedor'].value_counts()
        plt.bar(range(len(supplier_counts)), supplier_counts.values)
        plt.xticks(range(len(supplier_counts)), supplier_counts.index, rotation=45)
        plt.title('Distribución de Productos por Proveedor')
        plt.ylabel('Cantidad de Productos')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/productos_por_proveedor.png")
        plt.close()
        
        # 2. Distribución de precios
        plt.figure(figsize=(10, 6))
        prices = df[df['precio'] > 0]['precio']
        plt.hist(prices, bins=50, edgecolor='black', alpha=0.7)
        plt.title('Distribución de Precios')
        plt.xlabel('Precio')
        plt.ylabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/distribucion_precios.png")
        plt.close()
        
        # 3. Productos por categoría
        plt.figure(figsize=(10, 8))
        category_counts = df['categoria'].value_counts()
        plt.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        plt.title('Distribución por Categorías')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/productos_por_categoria.png")
        plt.close()
        
        return "✅ Visualizaciones generadas"

def analizar_datos_con_ia(datos, api_key=None, custom_prompt=None):
    """
    Función wrapper para analizar datos con IA
    Compatible con la aplicación modular
    
    Args:
        datos: Datos de productos para analizar
        api_key: API key de Google Gemini (opcional)
        custom_prompt: Prompt personalizado para el análisis (opcional)
    """
    try:
        from datetime import datetime
        
        # Crear analizador temporal
        analyzer = FerreteriaDataAnalyzer()
        
        # Convertir datos al formato esperado por el analizador
        productos_para_analisis = []
        
        if isinstance(datos, dict) and 'hojas' in datos:
            for hoja in datos['hojas']:
                if 'productos' in hoja:
                    for producto in hoja['productos']:
                        # Adaptar formato del producto
                        producto_adaptado = {
                            'descripcion': producto.get('descripcion', ''),
                            'precio': producto.get('precio', ''),
                            'codigo': producto.get('codigo', ''),
                            'proveedor': producto.get('proveedor', hoja.get('nombre', 'Desconocido')),
                            'categoria': producto.get('categoria', 'General')
                        }
                        productos_para_analisis.append(producto_adaptado)
        
        # Simular análisis básico
        total_productos = len(productos_para_analisis)
          # Si se proporciona API key, usar análisis con IA real
        if api_key:
            print(f"🤖 Iniciando análisis con IA para {total_productos} productos...")
            try:
                return _analizar_con_gemini(productos_para_analisis, api_key, custom_prompt)
            except Exception as e:
                print(f"❌ Error en análisis con IA: {e}")
                print("🔄 Fallback a análisis básico...")
                return _analizar_basico(productos_para_analisis)
        
        # Análisis básico sin IA (fallback)
        print(f"📊 Análisis básico para {total_productos} productos...")
        return _analizar_basico(productos_para_analisis)
    except Exception as e:
        print(f"Error en analizar_datos_con_ia: {e}")
        return {
            'resumen_general': {'total_productos': 0},
            'recomendaciones': ["Error durante el análisis"],
            'fecha_analisis': datetime.now().isoformat() if 'datetime' in locals() else ''
        }

def _analizar_con_gemini(productos, api_key, custom_prompt=None):
    """Análisis usando Google Gemini AI"""
    try:
        print("🔍 Intentando importar google.generativeai...")
        import google.generativeai as genai
        print("✅ google.generativeai importado correctamente")
        
        print("🔑 Configurando API key...")
        # Configurar Gemini
        genai.configure(api_key=api_key)
        print("✅ API key configurada")
        
        print("🤖 Inicializando modelo Gemini...")
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Modelo inicializado")
        
        print(f"📊 Preparando datos ({len(productos)} productos)...")
        # Preparar datos para el prompt
        productos_sample = productos[:50]  # Reducir muestra para evitar límites
        productos_texto = ""
        
        for i, producto in enumerate(productos_sample, 1):
            productos_texto += f"{i}. "
            productos_texto += f"Descripción: {producto.get('descripcion', 'Sin descripción')}, "
            productos_texto += f"Precio: ${producto.get('precio', 'N/A')}, "
            productos_texto += f"Código: {producto.get('codigo', 'N/A')}, "
            productos_texto += f"Proveedor: {producto.get('proveedor', 'N/A')}\n"
        
        print("📝 Generando prompt...")
        # Usar prompt personalizado o por defecto
        if custom_prompt:
            prompt = custom_prompt.format(productos_data=productos_texto)
        else:
            prompt = f"""
            Analiza los siguientes {len(productos)} productos de ferretería. Muestra analizada: {len(productos_sample)} productos.

            DATOS DE PRODUCTOS:
            {productos_texto}

            Proporciona un análisis en formato JSON con estas claves:
            {{
                "resumen_general": {{
                    "total_productos": {len(productos)},
                    "rango_precios": "rango detectado",
                    "categoria_principal": "categoría más común"
                }},
                "recomendaciones": ["rec1", "rec2", "rec3"],
                "insights": ["insight1", "insight2"]            }}
            """
        
        print("🚀 Enviando petición a Gemini (timeout: 30s)...")
        # Generar análisis con timeout
        import threading
        import time
        
        result = {'response': None, 'error': None}
        
        def generate_content():
            try:
                result['response'] = model.generate_content(prompt)
            except Exception as e:
                result['error'] = str(e)
        
        # Ejecutar con timeout
        thread = threading.Thread(target=generate_content)
        thread.start()
        thread.join(timeout=30)  # 30 segundos de timeout
        
        if thread.is_alive():
            print("⚠️ Timeout en petición a Gemini, usando análisis básico...")
            return _analizar_basico(productos)
        
        if result['error']:
            print(f"❌ Error en Gemini: {result['error']}")
            return _analizar_basico(productos)
        
        if not result['response']:
            print("❌ No se recibió respuesta de Gemini")
            return _analizar_basico(productos)
        
        response = result['response']
        print("✅ Respuesta recibida de Gemini")
        
        print("🔍 Procesando respuesta...")
        # Procesar respuesta
        try:
            import json
            import re
            
            # Extraer JSON de la respuesta
            response_text = response.text
            
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group())
                
                # Agregar metadatos
                analysis_json['metadata'] = {
                    'total_productos_analizados': len(productos),
                    'muestra_analizada': len(productos_sample),
                    'fecha_analisis': datetime.now().isoformat(),
                    'motor_ia': 'Google Gemini',
                    'prompt_personalizado': bool(custom_prompt)
                }
                
                return analysis_json
            else:
                # Si no hay JSON válido, crear estructura básica con la respuesta
                return {
                    'resumen_general': {
                        'total_productos': len(productos),
                        'analisis_ia': response_text[:500] + "..." if len(response_text) > 500 else response_text
                    },
                    'recomendaciones': ["Análisis completado con IA"],
                    'metadata': {
                        'total_productos_analizados': len(productos),
                        'fecha_analisis': datetime.now().isoformat(),
                        'motor_ia': 'Google Gemini',
                        'respuesta_completa': response_text
                    }
                }
                
        except Exception as json_error:
            # Si falla el parsing JSON, devolver respuesta como texto
            return {
                'resumen_general': {
                    'total_productos': len(productos),
                    'analisis_ia': response.text
                },
                'recomendaciones': ["Análisis completado con IA (formato libre)"],
                'metadata': {
                    'total_productos_analizados': len(productos),
                    'fecha_analisis': datetime.now().isoformat(),
                    'motor_ia': 'Google Gemini',
                    'nota': f"Respuesta en formato libre: {json_error}"
                }
            }
        
    except Exception as e:
        # Si falla la IA, devolver análisis básico
        print(f"Error en análisis con IA: {e}")
        return _analizar_basico(productos)

def _analizar_basico(productos_para_analisis):
    """Análisis básico sin IA"""
    try:
        from datetime import datetime
        
        total_productos = len(productos_para_analisis)
        
        # Análisis básico de precios
        precios_validos = []
        for producto in productos_para_analisis:
            try:
                precio_str = str(producto.get('precio', '0')).replace(',', '.')
                precio_num = float(precio_str)
                if precio_num > 0:
                    precios_validos.append(precio_num)
            except:
                continue
        
        if precios_validos:
            precio_min = min(precios_validos)
            precio_max = max(precios_validos)
            precio_promedio = sum(precios_validos) / len(precios_validos)
        else:
            precio_min = precio_max = precio_promedio = 0
        
        # Generar análisis
        analisis = {
            'resumen_general': {
                'total_productos': total_productos,
                'productos_con_precio': len(precios_validos),
                'rango_precios': f"${precio_min:.2f} - ${precio_max:.2f}",
                'precio_promedio': f"${precio_promedio:.2f}"
            },
            'categorias': {},
            'recomendaciones': [
                "Revisar productos sin precio asignado",
                "Verificar consistencia en códigos de productos",
                "Considerar análisis de competitividad de precios"
            ],
            'fecha_analisis': datetime.now().isoformat()
        }
        
        # Análisis por categorías
        categorias = {}
        for producto in productos_para_analisis:
            categoria = producto.get('categoria', 'General')
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(producto)
        
        analisis['categorias'] = {
            cat: {
                'total_productos': len(prods),
                'productos_destacados': prods[:3]  # Primeros 3 productos
            }
            for cat, prods in categorias.items()
        }
        
        return analisis
        
    except Exception as e:
        print(f"Error en analizar_datos_con_ia: {e}")
        return {
            'resumen_general': {'total_productos': 0},
            'recomendaciones': ["Error durante el análisis"],
            'fecha_analisis': datetime.now().isoformat()
        }

def main():
    """Función principal para testing"""
    analyzer = FerreteriaDataAnalyzer()
    
    # Ejemplo de uso
    print("Analizador de Datos de Ferretería")
    print("=================================")
    
    # Cargar datos de ejemplo (reemplazar con ruta real)
    # analyzer.load_data("datos_estructurados.json")
    # analyzer.extract_products_data()
    # print(analyzer.generate_price_analysis())

if __name__ == "__main__":
    main()
