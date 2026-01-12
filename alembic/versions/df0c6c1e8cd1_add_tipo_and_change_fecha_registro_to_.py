"""add tipo and change Fecha_Registro to date

Revision ID: df0c6c1e8cd1
Revises: 
Create Date: 2026-01-11 23:19:22.564785

Nota: evite editar este archivo después de que se haya aplicado en otros entornos; prefiera
crear migraciones de avance para mantener el historial consistente entre entornos.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'df0c6c1e8cd1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Steps:
      1) Add column `tipo` with a server_default so existing rows get a value.
      2) Alter `Fecha_Registro` from DATETIME to DATE (MySQL truncates time automatically).
      3) Remove the server_default on `tipo` to make it effectively NOT NULL without default.
    """
    # 1) add column `tipo` with default '' so existing rows are populated
    op.add_column('productos', sa.Column('tipo', sa.String(length=255), nullable=False, server_default=''))

    # 2) change Fecha_Registro type to DATE
    op.alter_column('productos', 'Fecha_Registro', existing_type=sa.DateTime(), type_=sa.Date(), existing_nullable=True)

    # 3) remove server default so column behaves as normal NOT NULL column
    op.alter_column('productos', 'tipo', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # 1) revert Fecha_Registro type to DATETIME
    op.alter_column('productos', 'Fecha_Registro', existing_type=sa.Date(), type_=sa.DateTime(), existing_nullable=True)

    # 2) drop column `tipo`
    op.drop_column('productos', 'tipo')
