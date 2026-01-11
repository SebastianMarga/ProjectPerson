"""Punto de entrada: inicializa entorno, base de datos y lanza la interfaz UI"""

# Importar el módulo db inicializador (asegura DB y crea tablas)
try:
    import app.db  # al importarse se asegura la base y se crean tablas
except Exception:
    # intentar importar como script directo
    import db as __db

# Ejecutar la UI
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    try:
        from app.ui import MainWindow
    except Exception:
        from ui import MainWindow

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())