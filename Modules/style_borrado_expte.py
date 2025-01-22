# Modules/style_borrado_expte.py

light_theme = """
/* Estilo general para la aplicación */
QWidget {
    background-color: #F7FBFF; /* Celeste muy claro */
    color: #333333;            /* Texto gris oscuro */
    font-size: 10pt;
    font-family: Arial, sans-serif;
}

/* QMainWindow */
QMainWindow {
    background-color: #ECF5FF; /* Fondo celeste claro */
    border: 1px solid #A9CCE3;
}

/* QLabel (etiquetas) */
QLabel {
    font-weight: bold;
    color: #2C3E50; /* Gris azulado */
}

/* QLineEdit (campos de entrada) */
QLineEdit {
    background-color: #FFFFFF;
    border: 2px solid #A9CCE3;  /* Gris azulado suave */
    padding: 6px;
    border-radius: 6px;
    color: #333333;
    selection-background-color: #B9DAF0;
}

/* Estilo específico para el campo de fojas con texto rojo */
QLineEdit#input_fojas {
    color: #D32F2F;  /* Rojo oscuro */
    font-weight: bold;
}


QLineEdit:hover {
    border: 2px solid #5DADE2; /* Borde azul más intenso al pasar el mouse */
}

QLineEdit:focus {
    border: 2px solid #3498DB; /* Borde azul fuerte al hacer focus */
    background-color: #EAF2F8;
}

/* QTextEdit (área de texto) */
QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #A9CCE3;
    border-radius: 6px;
    padding: 6px;
    color: #2C3E50;
}

QTextEdit:hover {
    border: 1px solid #5DADE2;
}

QTextEdit:focus {
    border: 1px solid #3498DB;
}

/* QPushButton (botones) */
QPushButton {
    background-color: #D4E6F1;   /* Azul claro */
    border: 2px solid #99BBE8;  /* Borde gris azulado */
    padding: 8px 16px;
    border-radius: 8px;
    color: #0B3B5E;             /* Texto más oscuro */
    font-weight: bold;
    transition: all 0.3s ease-in-out;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}

QPushButton:hover {
    background-color: #B9DAF0;  /* Un poco más intenso al pasar el mouse */
    border: 2px solid #2980B9;
    color: #FFFFFF;
    box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
}

QPushButton:pressed {
    background-color: #5DADE2;  /* Azul más fuerte al presionar */
    border: 2px solid #1F618D;
    box-shadow: inset 2px 2px 5px rgba(0,0,0,0.3);
}

/* QPushButton con estado deshabilitado */
QPushButton:disabled {
    background-color: #E5E8E8;
    color: #AAB7B8;
    border: 2px solid #D5DBDB;
}

/* QComboBox (desplegables) */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #A9CCE3;
    border-radius: 6px;
    padding: 4px;
    color: #333333;
}

QComboBox:hover {
    border: 1px solid #5DADE2;
}

QComboBox::drop-down {
    border-left: 1px solid #A9CCE3;
}

/* QScrollBar (barras de desplazamiento) */
QScrollBar:vertical {
    border: none;
    background: #ECF5FF;
    width: 12px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #A9CCE3;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #5DADE2;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* QGroupBox (secciones con borde y título) */
QGroupBox {
    border: 2px solid #A9CCE3;
    border-radius: 6px;
    margin-top: 20px;
    padding: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px;
    font-weight: bold;
    color: #0B3B5E;
}

/* QMessageBox (ventanas emergentes) */
QMessageBox {
    background-color: #FFFFFF;
}

/* QProgressBar (barra de progreso) */
QProgressBar {
    border: 1px solid #A9CCE3;
    border-radius: 6px;
    background-color: #ECF5FF;
    text-align: center;
    color: #2C3E50;
}

QProgressBar::chunk {
    background-color: #5DADE2;
    width: 20px;
}

/* QTabWidget (pestañas) */
QTabWidget::pane {
    border: 1px solid #A9CCE3;
    border-radius: 6px;
}

QTabBar::tab {
    background: #D4E6F1;
    border: 1px solid #A9CCE3;
    padding: 6px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #0B3B5E;
}

QTabBar::tab:selected {
    background: #5DADE2;
    color: #FFFFFF;
}

/* QToolTip (cuadros emergentes de ayuda) */
QToolTip {
    background-color: #5DADE2;
    color: white;
    border: 1px solid #1F618D;
    padding: 4px;
    border-radius: 6px;
    font-size: 9pt;
}
"""
