"""create_schedule_call_table

Revision ID: 74fc67c84dd4
Revises: 36bfcedf6c36
Create Date: 2023-01-12 02:44:33.814676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "74fc67c84dd4"
down_revision = "36bfcedf6c36"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedule_calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "how_to_contact",
            sa.Enum(
                "whatsapp",
                "zoom",
                "phone",
                name="how_to_contact",
            ),
            nullable=False,
        ),
        sa.Column("date_time", sa.DateTime()),
        sa.Column(
            "topic",
            sa.Enum(
                "general",
                "disease",
                "plantation",
                "harvesting",
                "pesticides",
                "waste",
                name="topic",
            ),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "type_of_expert",
            sa.Enum(
                "local",
                "international",
                name="type_of_expert",
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("schedule_calls")
