"""create evalscript table

Revision ID: 5da4f11e0f46
Revises: f0ee40a88b4a
Create Date: 2022-11-30 08:45:09.534558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5da4f11e0f46"
down_revision = "f0ee40a88b4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "indice",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("evalscript", sa.String(), nullable=False),
        sa.Column("satellite", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["satellite"], ["satellite.name"]),
        sa.PrimaryKeyConstraint("name", "satellite"),
    )


def downgrade() -> None:
    op.drop_table("indice")
