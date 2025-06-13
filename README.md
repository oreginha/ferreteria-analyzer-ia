# 🔧 Ferretería Analyzer con IA

Sistema completo de análisis de datos de ferretería con inteligencia artificial integrada. Pipeline automatizado para extracción, purificación, análisis y exportación de datos desde archivos HTML a Excel estructurado.

## 🎯 Características Principales

### 🚀 Pipeline Completo Automatizado
1. **📁 Extracción de Datos** - Procesamiento inteligente de archivos HTML
2. **🧹 Purificación con IA** - Limpieza y estructuración automática
3. **🤖 Análisis Inteligente** - Análisis de precios, tendencias y recomendaciones
4. **📊 Exportación Estructurada** - Generación de Excel con múltiples hojas

### ✨ Funcionalidades Avanzadas
- **Detección automática de proveedores** (YAYI, CRIMARAL, ANCAIG, etc.)
- **Clasificación inteligente de campos** (códigos, precios, IVA, descripciones)
- **Filtros sofisticados** para eliminar texto irrelevante
- **Múltiples precios por producto** correctamente extraídos
- **Metadatos completos** con estadísticas detalladas
- **Interfaz gráfica intuitiva** desarrollada en Tkinter

## 📊 Resultados de Calidad

### ✅ Extracción Superior
- **3,517 productos** de alta calidad (vs 21,435 con datos basura)
- **85.1%** de productos con código válido
- **99.7%** de productos con precio
- **85.0%** de productos con IVA extraído
- **100%** de eficiencia en purificación

### 🎖️ Calidad vs Cantidad
El sistema prioriza **calidad sobre cantidad**, extrayendo productos con estructura perfecta:

```json
{
  "descripcion": "ARANDELA AJUSTE PLASTICA CROMO TAPA LA PALANQUITA CON TORNILLO",
  "codigo": "9800003",
  "iva": 0,
  "precios": ["900,96", "684,73", "958,62", "480292"],
  "hoja": "YAYI_LISTA_01",
  "proveedor": "YAYI"
}
```

## 🚀 Instalación y Uso

### Requisitos
```bash
Python 3.7+
tkinter (incluido en Python)
beautifulsoup4
pandas
openpyxl
```

### Instalación Rápida
```bash
# Clonar repositorio
git clone https://github.com/oreginha/ferreteria-analyzer-ia.git
cd ferreteria-analyzer-ia

# Instalar dependencias
pip install beautifulsoup4 pandas openpyxl

# Ejecutar aplicación
python ferreteria_app_modular.py
```

### Uso con Script Batch (Windows)
```batch
ejecutar_app_completa.bat
```

## 📁 Estructura del Proyecto

### 🔧 Archivos Principales
- **`ferreteria_app_modular.py`** - Aplicación principal (controlador)
- **`ferreteria_ui.py`** - Interfaz de usuario (Tkinter)
- **`extraer_datos.py`** - Extracción de datos con algoritmo v2
- **`purificador_datos.py`** - Purificación inteligente
- **`data_analyzer.py`** - Análisis con IA

### 📄 Scripts de Soporte
- **`ejecutar_app_completa.bat`** - Ejecutor para Windows
- **`verificar_proyecto.py`** - Verificación del sistema
- **`test_extraccion.py`** - Pruebas de extracción

### 📚 Documentación
- **`PROYECTO_MODULARIZADO_COMPLETO.md`** - Documentación completa
- **`EXTRACCION_RESTAURADA_V2.md`** - Detalles del algoritmo v2

## 🛠️ Flujo de Trabajo

### 1. Seleccionar Directorio
Elige la carpeta con archivos HTML (Excel convertido)

### 2. Extraer Datos
- Procesamiento automático de archivos HTML
- Detección de proveedores
- Clasificación inteligente de campos

### 3. Purificar Datos ⭐
- Eliminación de texto irrelevante
- Filtrado de duplicados
- Estructuración automática
- Validación de códigos y precios

