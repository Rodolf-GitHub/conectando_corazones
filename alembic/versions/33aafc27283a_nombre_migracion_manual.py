"""nombre_migracion_manual

Revision ID: 33aafc27283a
Revises: 20c26a738df1
Create Date: 2025-05-04 11:28:28.643764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33aafc27283a'
down_revision: Union[str, None] = '20c26a738df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
