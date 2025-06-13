#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores de sintaxis en ferreteria_analyzer_app.py
"""

def fix_syntax_errors():
    input_file = "ferreteria_analyzer_app.py"
    output_file = "ferreteria_analyzer_app_fixed.py"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corregir líneas fusionadas comunes
    fixes = [
        # Líneas fusionadas con declaraciones
        ('        """Selecciona el directorio de trabajo"""        directory = filedialog.askdirectory',
         '        """Selecciona el directorio de trabajo"""\n        directory = filedialog.askdirectory'),
        
        ('        self.status_var = tk.StringVar()        self.status_var.set("Listo")',
         '        self.status_var = tk.StringVar()\n        self.status_var.set("Listo")'),
        
        ('                self.log_message("🔍 Iniciando extracción de datos...")                self.log_message(f"📂 Directorio de trabajo: {selected_dir}")',
         '                self.log_message("🔍 Iniciando extracción de datos...")\n                self.log_message(f"📂 Directorio de trabajo: {selected_dir}")'),
        
        ('                    self.log_message(f"❌ Error: El directorio no existe: {selected_dir}")                    self.update_status("Error: Directorio no existe")',
         '                    self.log_message(f"❌ Error: El directorio no existe: {selected_dir}")\n                    self.update_status("Error: Directorio no existe")'),
        
        # Corregir indentaciones incorrectas de métodos
        ('              def log_message(self, message):', '    def log_message(self, message):'),
        ('          def update_status(self, message):', '    def update_status(self, message):'),
        ('          def extract_data(self):', '    def extract_data(self):'),
        ('          def configure_gemini(self):', '    def configure_gemini(self):'),
        ('              def select_directory(self):', '    def select_directory(self):'),
        
        # Corregir espacios en comentarios fusionados
        ('                # Verificar que el directorio existe                if not os.path.exists',
         '                # Verificar que el directorio existe\n                if not os.path.exists'),
        
        ('                  # Ejecutar extracción de datos',
         '                # Ejecutar extracción de datos'),
        
        ('                  if data:',
         '                if data:'),
    ]
    
    # Aplicar correcciones
    for old, new in fixes:
        content = content.replace(old, new)
    
    # Escribir archivo corregido
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Archivo corregido guardado como: {output_file}")

if __name__ == "__main__":
    fix_syntax_errors()