### 4. Analizar con IA
- Análisis de precios y tendencias
- Identificación de productos destacados
- Generación de recomendaciones

### 5. Exportar Excel
- Archivo Excel con múltiples hojas
- Resumen ejecutivo automático
- Datos organizados por categorías

## 🎯 Casos de Uso

### 🏪 Ferreterías y Distribuidoras
- Análisis de inventarios
- Comparación de precios entre proveedores
- Optimización de catálogos
- Gestión de listas de productos

### 📊 Análisis de Datos
- Procesamiento de listas de precios
- Estructuración de datos no estructurados
- Limpieza automática de datasets
- Generación de reportes ejecutivos

## 🔧 Arquitectura Técnica

### 🏗️ Diseño Modular
```
ferreteria_app_modular.py (Controlador)
    ├── ferreteria_ui.py (Interfaz)
    ├── extraer_datos.py (Extracción)
    ├── purificador_datos.py (Purificación)
    └── data_analyzer.py (Análisis)
```

### 🧠 Algoritmo de Extracción v2
1. **Clasificación de campos** por patrones regex
2. **Filtros sofisticados** para texto irrelevante
3. **Detección de proveedores** automática
4. **Normalización de precios** inteligente
5. **Validación robusta** de productos

### 📈 Estadísticas y Metadatos
```json
{
  "metadata": {
    "planilla_original": "YAYI FULL - 3 FEBRERO",
    "proveedor": "YAYI",
    "total_productos": 3517,
    "eficiencia_purificacion": "100.0%"
  },
  "estadisticas": {
    "productos_con_codigo": 2994,
    "productos_con_precio": 3506,
    "productos_con_iva": 2991
  }
}
```

## 🎖️ Ventajas Competitivas

### ⚡ Performance Superior
- **Algoritmo v2** optimizado para calidad
- **Procesamiento inteligente** vs extracción bruta
- **Filtrado avanzado** elimina 85% de ruido
- **Estructuración automática** de datos

### 🎯 Precisión
- **Detección automática** de 15+ proveedores
- **Clasificación inteligente** de campos
- **Validación robusta** de productos
- **Metadatos completos** automáticos

### 🔧 Usabilidad
- **Interfaz intuitiva** paso a paso
- **Procesamiento en hilos** (UI responsiva)
- **Mensajes informativos** en tiempo real
- **Scripts de ejecución** listos

## 📋 Roadmap

### ✅ Completado
- [x] Pipeline completo funcional
- [x] Algoritmo v2 de extracción
- [x] Interfaz gráfica completa
- [x] Purificación inteligente
- [x] Análisis con IA
- [x] Exportación estructurada
- [x] Documentación completa

### 🔮 Futuro
- [ ] API REST para integración
- [ ] Soporte para más formatos (CSV, XML)
- [ ] Dashboard web interactivo
- [ ] Machine Learning para categorización
- [ ] Integración con bases de datos

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Desarrollado por IA Assistant**
- Proyecto: Ferretería Analyzer con IA
- Versión: 3.0 - Algoritmo v2 Restaurado
- Fecha: Junio 2025

## 🙏 Agradecimientos

- **BeautifulSoup4** - Parsing HTML
- **Pandas** - Manipulación de datos
- **Tkinter** - Interfaz gráfica
- **OpenPyXL** - Exportación Excel

---

### 🎯 ¡Listo para Producción!

**Sistema completo de análisis de ferretería con IA - Calidad empresarial** 🚀

[![GitHub issues](https://img.shields.io/github/issues/oreginha/ferreteria-analyzer-ia)](https://github.com/oreginha/ferreteria-analyzer-ia/issues)
[![GitHub stars](https://img.shields.io/github/stars/oreginha/ferreteria-analyzer-ia)](https://github.com/oreginha/ferreteria-analyzer-ia/stargazers)
[![GitHub license](https://img.shields.io/github/license/oreginha/ferreteria-analyzer-ia)](https://github.com/oreginha/ferreteria-analyzer-ia/blob/main/LICENSE)