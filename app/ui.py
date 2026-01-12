from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QSpinBox, QDateEdit, QMessageBox, QApplication,
    QAbstractItemView, QDialogButtonBox, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, QDate
from datetime import date
import traceback

# Uso opcional de pandas para exportar a .xlsx; si no está, crearemos a CSV
try:
    import pandas as pd
    HAS_PANDAS = True
    # pandas necesita openpyxl para escribir .xlsx
    try:
        import openpyxl  # noqa: F401
        HAS_OPENPYXL = True
    except Exception:
        HAS_OPENPYXL = False
except Exception:
    pd = None
    HAS_PANDAS = False
    HAS_OPENPYXL = False
# Soporte para exportar a PDF con reportlab
try:
    from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False
try:
    from app.repository import list_products, insert_product_safe, update_product_safe, delete_product
    from app.exporter import export_csv, export_xlsx, export_pdf, export_to, MissingDependencyError, ExportError
except ModuleNotFoundError:
    try:
        from repository import list_products, insert_product_safe, update_product_safe, delete_product
        from exporter import export_csv, export_xlsx, export_pdf, export_to, MissingDependencyError, ExportError
    except Exception:
        traceback.print_exc()
        raise


class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Producto")
        # Hacer dialog modal para que se muestre y capture la interacción
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.product = product
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.tipo_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        self.cant_spin = QSpinBox()
        self.cant_spin.setRange(0, 1000000)
        self.marca_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        layout.addRow("Nombre:", self.name_edit)
        layout.addRow("Tipo:", self.tipo_edit)
        layout.addRow("Descripción:", self.desc_edit)
        layout.addRow("Cantidad:", self.cant_spin)
        layout.addRow("Marca:", self.marca_edit)
        layout.addRow("Fecha Vencimiento:", self.date_edit)

        # Botones OK / Cancelar
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        # Cargar datos si se proporciona un producto
        if product:
            self.name_edit.setText(product.name or "")
            self.tipo_edit.setText(product.tipo or "")
            self.desc_edit.setText(product.descripcion or "")
            self.cant_spin.setValue(product.cantidad or 0)
            self.marca_edit.setText(product.Marca or "")
            if product.Fecha_Vencimiento:
                self.date_edit.setDate(QDate(product.Fecha_Vencimiento.year, product.Fecha_Vencimiento.month, product.Fecha_Vencimiento.day))
            else:
                self.date_edit.setDate(QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())

    def get_data(self):
        qd = self.date_edit.date()
        return {
            "name": self.name_edit.text().strip(),
            "tipo": self.tipo_edit.text().strip(),
            "descripcion": self.desc_edit.text().strip(),
            "cantidad": self.cant_spin.value(),
            "Marca": self.marca_edit.text().strip(),
            "Fecha_Vencimiento": date(qd.year(), qd.month(), qd.day())
        }

#Se crea la ventana principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario - Mini")
        self.resize(800, 400)

        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        # Tabla
        # ahora con columna 'Tipo'
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "Descripción", "Cantidad", "Marca", "Fecha Vencimiento", "Fecha Registro"]) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        vbox.addWidget(self.table)

        # Botones
        hbox = QHBoxLayout()
        self.add_btn = QPushButton("Agregar")
        self.edit_btn = QPushButton("Editar")
        self.del_btn = QPushButton("Eliminar")
        self.refresh_btn = QPushButton("Refrescar")
        self.export_btn = QPushButton("Exportar")
        hbox.addWidget(self.add_btn)
        hbox.addWidget(self.edit_btn)
        hbox.addWidget(self.del_btn)
        hbox.addWidget(self.refresh_btn)
        hbox.addWidget(self.export_btn)
        hbox.addStretch()
        vbox.addLayout(hbox)

        # Conectar señales
        self.add_btn.clicked.connect(self.on_add)
        self.edit_btn.clicked.connect(self.on_edit)
        self.del_btn.clicked.connect(self.on_delete)
        self.refresh_btn.clicked.connect(self.load_products)
        self.export_btn.clicked.connect(self.on_export)

        self.load_products()
# Cargar productos en la tabla
    def load_products(self):
        try:
            products = list_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo obtener productos:\n{e}")
            return

        self.table.setRowCount(0)
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(p.tipo or ""))
            self.table.setItem(row, 3, QTableWidgetItem(p.descripcion or ""))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.cantidad)))
            self.table.setItem(row, 5, QTableWidgetItem(p.Marca or ""))
            self.table.setItem(row, 6, QTableWidgetItem(p.Fecha_Vencimiento.isoformat() if p.Fecha_Vencimiento else ""))
            self.table.setItem(row, 7, QTableWidgetItem(p.Fecha_Registro.isoformat() if p.Fecha_Registro else ""))

        self.table.resizeColumnsToContents()
