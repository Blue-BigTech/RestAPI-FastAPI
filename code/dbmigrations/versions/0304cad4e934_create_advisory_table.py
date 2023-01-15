"""create advisory table

Revision ID: 0304cad4e934
Revises: b463959ab216
Create Date: 2022-12-02 18:15:31.622751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0304cad4e934"
down_revision = "b463959ab216"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "advisory",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("crop", sa.String(), nullable=False),
        sa.Column("min_temp", sa.Float()),
        sa.Column("max_temp", sa.Float()),
        sa.Column("min_uv", sa.Float()),
        sa.Column("max_uv", sa.Float()),
        sa.Column("min_wind", sa.Float()),
        sa.Column("max_wind", sa.Float()),
        sa.Column("min_rainfall", sa.Float()),
        sa.Column("max_rainfall", sa.Float()),
        sa.Column("min_soilmoisture", sa.Float()),
        sa.Column("max_soilmoisture", sa.Float()),
        sa.Column("flag", sa.String()),
        sa.Column("advisory", sa.String()),
        sa.Column("stage_growth", sa.String()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["crop"], ["crop.id"]),
    )


def downgrade() -> None:
    op.drop_table("advisory")
