"""create scouting table

Revision ID: e908662eb28e
Revises: 5b705a374a2a
Create Date: 2022-12-06 12:58:21.916622

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = "e908662eb28e"
down_revision = "5b705a374a2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scoutings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POINT",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=False,
        ),
        sa.Column(
            "note_type",
            sa.Enum(
                "Disease",
                "Pests",
                "Water logging",
                "Weeds",
                "Lodging",
                "Others",
                name="note_types",
            ),
            nullable=False,
        ),
        sa.Column("comments", sa.String(length=50), nullable=True),
        sa.Column("attachment", sa.String(length=50), nullable=True),
        sa.Column("farm", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["farm"], ["farm.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("scoutings")
