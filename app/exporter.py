"""Export utilities: CSV, XLSX and PDF exporters used by the UI.

Functions:
- export_csv(path, data, fieldnames)
- export_xlsx(path, data, fieldnames)
- export_pdf(path, data, fieldnames)
- MissingDependencyError

Each function raises MissingDependencyError when a required library is not installed, and raises a RuntimeError for other failures.
"""
from typing import List, Dict
import csv

class MissingDependencyError(RuntimeError):
    pass

class ExportError(RuntimeError):
    pass


def export_csv(path: str, data: List[Dict], fieldnames: List[str]):
    """Export data (list of dicts) to CSV at `path`."""
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except Exception as e:
        raise ExportError(str(e)) from e


def export_xlsx(path: str, data: List[Dict], fieldnames: List[str]):
    """Export data to an Excel .xlsx file using pandas + openpyxl.

    Raises MissingDependencyError if pandas or openpyxl are not available.
    """
    try:
        import pandas as pd
    except Exception as e:
        raise MissingDependencyError("pandas is required to export to .xlsx (pip install pandas)") from e
    try:
        import openpyxl  # noqa: F401
    except Exception as e:
        raise MissingDependencyError("openpyxl is required to export to .xlsx (pip install openpyxl)") from e

    try:
        df = pd.DataFrame(data, columns=fieldnames)
        df.to_excel(path, index=False, engine='openpyxl')
    except Exception as e:
        raise ExportError(str(e)) from e


def export_pdf(path: str, data: List[Dict], fieldnames: List[str], logo_path: str = None, logo_width: float = 80, logo_height: float = None, margin_top: float = 20):
    """Export data to PDF using reportlab.

    Optional parameters:
      - logo_path: path to an image file to place at the top-left of each page.
      - logo_width / logo_height: dimensions in points (defaults scale preserving aspect ratio)
      - margin_top: distance from the top edge in points.

    Raises MissingDependencyError if reportlab is not available.
    """
    try:
        from reportlab.platypus import SimpleDocTemplate, Table as RLTable, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception as e:
        raise MissingDependencyError("reportlab is required to export to PDF (pip install reportlab)") from e

    def _draw_logo(c, doc):
        if not logo_path:
            return
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_path)
            iw, ih = img.getSize()
            lw = logo_width if logo_width is not None else 100
            if logo_height is None:
                lh = lw * ih / iw if iw != 0 else lw
            else:
                lh = logo_height
            x = doc.leftMargin
            page_h = doc.pagesize[1]
            y = page_h - margin_top - lh
            c.drawImage(img, x, y, width=lw, height=lh, mask='auto')
        except Exception as e:
            # Raise an ExportError so UI can handle it gracefully
            raise ExportError(f"Error dibujando el logo: {e}") from e

    try:
        doc = SimpleDocTemplate(path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Inventario", styles['Title']))
        elements.append(Spacer(1, 12))

        table_data = [fieldnames]
        for r in data:
            table_data.append([r.get(col, '') for col in fieldnames])

        t = RLTable(table_data, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))

        elements.append(t)
        # pass the drawing callback to ensure logo appears on every page
        doc.build(elements, onFirstPage=_draw_logo, onLaterPages=_draw_logo)
    except MissingDependencyError:
        raise
    except ExportError:
        raise
    except Exception as e:
        raise ExportError(str(e)) from e


def export_to(fmt: str, path: str, data: List[Dict], fieldnames: List[str], **kwargs):
    fmt = fmt.lower()
    if fmt == 'csv':
        return export_csv(path, data, fieldnames)
    if fmt == 'xlsx' or fmt == 'excel':
        return export_xlsx(path, data, fieldnames)
    if fmt == 'pdf':
        return export_pdf(path, data, fieldnames, **kwargs)
    raise ValueError(f"Formato desconocido: {fmt}")