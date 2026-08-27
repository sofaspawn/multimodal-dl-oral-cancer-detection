"""store patient metadata with each prediction"""

from alembic import op
import sqlalchemy as sa


revision = "20260827_0002"
down_revision = "20260825_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predictions", sa.Column("metadata_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("predictions", "metadata_json")
