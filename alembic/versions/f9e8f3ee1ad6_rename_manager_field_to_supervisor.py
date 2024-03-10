"""rename_manager_field_to_supervisor

Revision ID: f9e8f3ee1ad6
Revises: e32703bd6978
Create Date: 2024-02-29 02:31:55.976292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f9e8f3ee1ad6'
down_revision: Union[str, None] = 'e32703bd6978'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('second_order_data', 'project_supervisor_fio')
    op.add_column('second_order_data',
                  sa.Column('project_supervisor_fio', sa.String, nullable=True)
                  )


def downgrade() -> None:
    pass
