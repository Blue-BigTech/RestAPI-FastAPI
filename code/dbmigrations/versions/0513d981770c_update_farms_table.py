"""update farms table

Revision ID: 0513d981770c
Revises: 7eca3b106594
Create Date: 2022-11-25 19:52:48.295604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0513d981770c"
down_revision = "7eca3b106594"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "farm",
        sa.Column("harvesting_date", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.add_column("farm", sa.Column("season", sa.Integer()))
    op.add_column("farm", sa.Column("description", sa.String(200)))
    op.create_foreign_key(
        constraint_name="fk_crop_id",
        source_table="farm",
        referent_table="crop",
        local_cols=["crop"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    op.drop_column("farm", "harvesting_date")
    op.drop_column("farm", "season")
    op.drop_column("farm", "description")
    op.drop_constraint("fk_crop_id", table_name="farm")
