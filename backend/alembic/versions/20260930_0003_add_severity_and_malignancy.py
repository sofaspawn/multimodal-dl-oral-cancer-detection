"""Add severity and potentially_malignant columns to predictions table"""

from alembic import op
import sqlalchemy as sa


revision = "20260930_0003"
down_revision = "20260827_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predictions", sa.Column("severity", sa.String(16), nullable=True))
    op.add_column("predictions", sa.Column("potentially_malignant", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("predictions", "potentially_malignant")
    op.drop_column("predictions", "severity")
