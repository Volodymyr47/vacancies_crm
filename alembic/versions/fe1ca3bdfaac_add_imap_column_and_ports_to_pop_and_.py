"""Add imap column, and ports to pop and smtp

Revision ID: fe1ca3bdfaac
Revises: 3ef0a47982d5
Create Date: 2023-02-23 10:55:09.934808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe1ca3bdfaac'
down_revision = '3ef0a47982d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email_creds', sa.Column('pop_port', sa.Integer(), nullable=True))
    op.add_column('email_creds', sa.Column('imap_server', sa.String(length=100), nullable=True))
    op.add_column('email_creds', sa.Column('imap_port', sa.Integer(), nullable=True))
    op.add_column('email_creds', sa.Column('smtp_port', sa.Integer(), nullable=True))
    op.alter_column('email_creds', 'pop_server',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('email_creds', 'smtp_server',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('email_creds', 'smtp_server',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.alter_column('email_creds', 'pop_server',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
    op.drop_column('email_creds', 'smtp_port')
    op.drop_column('email_creds', 'imap_port')
    op.drop_column('email_creds', 'imap_server')
    op.drop_column('email_creds', 'pop_port')
    # ### end Alembic commands ###
