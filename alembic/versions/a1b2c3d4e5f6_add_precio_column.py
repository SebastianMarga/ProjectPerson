"""add precio column to productos

Revision ID: a1b2c3d4e5f6
Revises: df0c6c1e8cd1
Create Date: 2026-01-12 00:00:00.000000

Nota: Esta migración añade la columna `precio`. Si ya se ha aplicado en otros entornos, no
edite el archivo; cree una nueva migración para cambios posteriores.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'df0c6c1e8cd1'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'precio' column with a safe server_default, then remove the default
    op.add_column('productos', sa.Column('precio', sa.Float(), nullable=False, server_default='0.0'))
    # Remove server_default to keep schema clean
    op.alter_column('productos', 'precio', server_default=None)


def downgrade():
    op.drop_column('productos', 'precio')
