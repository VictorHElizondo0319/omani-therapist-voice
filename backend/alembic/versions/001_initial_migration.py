"""Initial migration for OMANI-Therapist-Voice

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversation_sessions table
    op.create_table('conversation_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('cultural_context', sa.JSON(), nullable=True),
        sa.Column('emergency_contacts', sa.JSON(), nullable=True),
        sa.Column('is_crisis_session', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create conversation_turns table
    op.create_table('conversation_turns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('user_audio_data', sa.Text(), nullable=True),
        sa.Column('user_transcript', sa.Text(), nullable=True),
        sa.Column('user_emotional_analysis', sa.JSON(), nullable=True),
        sa.Column('ai_response_text', sa.Text(), nullable=True),
        sa.Column('ai_response_audio', sa.Text(), nullable=True),
        sa.Column('ai_model_used', sa.String(), nullable=True),
        sa.Column('cultural_adaptations', sa.JSON(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('latency_metrics', sa.JSON(), nullable=True),
        sa.Column('safety_flags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], )
    )
    
    # Create safety_incidents table
    op.create_table('safety_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('incident_type', sa.String(), nullable=False),
        sa.Column('severity_level', sa.String(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('user_input', sa.Text(), nullable=True),
        sa.Column('ai_response', sa.Text(), nullable=True),
        sa.Column('intervention_taken', sa.Text(), nullable=True),
        sa.Column('escalation_required', sa.Boolean(), nullable=False),
        sa.Column('escalated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], )
    )
    
    # Create cultural_adaptations table
    op.create_table('cultural_adaptations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=False),
        sa.Column('adapted_text', sa.Text(), nullable=False),
        sa.Column('adaptation_type', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], )
    )
    
    # Create indexes for better performance
    op.create_index('ix_conversation_sessions_user_id', 'conversation_sessions', ['user_id'])
    op.create_index('ix_conversation_sessions_started_at', 'conversation_sessions', ['started_at'])
    op.create_index('ix_conversation_turns_session_id', 'conversation_turns', ['session_id'])
    op.create_index('ix_conversation_turns_created_at', 'conversation_turns', ['created_at'])
    op.create_index('ix_safety_incidents_session_id', 'safety_incidents', ['session_id'])
    op.create_index('ix_safety_incidents_detected_at', 'safety_incidents', ['detected_at'])
    op.create_index('ix_cultural_adaptations_session_id', 'cultural_adaptations', ['session_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_cultural_adaptations_session_id', table_name='cultural_adaptations')
    op.drop_index('ix_safety_incidents_detected_at', table_name='safety_incidents')
    op.drop_index('ix_safety_incidents_session_id', table_name='safety_incidents')
    op.drop_index('ix_conversation_turns_created_at', table_name='conversation_turns')
    op.drop_index('ix_conversation_turns_session_id', table_name='conversation_turns')
    op.drop_index('ix_conversation_sessions_started_at', table_name='conversation_sessions')
    op.drop_index('ix_conversation_sessions_user_id', table_name='conversation_sessions')
    
    # Drop tables
    op.drop_table('cultural_adaptations')
    op.drop_table('safety_incidents')
    op.drop_table('conversation_turns')
    op.drop_table('conversation_sessions')
