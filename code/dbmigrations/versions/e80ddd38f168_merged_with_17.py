"""merged with #17

Revision ID: e80ddd38f168
Revises: 9a49b44cb424, 5b705a374a2a
Create Date: 2022-12-06 13:38:53.187809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e80ddd38f168"
down_revision = ("9a49b44cb424", "5b705a374a2a")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
