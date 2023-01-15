"""create predict_disease table

Revision ID: 6fdec2cdb850
Revises: 7d50917a37f1
Create Date: 2022-12-19 17:43:42.477056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6fdec2cdb850"
down_revision = "7d50917a37f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "predict_disease",
        sa.Column("class_name", sa.String(), nullable=False),
        sa.Column("disease", sa.String(), nullable=False),
        sa.Column("crop_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("class_name"),
        sa.ForeignKeyConstraint(["crop_id"], ["crop.id"]),
    )


def downgrade() -> None:
    op.drop_table("predict_disease")
