"""Add agent execution tracking and metrics tables

Revision ID: add_agent_metrics
Revises: 
Create Date: 2025-11-28

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'add_agent_metrics'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create agent_executions table
    op.create_table(
        'agent_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=False),
        sa.Column('output_text', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=False),
        sa.Column('success', sa.Boolean(), default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_executions_agent_type', 'agent_executions', ['agent_type'])
    op.create_index('ix_agent_executions_id', 'agent_executions', ['id'])
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('collection_name', sa.String(length=255), nullable=False),
        sa.Column('chunk_count', sa.Integer(), default=0),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_id', 'documents', ['id'])
    
    # Create agent_metrics table
    op.create_table(
        'agent_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('total_executions', sa.Integer(), default=0),
        sa.Column('successful_executions', sa.Integer(), default=0),
        sa.Column('failed_executions', sa.Integer(), default=0),
        sa.Column('avg_response_time_ms', sa.Float(), default=0.0),
        sa.Column('total_tokens_used', sa.Integer(), default=0),
        sa.Column('avg_rating', sa.Float(), default=0.0),
        sa.Column('total_ratings', sa.Integer(), default=0),
        sa.Column('last_updated', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_type')
    )
    op.create_index('ix_agent_metrics_agent_type', 'agent_metrics', ['agent_type'], unique=True)
    op.create_index('ix_agent_metrics_id', 'agent_metrics', ['id'])


def downgrade():
    op.drop_index('ix_agent_metrics_id', table_name='agent_metrics')
    op.drop_index('ix_agent_metrics_agent_type', table_name='agent_metrics')
    op.drop_table('agent_metrics')
    
    op.drop_index('ix_documents_id', table_name='documents')
    op.drop_table('documents')
    
    op.drop_index('ix_agent_executions_id', table_name='agent_executions')
    op.drop_index('ix_agent_executions_agent_type', table_name='agent_executions')
    op.drop_table('agent_executions')
