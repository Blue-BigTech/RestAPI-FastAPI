"""add catalogue column to satellite table

Revision ID: c65762dc355f
Revises: 7d35119667ad
Create Date: 2022-12-07 18:18:20.157370

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c65762dc355f"
down_revision = "7d35119667ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("satellite", sa.Column("catalogue", sa.Boolean()))


def downgrade() -> None:
    op.drop_column("satellite", "catalogue")
