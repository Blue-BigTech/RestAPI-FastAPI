"""farms timestamp to date

Revision ID: 822afdfbec5d
Revises: 0513d981770c
Create Date: 2022-11-29 12:55:21.181987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "822afdfbec5d"
down_revision = "0513d981770c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("farm", "sowing_date", type_=sa.Date())
    op.alter_column("farm", "harvesting_date", type_=sa.Date())


def downgrade() -> None:
    op.alter_column("farm", "sowing_date", type_=sa.TIMESTAMP(timezone=True))
    op.alter_column("farm", "harvesting_date", type_=sa.TIMESTAMP(timezone=True))
