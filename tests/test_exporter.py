import os
from pathlib import Path
import pytest
from app.exporter import export_csv, export_xlsx, export_pdf, MissingDependencyError

SAMPLE_DATA = [
    {'id': 1, 'name': 'Producto A', 'tipo': 'Tipo1', 'descripcion': 'Desc', 'cantidad': 10, 'Marca': 'M', 'Fecha_Vencimiento': '2026-01-01', 'Fecha_Registro': '2026-01-01'},
    {'id': 2, 'name': 'Producto B', 'tipo': 'Tipo2', 'descripcion': 'Desc2', 'cantidad': 5, 'Marca': 'M2', 'Fecha_Vencimiento': '2026-02-01', 'Fecha_Registro': '2026-02-02'},
]
FIELDNAMES = ['id','name','tipo','descripcion','cantidad','Marca','Fecha_Vencimiento','Fecha_Registro']


def test_export_csv(tmp_path):
    p = tmp_path / "out.csv"
    export_csv(str(p), SAMPLE_DATA, FIELDNAMES)
    assert p.exists() and p.stat().st_size > 0
    text = p.read_text(encoding='utf-8')
    assert 'Producto A' in text


@pytest.mark.skipif(not pytest.importorskip('pandas', reason='pandas missing'), reason='pandas not available')
def test_export_xlsx(tmp_path):
    p = tmp_path / "out.xlsx"
    # If pandas/openpyxl missing, export_xlsx should raise MissingDependencyError
    try:
        export_xlsx(str(p), SAMPLE_DATA, FIELDNAMES)
    except MissingDependencyError:
        pytest.skip('openpyxl or pandas missing')
    assert p.exists() and p.stat().st_size > 0


@pytest.mark.skipif(not pytest.importorskip('reportlab', reason='reportlab missing'), reason='reportlab not available')
def test_export_pdf(tmp_path):
    p = tmp_path / "out.pdf"
    try:
        export_pdf(str(p), SAMPLE_DATA, FIELDNAMES, logo_path=None)
    except MissingDependencyError:
        pytest.skip('reportlab missing')
    assert p.exists() and p.stat().st_size > 0
