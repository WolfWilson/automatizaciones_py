import sys
import os
import shutil
import logging
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

import PyPDF2

# Librería para enviar correo usando Outlook
# (pywin32)
try:
    import win32com.client as win32
except ImportError:
    win32 = None
    # Si no se encuentra, puedes mostrar un warning o manejarlo.


class PDFManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Gestor de Expedientes - Borrar Fojas de PDF")
        self.setGeometry(200, 200, 900, 650)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Layout para los campos de entrada y botones
        self.layout_inputs = QHBoxLayout()
        
        # 1) Número de Expediente (hasta 6 dígitos)
        self.label_numero = QLabel("Número (6 dígitos):")
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Ej: 17399 -> 017399")
        
        # 2) Año (4 dígitos)
        self.label_anio = QLabel("Año (4 díg):")
        self.input_anio = QLineEdit()
        self.input_anio.setPlaceholderText("Ej: 2023")
        
        # 3) Rango de fojas a borrar (por ejemplo "22-25")
        self.label_fojas = QLabel("Fojas (Ej: 22-25):")
        self.input_fojas = QLineEdit()
        
        # 4) Solicitante (opcional)
        self.label_solicitante = QLabel("Solicitante:")
        self.input_solicitante = QLineEdit()
        self.input_solicitante.setPlaceholderText("Ej: abouvier (opcional)")
        
        # Botón de búsqueda para mostrar cantidad de páginas
        self.btn_buscar = QPushButton("Buscar PDF")
        self.btn_buscar.clicked.connect(self.buscar_pdf)
        
        # Botón para ejecutar el borrado de fojas
        self.btn_realizar = QPushButton("Borrar Fojas")
        self.btn_realizar.clicked.connect(self.borrar_fojas)
        
        # Botón para abrir PDF en el visualizador por defecto
        self.btn_abrir_pdf = QPushButton("Abrir PDF")
        self.btn_abrir_pdf.clicked.connect(self.abrir_pdf)
        
        # Agregar widgets al layout_inputs
        self.layout_inputs.addWidget(self.label_numero)
        self.layout_inputs.addWidget(self.input_numero)
        self.layout_inputs.addWidget(self.label_anio)
        self.layout_inputs.addWidget(self.input_anio)
        self.layout_inputs.addWidget(self.label_fojas)
        self.layout_inputs.addWidget(self.input_fojas)
        self.layout_inputs.addWidget(self.label_solicitante)
        self.layout_inputs.addWidget(self.input_solicitante)
        
        # Agregar los botones (podrías también separarlos en otro layout)
        self.layout_inputs.addWidget(self.btn_buscar)
        self.layout_inputs.addWidget(self.btn_realizar)
        self.layout_inputs.addWidget(self.btn_abrir_pdf)
        
        # Panel de texto para mostrar logs/procesos
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        
        # Layout para mostrar la información de la portada
        self.info_layout = QHBoxLayout()
        self.label_info_nro = QLabel("Nro: -")       # Se actualizará según portada
        self.label_info_iniciado = QLabel("Iniciado: -")
        self.label_info_extracto = QLabel("Extracto: -")
        
        self.info_layout.addWidget(self.label_info_nro)
        self.info_layout.addWidget(self.label_info_iniciado)
        self.info_layout.addWidget(self.label_info_extracto)
        
        # Agregamos todo al layout principal
        self.main_layout.addLayout(self.layout_inputs)
        self.main_layout.addLayout(self.info_layout)
        self.main_layout.addWidget(self.text_log)
        
        # Configurar el logger
        self.config_logger()
        
        self.print_log("Aplicación iniciada correctamente.")
    
    def config_logger(self):
        """
        Configura el logger para registrar en archivo y consola
        """
        log_filename = "borrado_fojas.log"
        
        logging.basicConfig(
            filename=log_filename,
            filemode="a",  # append
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO
        )
    
    def print_log(self, message, level="info"):
        """
        Muestra mensajes en el QTextEdit y también en el logger.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{current_time}] {message}"
        
        self.text_log.append(full_message)
        
        if level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        else:
            logging.debug(message)
        
        print(full_message)
    
    def build_pdf_path(self):
        """
        Construye la ruta del PDF en base a los valores de numero, año y letra (por ahora 'E').
        Retorna la ruta completa y el subcarpeta (base) para usarlo en backup, etc.
        """
        numero_str = self.input_numero.text().strip()
        anio_str = self.input_anio.text().strip()
        
        if not numero_str or not anio_str:
            raise ValueError("Falta número o año para construir la ruta.")
        
        # Asegurar que el número tenga 6 dígitos
        try:
            num_int = int(numero_str)  # Verifica que sea numérico
            numero_str = f"{num_int:06d}"
        except ValueError:
            raise ValueError("El número de expediente debe ser un entero válido.")
        
        if len(anio_str) != 4 or not anio_str.isdigit():
            raise ValueError("El año debe ser un número de 4 dígitos.")
        
        letra = "E"
        
        # Ruta en la red
        root_path = r"\\fs01\Digitalizacion_Jubilaciones"
        anio_folder = anio_str
        letra_folder = letra
        subcarpeta = f"{letra}-{numero_str}-{anio_str}"
        
        pdf_name = f"{subcarpeta}.pdf"
        pdf_path = os.path.join(root_path, anio_folder, letra_folder, subcarpeta, pdf_name)
        
        return pdf_path, subcarpeta
    
    def buscar_pdf(self):
        """
        Botón para verificar si el PDF existe y mostrar la cantidad de páginas (si es posible).
        """
        try:
            pdf_path, _ = self.build_pdf_path()
        except ValueError as e:
            QMessageBox.warning(self, "Error de datos", str(e))
            return
        
        if not os.path.isfile(pdf_path):
            self.print_log(f"No se encontró el archivo en la ruta: {pdf_path}", level="error")
            QMessageBox.warning(self, "Archivo no encontrado", f"No existe: {pdf_path}")
            return
        
        # Intentar abrir y contar páginas
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                
                self.print_log(f"El archivo '{pdf_path}' existe. Páginas: {total_pages}")
                QMessageBox.information(
                    self,
                    "Búsqueda exitosa",
                    f"Se encontró el PDF.\nCantidad de páginas: {total_pages}"
                )
            
            # Intentar leer la primera página (portada)
            self.leer_datos_portada(pdf_path)
            
        except PermissionError:
            error_msg = (
                "Permiso denegado al intentar leer el PDF.\n"
                "Verifica que el archivo no esté abierto y que tengas permisos de lectura."
            )
            self.print_log(error_msg, level="error")
            QMessageBox.critical(self, "Error de Permisos", error_msg)
        except Exception as e:
            self.print_log(f"Error al intentar abrir/leer el PDF: {str(e)}", level="error")
            QMessageBox.critical(self, "Error al abrir PDF", str(e))
    
    def leer_datos_portada(self, pdf_path):
        """
        Lee la primera página de 'pdf_path' y busca los datos:
          Nro, Iniciado y Extracto
        Ajusta el contenido de los label_info_* en la interfaz.
        """
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) == 0:
                    self.print_log("El PDF no contiene páginas.", level="warning")
                    return
                
                first_page = reader.pages[0]
                text = first_page.extract_text() or ""
                
                lines = text.split("\n")
                
                nro_val = "-"
                iniciado_val = "-"
                extracto_val = "-"
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("Nro:"):
                        nro_val = line.replace("Nro:", "").strip()
                    elif line.startswith("Iniciado:"):
                        iniciado_val = line.replace("Iniciado:", "").strip()
                    elif line.startswith("Extracto:"):
                        extracto_val = line.replace("Extracto:", "").strip()
                
                # Actualizamos los labels
                self.label_info_nro.setText(f"Nro: {nro_val}")
                self.label_info_iniciado.setText(f"Iniciado: {iniciado_val}")
                self.label_info_extracto.setText(f"Extracto: {extracto_val}")
                
                self.print_log(f"Datos portada => Nro: {nro_val}, Iniciado: {iniciado_val}, Extracto: {extracto_val}")
                
        except PermissionError as e:
            self.print_log(f"Permiso denegado al leer portada: {str(e)}", level="error")
        except Exception as e:
            self.print_log(f"Error leyendo portada: {str(e)}", level="error")
    
    def abrir_pdf(self):
        """
        Abre el PDF en el visualizador predeterminado de Windows (usando os.startfile).
        """
        try:
            pdf_path, _ = self.build_pdf_path()
        except ValueError as e:
            QMessageBox.warning(self, "Error de datos", str(e))
            return
        
        if not os.path.isfile(pdf_path):
            self.print_log(f"No se encontró el archivo para abrir: {pdf_path}", level="error")
            QMessageBox.warning(self, "Archivo no encontrado", f"No existe: {pdf_path}")
            return
        
        try:
            # Sólo funciona en Windows
            os.startfile(pdf_path)
            self.print_log(f"Abriendo PDF: {pdf_path}")
        except Exception as e:
            self.print_log(f"No se pudo abrir el PDF: {str(e)}", level="error")
            QMessageBox.critical(self, "Error al abrir PDF", str(e))
    
    def borrar_fojas(self):
        """
        Botón para realizar la copia de seguridad y eliminar las páginas solicitadas.
        """
        fojas_str = self.input_fojas.text().strip()
        if not fojas_str:
            QMessageBox.warning(self, "Error de datos", "Por favor ingresa las fojas a eliminar (rango 'x-y').")
            return
        
        try:
            pdf_path, subcarpeta = self.build_pdf_path()
        except ValueError as e:
            QMessageBox.warning(self, "Error de datos", str(e))
            return
        
        if not os.path.isfile(pdf_path):
            self.print_log(f"No se encontró el archivo en la ruta: {pdf_path}", level="error")
            QMessageBox.warning(self, "Archivo no encontrado", f"No existe: {pdf_path}")
            return
        
        backup_dir = r"C:\Bk_de_Expedientes"
        
        if not os.path.exists(backup_dir):
            try:
                os.makedirs(backup_dir)
            except Exception as e:
                self.print_log(f"No se pudo crear la carpeta de backup: {backup_dir}", level="error")
                QMessageBox.critical(self, "Error de Backup", f"No se pudo crear {backup_dir}\n{e}")
                return
        
        backup_filename = f"{subcarpeta}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Crear el backup
        try:
            shutil.copy2(pdf_path, backup_path)
            self.print_log(f"Backup creado: {backup_path}")
        except PermissionError as e:
            self.print_log(f"Permiso denegado al crear backup: {str(e)}", level="error")
            QMessageBox.critical(
                self,
                "Error de Permisos",
                "No se pudo crear la copia de seguridad.\n"
                "Revisa si tienes permisos de escritura."
            )
            return
        except Exception as e:
            self.print_log(f"Error creando backup: {str(e)}", level="error")
            QMessageBox.critical(self, "Error de Backup", f"No se pudo crear la copia de seguridad.\n{e}")
            return
        
        # Parsear fojas (x-y)
        try:
            inicio, fin = fojas_str.split("-")
            inicio = int(inicio)
            fin = int(fin)
            if inicio <= 0 or fin <= 0:
                raise ValueError("Los números de página deben ser positivos.")
            if inicio > fin:
                raise ValueError("El rango de fojas es inválido (inicio > fin).")
        except ValueError:
            self.print_log("Formato de fojas incorrecto. Usa 'inicio-fin', ej: 30-34.", level="error")
            QMessageBox.warning(
                self, "Error de Formato", 
                "Fojas debe ser un rango válido, ej: 30-34."
            )
            return
        
        # Eliminar páginas
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                
                total_pages = len(reader.pages)
                
                for idx in range(total_pages):
                    page_number = idx + 1
                    if inicio <= page_number <= fin:
                        continue
                    writer.add_page(reader.pages[idx])
                
                with open(pdf_path, 'wb') as out_f:
                    writer.write(out_f)
                    
            self.print_log(f"Fojas {inicio}-{fin} eliminadas correctamente en: {pdf_path}")
            QMessageBox.information(
                self, 
                "Proceso completado", 
                f"Fojas {inicio}-{fin} eliminadas con éxito.\nRevisa el log para más detalles."
            )
            
            # Enviar correo de confirmación si hay solicitante
            solicitante = self.input_solicitante.text().strip()
            if solicitante:
                # Armar correo (solicitante@insssep.gov.ar)
                correo_destino = f"{solicitante}@insssep.gov.ar"
                self.enviar_correo_confirmacion(correo_destino, pdf_path, inicio, fin)
            
            # Mostrar el contenido del log al finalizar
            self.mostrar_contenido_log()
        
        except PermissionError:
            error_msg = (
                f"Permiso denegado al intentar escribir en el PDF:\n{pdf_path}\n\n"
                f"Verifica que el archivo no esté abierto y que tengas permisos de escritura."
            )
            self.print_log(error_msg, level="error")
            QMessageBox.critical(self, "Error de Permisos", error_msg)
        except Exception as e:
            self.print_log(f"Error al procesar el PDF: {str(e)}", level="error")
            QMessageBox.critical(self, "Error al procesar PDF", str(e))
    
    def enviar_correo_confirmacion(self, destinatario, pdf_path, inicio, fin):
        """
        Envía un correo de confirmación (vía Outlook) indicando que se borraron las fojas.
        """
        if not win32:
            # Si no está instalado pywin32, no se puede enviar correo
            self.print_log("pywin32 no está disponible. No se envía correo.", level="warning")
            return
        
        try:
            outlook = win32.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = olMailItem
            mail.To = destinatario
            mail.Subject = "Confirmación de Borrado de Fojas"
            
            expediente = os.path.basename(os.path.dirname(pdf_path))  # Extrae el nombre de la carpeta, que corresponde al número del expediente

            cuerpo = (
                f"Estimado/a,\n\n"
                f"Se han borrado las fojas {inicio}-{fin} del expediente:\n"
                f"{expediente}\n\n"
                f"Estado: REALIZADO.\n\n"
                f"Saludos,\n"
                f"Equipo de Automatización"
            )

            
            mail.Body = cuerpo
            # Si deseas enviar en HTML:
            # mail.HTMLBody = "<p>...</p>"
            
            mail.Send()
            
            self.print_log(f"Correo de confirmación enviado a: {destinatario}")
        
        except Exception as e:
            self.print_log(f"No se pudo enviar el correo a {destinatario}: {str(e)}", level="error")
    
    def mostrar_contenido_log(self):
        """
        Carga y muestra el contenido del archivo de log al final del proceso.
        """
        log_filename = "borrado_fojas.log"
        if os.path.isfile(log_filename):
            try:
                with open(log_filename, "r", encoding="utf-8") as log_file:
                    contenido = log_file.read()
                self.print_log("\n=== CONTENIDO DEL LOG ===")
                self.text_log.append(contenido)
                self.print_log("=== FIN DEL LOG ===\n")
            except Exception as e:
                self.print_log(f"Error al leer el log: {e}", level="error")
        else:
            self.print_log("No se encontró el archivo de log para mostrar.", level="warning")


def main():
    app = QApplication(sys.argv)
    ventana = PDFManager()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
