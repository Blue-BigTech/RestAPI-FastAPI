"""add crop rotation table and update farms table

Revision ID: 9a49b44cb424
Revises: 0304cad4e934
Create Date: 2022-12-02 21:49:38.467455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9a49b44cb424"
down_revision = "0304cad4e934"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update farms table
    op.drop_column("farm", "sowing_date")
    op.drop_column("farm", "harvesting_date")
    op.drop_column("farm", "season")
    op.drop_constraint("fk_crop_id", "farm")
    op.drop_column("farm", "crop")

    # Add column
    op.add_column(
        "farm",
        sa.Column(
            "area",
            sa.Float(),
            sa.Computed(
                "((ST_Area(ST_setSRID(geometry, 4326)::geography)) * 0.0002471054)",
                True,
            ),
        ),
    )

    # Create farm_crop table for crop rotation
    op.create_table(
        "farm_crop",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farm_id", sa.String(), nullable=False),
        sa.Column("crop_id", sa.String(), nullable=False),
        sa.Column("sowing_date", sa.Date()),
        sa.Column("harvesting_date", sa.Date()),
        sa.Column("season", sa.Integer()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"]),
        sa.ForeignKeyConstraint(["crop_id"], ["crop.id"]),
    )


def downgrade() -> None:
    op.add_column("farm", sa.Column("sowing_date", sa.Date(), nullable=False))
    op.add_column("farm", sa.Column("harvesting_date", sa.Date(), nullable=False))
    op.add_column("farm", sa.Column("season", sa.Integer(), nullable=False))
    op.add_column("farm", sa.Column("crop", sa.String(), nullable=False))
    op.drop_column("farm", "area")
    op.create_foreign_key(
        constraint_name="fk_crop_id",
        source_table="farm",
        referent_table="crop",
        local_cols=["crop"],
        remote_cols=["id"],
    )
    op.drop_table("farm_crop")
