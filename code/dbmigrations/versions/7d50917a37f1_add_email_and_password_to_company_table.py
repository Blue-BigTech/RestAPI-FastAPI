"""add email and password to company table

Revision ID: 7d50917a37f1
Revises: 6b4e3ca0d847
Create Date: 2022-12-12 00:39:09.212182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d50917a37f1"
down_revision = "6b4e3ca0d847"
branch_labels = None
depends_on = None

table = "companies"


def upgrade() -> None:
    op.add_column(table, sa.Column("email", sa.String(), nullable=True))
    op.add_column(table, sa.Column("password", sa.String(), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column(table, "email")
    op.drop_column(table, "password")
    pass
