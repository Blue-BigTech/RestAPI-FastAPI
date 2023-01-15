"""indice table add satistcal column


Revision ID: 02dd91b97c40
Revises: 5da4f11e0f46
Create Date: 2022-12-01 12:13:20.239799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02dd91b97c40"
down_revision = "5da4f11e0f46"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "indice", sa.Column("statistical_evalscript", sa.String(), nullable=True)
    ),


def downgrade() -> None:
    op.drop_column("indice", "statistical_evalscript")
