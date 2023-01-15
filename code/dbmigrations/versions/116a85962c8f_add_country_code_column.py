"""add country code column

Revision ID: 116a85962c8f
Revises: 6b4e3ca0d847
Create Date: 2022-12-14 14:44:45.570107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "116a85962c8f"
down_revision = "6b4e3ca0d847"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("country_code", sa.Integer(), nullable=False, server_default="91"),
    )


def downgrade() -> None:
    op.drop_column("users", "country_code")
