"""initial migration

Revision ID: e32703bd6978
Revises: 
Create Date: 2024-02-29 02:01:17.200140

"""
import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_file as sa_file

from validators import CustomSizeValidator, CustomContentTypeValidator

# revision identifiers, used by Alembic.
revision: str = 'e32703bd6978'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'first_order_data',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('order_type', sa.String),
        sa.Column('fio', sa.String),
        sa.Column('email', sa.String),
        sa.Column('position', sa.String),
        sa.Column('basis', sa.String),
        sa.Column('phone_number', sa.String),
        sa.Column('manager_fio', sa.String),
        sa.Column('project_supervisor_fio', sa.String),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.now())
    )
    op.create_table(
        'second_order_data',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('order_type', sa.String),
        sa.Column('fio', sa.String),
        sa.Column('user_role', sa.String),
        sa.Column('basis', sa.String, nullable=True),
        sa.Column('document', sa_file.FileField, validators=[
            CustomSizeValidator(max_size='5M'),
            CustomContentTypeValidator(['text/pdf', 'text/word'])
        ], nullable=True),
        sa.Column('phone_number', sa.String),
        sa.Column('project_supervisor_fio', sa.String),
        sa.Column('first_date', sa.Date),
        sa.Column('second_date', sa.Date, nullable=True),
        sa.Column('objects', sa.String),

        sa.Column('created_at', sa.DateTime, default=datetime.datetime.now())
    )
    op.create_table(
        'third_order_data',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('order_type', sa.String),
        sa.Column('fio', sa.String),
        sa.Column('email', sa.String),
        sa.Column('position', sa.String),
        sa.Column('basis', sa.String),
        sa.Column('phone_number', sa.String),
        sa.Column('project_supervisor_fio', sa.String),
        sa.Column('document', sa_file.FileField, validators=[
            CustomSizeValidator(max_size='5M'),
            CustomContentTypeValidator(['text/pdf', 'text/word'])
        ]),

        sa.Column('created_at', sa.DateTime, default=datetime.datetime.now())
    )


def downgrade() -> None:
    pass
