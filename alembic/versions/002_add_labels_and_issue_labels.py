"""Add labels and issue_labels tables

Revision ID: 002
Revises: 001
Create Date: 2025-12-29 19:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create labels table
    op.create_table('labels',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_labels_name', 'labels', ['name'], unique=False)
    op.create_index('idx_labels_project', 'labels', ['project_id'], unique=False)
    op.create_index('ix_labels_is_deleted', 'labels', ['is_deleted'], unique=False)

    # Create issue_labels association table
    op.create_table('issue_labels',
        sa.Column('issue_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('label_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['label_id'], ['labels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('issue_id', 'label_id'),
        sa.UniqueConstraint('issue_id', 'label_id', name='uq_issue_label')
    )

    # Add indexes to issues table for better performance
    op.create_index('idx_issues_assignee_status', 'issues', ['assignee_id', 'status'], unique=False)
    op.create_index('idx_issues_project_status', 'issues', ['project_id', 'status'], unique=False)
    op.create_index('idx_issues_created_at', 'issues', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes from issues table
    op.drop_index('idx_issues_created_at', table_name='issues')
    op.drop_index('idx_issues_project_status', table_name='issues')
    op.drop_index('idx_issues_assignee_status', table_name='issues')
    
    # Drop issue_labels table
    op.drop_table('issue_labels')
    
    # Drop indexes and labels table
    op.drop_index('ix_labels_is_deleted', table_name='labels')
    op.drop_index('idx_labels_project', table_name='labels')
    op.drop_index('idx_labels_name', table_name='labels')
    op.drop_table('labels')
