"""add roles column to users table

Revision ID: 17916fb0e028
Revises: e7b99207999a
Create Date: 2022-12-08 13:12:26.649309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "17916fb0e028"
down_revision = "e7b99207999a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("role", sa.String(), nullable=False, server_default="farmer")
    )


def downgrade() -> None:
    op.drop_column("users", "role")
