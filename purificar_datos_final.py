#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final para purificar datos JSON de ferretería
Versión optimizada que extrae solo información de productos relevantes
"""

import json
import re
from datetime import datetime


class PurificadorFinal:
    def __init__(self):
        # Patrones para identificar filas irrelevantes
        self.patrones_irrelevantes = [
            r'BUSCADOR RAPIDO',
            r'distribuidora.*@.*\.com',
            r'Precios orientativos',
            r'CALCULADORA',
            r'COMPLETAR DONDE',
            r'FUNCIONAMIENTO',
            r'INGRESAR.*CENTIMETROS',
            r'MARGEN DE GANANCIA',
            r'POR DEFECTO',
            r'Recuerde que',
            r'UwU',
            r'AQU VER LA',
            r'CODIGO.*DESCRIPCION.*BASE',
            r'ESCRIBA AQUI MISMO',
            r'DIAMETRO DEL',
            r'CUANTO COBRAR',
            r'PESTAA para actualizacion',
            r'^YAYI$',
            r'^DESCRIPCION$',
            r'^CODIGO$',
            r'^BASE$',
            r'^PUBLICO$',
            r'^\.$',
            r'^-$',
            r'^\+$',
            r'OFERTAS',
            r'FECHA',
            r'% GANANCIA',
            r'SIN IVA',
            r'COSTO FINAL',
            r'CON OFERTAS'
        ]
        
        # Patrones para identificar campos específicos
        self.patron_codigo = re.compile(r'^[0-9]{6,8}$')
        self.patron_precio = re.compile(r'^[\d\.,]+$')
        self.patron_moneda = re.compile(r'[\$\s]*[\d\.,]+')
        self.patron_iva = re.compile(r'^[0-9]{1,2}$')
        self.patron_medida = re.compile(r'\d+/\d+|\d+x\d+|\d+mm|\d+cm|\d+"')
        
    def es_fila_irrelevante(self, fila):
        """Determina si toda la fila es irrelevante"""
        texto_fila = ' '.join(str(cell) for cell in fila).strip()
        
        # Si la fila está mayormente vacía
        celdas_vacias = sum(1 for cell in fila if not str(cell).strip())
        if celdas_vacias > len(fila) * 0.7:
            return True
            
        # Verificar patrones irrelevantes
        for patron in self.patrones_irrelevantes:
            if re.search(patron, texto_fila, re.IGNORECASE):
                return True
        
        return False
    
    def extraer_codigo(self, fila):
        """Extrae código de producto de una fila"""
        for cell in fila:
            cell_str = str(cell).strip()
            if self.patron_codigo.match(cell_str):
                return cell_str
        return None
    
    def extraer_descripcion(self, fila):
        """Extrae descripción de producto de una fila"""
        candidatos = []
        
        for cell in fila:
            cell_str = str(cell).strip()
            
            # Descartar si es muy corto, muy largo, o contiene patrones irrelevantes
            if len(cell_str) < 3 or len(cell_str) > 80:
                continue
                
            # Descartar códigos, precios, y otros campos específicos
            if (self.patron_codigo.match(cell_str) or 
                self.patron_precio.match(cell_str) or
                self.patron_iva.match(cell_str) or
                cell_str in ['.', '-', '+', '$']):
                continue
            
            # Descartar patrones irrelevantes
            es_irrelevante = False
            for patron in self.patrones_irrelevantes:
                if re.search(patron, cell_str, re.IGNORECASE):
                    es_irrelevante = True
                    break
            
            if not es_irrelevante:
                candidatos.append(cell_str)
        
        # Devolver la descripción más larga y específica
        if candidatos:
            return max(candidatos, key=len)
        return None
    
    def extraer_precios(self, fila):
        """Extrae precios de una fila"""
        precios = []
        
        for cell in fila:
            cell_str = str(cell).strip()
            
            # Buscar números que podrían ser precios
            if self.patron_moneda.match(cell_str):
                # Limpiar precio
                precio_limpio = re.sub(r'[^\d,.]', '', cell_str)
                
                # Verificar que no sea un código o valor muy pequeño
                if (precio_limpio and 
                    not self.patron_codigo.match(precio_limpio) and
                    ',' in precio_limpio or '.' in precio_limpio):
                    
                    # Convertir a float para validar
                    try:
                        valor_num = float(precio_limpio.replace(',', '.'))
                        if valor_num > 0.01:  # Precio mínimo razonable
                            precios.append(precio_limpio)
                    except:
                        continue
        
        return precios if precios else None
    
    def extraer_iva(self, fila):
        """Extrae porcentaje de IVA de una fila"""
        for cell in fila:
            cell_str = str(cell).strip()
            if self.patron_iva.match(cell_str):
                try:
                    valor = int(cell_str)
                    if 0 <= valor <= 50:  # Rango razonable para IVA
                        return valor
                except:
                    continue
        return None
    
    def extraer_medida(self, fila):
        """Extrae medidas de una fila"""
        for cell in fila:
            cell_str = str(cell).strip()
            if self.patron_medida.search(cell_str):
                return cell_str
        return None
    
    def procesar_fila(self, fila):
        """Procesa una fila y extrae información del producto"""
        # Verificar si la fila es irrelevante
        if self.es_fila_irrelevante(fila):
            return None
        
        # Extraer campos
        codigo = self.extraer_codigo(fila)
        descripcion = self.extraer_descripcion(fila)
        precios = self.extraer_precios(fila)
        iva = self.extraer_iva(fila)
        medida = self.extraer_medida(fila)
        
        # Crear producto si tiene información mínima relevante
        if codigo or (descripcion and len(descripcion) > 5):
            producto = {}
            
            if codigo:
                producto['codigo'] = codigo
            if descripcion:
                producto['descripcion'] = descripcion
            if precios:
                if len(precios) == 1:
                    producto['precio'] = precios[0]
                else:
                    producto['precios'] = precios
            if iva is not None:
                producto['iva'] = iva
            if medida:
                producto['medida'] = medida
            
            return producto
        
        return None
    
    def purificar_json(self, archivo_entrada, archivo_salida=None):
        """Purifica el archivo JSON eliminando información irrelevante"""
        print(f"🔄 Cargando datos de: {archivo_entrada}")
        
        try:
            with open(archivo_entrada, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            print(f"❌ Error al cargar el archivo: {e}")
            return False
        
        print("🧹 Purificando datos con algoritmo optimizado...")
        
        productos_purificados = []
        total_filas_procesadas = 0
        productos_por_hoja = {}
        
        # Procesar cada hoja
        for hoja in datos.get('hojas', []):
            nombre_hoja = hoja.get('hoja', 'Sin nombre')
            print(f"  📄 Procesando hoja: {nombre_hoja}")
            productos_hoja = 0
            
            for tabla in hoja.get('tablas', []):
                for fila in tabla.get('filas', []):
                    total_filas_procesadas += 1
                    producto = self.procesar_fila(fila)
                    
                    if producto:
                        producto['hoja'] = nombre_hoja
                        producto['proveedor'] = datos.get('proveedor_principal', 'YAYI')
                        productos_purificados.append(producto)
                        productos_hoja += 1
            
            productos_por_hoja[nombre_hoja] = productos_hoja
        
        # Estadísticas
        stats = {
            'productos_con_codigo': sum(1 for p in productos_purificados if 'codigo' in p),
            'productos_con_precio': sum(1 for p in productos_purificados if 'precio' in p or 'precios' in p),
            'productos_con_descripcion': sum(1 for p in productos_purificados if 'descripcion' in p),
            'productos_con_medida': sum(1 for p in productos_purificados if 'medida' in p),
            'productos_con_iva': sum(1 for p in productos_purificados if 'iva' in p),
            'productos_completos': sum(1 for p in productos_purificados 
                                     if 'codigo' in p and 'descripcion' in p and ('precio' in p or 'precios' in p))
        }
        
        # Crear estructura final
        datos_finales = {
            'metadata': {
                'planilla_original': datos.get('planilla', ''),
                'proveedor': datos.get('proveedor_principal', 'YAYI'),
                'fecha_purificacion': datetime.now().isoformat(),
                'version_purificador': 'Final v1.0',
                'total_productos': len(productos_purificados),
                'total_filas_procesadas': total_filas_procesadas,
                'eficiencia_purificacion': f"{(len(productos_purificados)/total_filas_procesadas*100):.1f}%" if total_filas_procesadas > 0 else "0%",
                'productos_por_hoja': productos_por_hoja
            },
            'estadisticas': stats,
            'productos': productos_purificados
        }
        
        # Guardar archivo
        if archivo_salida is None:
            archivo_salida = archivo_entrada.replace('.json', '_purificado_final.json')
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(datos_finales, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Datos purificados guardados en: {archivo_salida}")
            print(f"📊 Estadísticas finales:")
            print(f"   • Filas procesadas: {total_filas_procesadas:,}")
            print(f"   • Productos extraídos: {len(productos_purificados):,}")
            print(f"   • Eficiencia: {datos_finales['metadata']['eficiencia_purificacion']}")
            print(f"   • Con código: {stats['productos_con_codigo']:,}")
            print(f"   • Con descripción: {stats['productos_con_descripcion']:,}")
            print(f"   • Con precio: {stats['productos_con_precio']:,}")
            print(f"   • Productos completos: {stats['productos_completos']:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")
            return False
    
    def mostrar_muestra(self, archivo_purificado, cantidad=10):
        """Muestra una muestra de los productos más completos"""
        try:
            with open(archivo_purificado, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            productos = datos.get('productos', [])
            
            # Filtrar productos más completos
            productos_completos = [p for p in productos 
                                 if 'codigo' in p and 'descripcion' in p and ('precio' in p or 'precios' in p)]
            
            print(f"\n🎯 Muestra de {min(cantidad, len(productos_completos))} productos más completos:")
            print("-" * 80)
            
            for i, producto in enumerate(productos_completos[:cantidad]):
                print(f"Producto {i+1}:")
                for clave, valor in producto.items():
                    if clave == 'precios' and isinstance(valor, list):
                        print(f"  {clave}: {', '.join(valor[:2])}{'...' if len(valor) > 2 else ''}")
                    else:
                        print(f"  {clave}: {valor}")
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error al mostrar muestra: {e}")


def main():
    purificador = PurificadorFinal()
    
    archivo_entrada = "datos_extraidos_app.json"
    archivo_salida = "datos_purificados_final.json"
    
    print("🎯 PURIFICADOR FINAL DE DATOS DE FERRETERÍA")
    print("=" * 70)
    
    if purificador.purificar_json(archivo_entrada, archivo_salida):
        purificador.mostrar_muestra(archivo_salida)
        print(f"\n✨ ¡Proceso completado! Datos purificados en: {archivo_salida}")
    else:
        print("❌ Error en el proceso de purificación")


if __name__ == "__main__":
    main()
