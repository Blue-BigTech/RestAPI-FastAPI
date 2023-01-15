"""create_contact_table

Revision ID: 36bfcedf6c36
Revises: cfe6ca0849a0
Create Date: 2022-12-26 08:20:30.429092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "36bfcedf6c36"
down_revision = "cfe6ca0849a0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("request_type", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("contacts")
