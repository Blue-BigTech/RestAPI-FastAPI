"""create crops table

Revision ID: 7eca3b106594
Revises: 8c29df4c0e9f
Create Date: 2022-11-25 15:17:32.567304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7eca3b106594"
down_revision = "8c29df4c0e9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=200)),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("crop")
