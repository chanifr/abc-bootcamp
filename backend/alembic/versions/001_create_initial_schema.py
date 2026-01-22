"""create initial schema

Revision ID: 001
Revises:
Create Date: 2026-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('read_only', 'editor', 'admin', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create candidates table
    op.create_table(
        'candidates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('Active', 'Hired', 'Rejected', 'Withdrawn', name='candidatestatus'), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_candidates_email', 'candidates', ['email'])

    # Create positions table
    op.create_table(
        'positions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('department', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=False),
        sa.Column('min_experience_years', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('Open', 'Closed', 'On Hold', name='positionstatus'), nullable=False),
        sa.Column('posted_date', sa.Date(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create experiences table
    op.create_table(
        'experiences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_experiences_candidate_id', 'experiences', ['candidate_id'])

    # Create education table
    op.create_table(
        'education',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), nullable=False),
        sa.Column('institution', sa.String(255), nullable=False),
        sa.Column('degree', sa.String(255), nullable=False),
        sa.Column('field', sa.String(255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_education_candidate_id', 'education', ['candidate_id'])

    # Create skills table
    op.create_table(
        'skills',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('level', sa.Enum('Beginner', 'Intermediate', 'Advanced', 'Expert', name='skilllevel'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_skills_candidate_id', 'skills', ['candidate_id'])
    op.create_index('ix_skills_name', 'skills', ['name'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), nullable=False),
        sa.Column('type', sa.Enum('CV', 'Cover Letter', 'Certificate', 'Other', name='documenttype'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(512), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_documents_candidate_id', 'documents', ['candidate_id'])

    # Create position_skills table
    op.create_table(
        'position_skills',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('position_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_position_skills_position_id', 'position_skills', ['position_id'])

    # Create candidate_positions junction table
    op.create_table(
        'candidate_positions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('candidate_id', sa.String(36), nullable=False),
        sa.Column('position_id', sa.String(36), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('candidate_id', 'position_id', name='uq_candidate_position'),
    )
    op.create_index('ix_candidate_positions_candidate_id', 'candidate_positions', ['candidate_id'])
    op.create_index('ix_candidate_positions_position_id', 'candidate_positions', ['position_id'])


def downgrade() -> None:
    op.drop_table('candidate_positions')
    op.drop_table('position_skills')
    op.drop_table('documents')
    op.drop_table('skills')
    op.drop_table('education')
    op.drop_table('experiences')
    op.drop_table('positions')
    op.drop_table('candidates')
    op.drop_table('users')
