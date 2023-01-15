"""Remove length on varchar columns

Revision ID: 6b4e3ca0d847
Revises: 17916fb0e028
Create Date: 2022-12-08 15:30:37.175260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b4e3ca0d847"
down_revision = "17916fb0e028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # farm table
    op.alter_column("farm", "description", type_=sa.String())

    # # crop table
    op.alter_column("crop", "name", type_=sa.String())
    op.alter_column("crop", "description", type_=sa.String())
    op.alter_column("crop", "yield_unit", type_=sa.String())
    op.alter_column("crop", "yield_per", type_=sa.String())

    # # indice table
    op.alter_column("indice", "alias", type_=sa.String())
    op.alter_column("indice", "name", type_=sa.String())
    op.alter_column("indice", "satellite", type_=sa.String())

    # scoutings
    op.alter_column("scoutings", "comments", type_=sa.String())
    op.alter_column("scoutings", "attachment", type_=sa.String())
    op.alter_column("scoutings", "farm", type_=sa.String())

    # satellite
    op.alter_column("satellite", "name", type_=sa.String())
    op.alter_column("satellite", "region_url", type_=sa.String())
    op.alter_column("satellite", "satellite", type_=sa.String())


def downgrade() -> None:
    # farm
    op.alter_column("farm", "description", type_=sa.String(200))

    # crop
    op.alter_column("crop", "name", type_=sa.String(50))
    op.alter_column("crop", "description", type_=sa.String(200))
    op.alter_column("crop", "yield_unit", type_=sa.String(20))
    op.alter_column("crop", "yield_per", type_=sa.String(20))

    # Indice
    op.alter_column("indice", "name", type_=sa.String(50))
    op.alter_column("indice", "alias", type_=sa.String(20))
    op.alter_column("indice", "satellite", type_=sa.String(20))

    # Scoutings
    op.alter_column("scoutings", "comments", type_=sa.String(50))
    op.alter_column("scoutings", "attachment", type_=sa.String(50))
    op.alter_column("scoutings", "farm", type_=sa.String(50))

    # satellite
    op.alter_column("satellite", "name", type_=sa.String(50))
    op.alter_column("satellite", "region_url", type_=sa.String(100))
    op.alter_column("satellite", "satellite", type_=sa.String(50))
