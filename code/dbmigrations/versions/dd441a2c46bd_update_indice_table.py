"""update indice table

Revision ID: dd441a2c46bd
Revises: 9a49b44cb424
Create Date: 2022-12-05 18:26:34.193344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dd441a2c46bd"
down_revision = "9a49b44cb424"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "indice",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "indice",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column("indice", sa.Column("description", sa.String()))
    op.add_column("indice", sa.Column("source", sa.String()))
    op.add_column("indice", sa.Column("alias", sa.String(20)))


def downgrade() -> None:
    op.drop_column("indice", "created_at")
    op.drop_column("indice", "updated_at")
    op.drop_column("indice", "description")
    op.drop_column("indice", "source")
    op.drop_column("indice", "alias")
