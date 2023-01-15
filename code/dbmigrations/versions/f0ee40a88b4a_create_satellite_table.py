"""create satellite table

Revision ID: f0ee40a88b4a
Revises: 7bb8a1d7ef18
Create Date: 2022-11-29 15:33:17.008531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0ee40a88b4a"
down_revision = "7bb8a1d7ef18"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "satellite",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("region_url", sa.String(length=100), nullable=False),
        sa.Column("satellite", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("satellites")