# Obtener ID del producto seleccionado
    def get_selected_product_id(self):
        sel = self.table.currentRow()
        if sel < 0:
            return None
        item = self.table.item(sel, 0)
        return int(item.text()) if item else None

    def on_add(self):
        dlg = ProductDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                insert_product_safe(**data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo insertar producto:\n{e}")
            self.load_products()

    def on_edit(self):
        pid = self.get_selected_product_id()
        if not pid:
            QMessageBox.information(self, "Selecciona", "Selecciona un producto para editar.")
            return
        # Cargar producto
        products = list_products()
        prod = next((x for x in products if x.id == pid), None)
        if not prod:
            QMessageBox.critical(self, "Error", "Producto no encontrado.")
            return
        dlg = ProductDialog(self, product=prod)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                update_product_safe(pid, **data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar producto:\n{e}")
            self.load_products()

    def on_export(self):
        try:
            products = list_products()
            data = []
            for p in products:
                data.append({
                    'id': p.id,
                    'name': p.name or '',
                    'tipo': p.tipo or '',
                    'descripcion': p.descripcion or '',
                    'cantidad': p.cantidad,
                    'Marca': p.Marca or '',
                    'Fecha_Vencimiento': p.Fecha_Vencimiento.isoformat() if p.Fecha_Vencimiento else '',
                    'Fecha_Registro': p.Fecha_Registro.isoformat() if p.Fecha_Registro else ''
                })
            fieldnames = ['id','name','tipo','descripcion','cantidad','Marca','Fecha_Vencimiento','Fecha_Registro']

            # Pedir formato
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Formato de exportación")
            dlg.setText("Selecciona el formato de exportación:")
            btn_csv = dlg.addButton("CSV", QMessageBox.AcceptRole)
            btn_pdf = dlg.addButton("PDF", QMessageBox.AcceptRole)
            btn_xlsx = dlg.addButton("Excel (.xlsx)", QMessageBox.AcceptRole)
            dlg.addButton(QMessageBox.Cancel)
            dlg.exec()
            clicked = dlg.clickedButton()
            if clicked == btn_csv:
                fmt = 'csv'
            elif clicked == btn_pdf:
                fmt = 'pdf'
            elif clicked == btn_xlsx:
                fmt = 'xlsx'
            else:
                return

            # Pedir ruta según formato
            if fmt == 'pdf':
                path, _ = QFileDialog.getSaveFileName(self, "Guardar inventario", "inventario.pdf", "PDF Files (*.pdf)")
            elif fmt == 'xlsx':
                path, _ = QFileDialog.getSaveFileName(self, "Guardar inventario", "inventario.xlsx", "Excel Files (*.xlsx)")
            else:
                path, _ = QFileDialog.getSaveFileName(self, "Guardar inventario", "inventario.csv", "CSV Files (*.csv)")
            if not path:
                return

            # Si exportamos a PDF, preguntar por un logo opcional y pedir tamaño
            logo_path = None
            logo_width = None
            if fmt == 'pdf':
                # preseleccionar logo en resources si existe
                logo_path = "resources/logo.png"
                if logo_path == '' or logo_path is None:
                    logo_path = None
                else:
                    size, ok = QInputDialog.getItem(self, "Tamaño del logo", "Selecciona tamaño:", ["Pequeño", "Mediano", "Grande"], 1, False)
                    if ok:
                        if size == "Pequeño":
                            logo_width = 50
                        elif size == "Mediano":
                            logo_width = 80
                        else:
                            logo_width = 120
                    else:
                        logo_width = 80

            # Intentar exportar con el módulo exportador
            try:
                if fmt == 'pdf':
                    export_to(fmt, path, data, fieldnames, logo_path=logo_path, logo_width=logo_width)
                else:
                    export_to(fmt, path, data, fieldnames)
                QMessageBox.information(self, "Exportado", f"Datos exportados a: {path}")
            except MissingDependencyError as e:
                resp = QMessageBox.question(self, "Dependencia faltante", f"{e}\n¿Guardar en CSV en su lugar?", QMessageBox.Yes | QMessageBox.No)
                if resp == QMessageBox.Yes:
                    csv_path = path.rsplit('.',1)[0] + '.csv'
                    try:
                        export_csv(csv_path, data, fieldnames)
                        QMessageBox.information(self, "Exportado", f"Datos exportados a: {csv_path}")
                    except Exception as ex:
                        QMessageBox.critical(self, "Error", f"No se pudo exportar a CSV:\n{ex}")
                else:
                    QMessageBox.information(self, "Cancelado", "Exportación cancelada.")
            except ExportError as e:
                QMessageBox.critical(self, "Error", f"Error en la exportación:\n{e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{e}")

    def on_delete(self):
        pid = self.get_selected_product_id()
        if not pid:
            QMessageBox.information(self, "Selecciona", "Selecciona un producto para eliminar.")
            return
        ok = QMessageBox.question(self, "Confirmar", "¿Eliminar producto seleccionado?", QMessageBox.Yes | QMessageBox.No)
        if ok != QMessageBox.Yes:
            return
        try:
            deleted = delete_product(pid)
            if not deleted:
                QMessageBox.information(self, "Info", "Producto no encontrado o ya eliminado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar producto:\n{e}")
        self.load_products()
