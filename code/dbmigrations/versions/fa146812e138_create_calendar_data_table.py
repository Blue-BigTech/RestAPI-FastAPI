"""create calendar_data table

Revision ID: fa146812e138
Revises: 5b705a374a2a
Create Date: 2022-12-06 14:27:57.232685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fa146812e138"
down_revision = "5b705a374a2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calendar_data",
        sa.Column("id", sa.Integer(), index=True),
        sa.Column("farm", sa.String(), nullable=False),
        sa.Column(
            "title",
            sa.Enum(
                "Tilage",
                "Planting",
                "Fertilization",
                "Spraying",
                "Harvesting",
                "Planned Cost",
                "Other",
                name="calendar_data_title_type",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["farm"], ["farm.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("calendar_data")
