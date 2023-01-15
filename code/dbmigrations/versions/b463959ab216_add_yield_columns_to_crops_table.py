"""add yield columns to crops table

Revision ID: b463959ab216
Revises: 02dd91b97c40
Create Date: 2022-12-02 13:36:52.270361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b463959ab216"
down_revision = "02dd91b97c40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crop", sa.Column("yield_value", sa.Float()))
    op.add_column("crop", sa.Column("yield_unit", sa.String(20)))
    op.add_column("crop", sa.Column("yield_per", sa.String(20)))


def downgrade() -> None:
    op.drop_column("crop", "yield_value")
    op.drop_column("crop", "yield_unit")
    op.drop_column("crop", "yield_per")
