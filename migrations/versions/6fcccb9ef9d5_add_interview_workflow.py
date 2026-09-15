"""add interview workflow

Revision ID: 6fcccb9ef9d5
Revises: 3692d70e5619
Create Date: 2026-09-15 11:06:57.288094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fcccb9ef9d5'
down_revision: Union[str, Sequence[str], None] = '3692d70e5619'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely after partial SQLite migration."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names())

    # ---------------------------------------------------------
    # 1. INTERVIEWS
    # ---------------------------------------------------------

    if "interviews" not in existing_tables:
        op.create_table(
            "interviews",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("application_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("interview_type", sa.String(length=50), nullable=False),
            sa.Column("recruiter_notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.Column(
                "started_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "completed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["application_id"],
                ["applications.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("application_id"),
        )

    # Check index separately because the table may already exist.
    inspector = sa.inspect(bind)

    interview_indexes = {
        index["name"]
        for index in inspector.get_indexes("interviews")
    }

    if "ix_interviews_id" not in interview_indexes:
        op.create_index(
            "ix_interviews_id",
            "interviews",
            ["id"],
            unique=False,
        )

    # Refresh tables after possible creation
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # ---------------------------------------------------------
    # 2. INTERVIEW EVALUATIONS
    # ---------------------------------------------------------

    if "interview_evaluations" not in existing_tables:
        op.create_table(
            "interview_evaluations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("interview_id", sa.Integer(), nullable=False),
            sa.Column("technical_score", sa.Float(), nullable=False),
            sa.Column("communication_score", sa.Float(), nullable=False),
            sa.Column("problem_solving_score", sa.Float(), nullable=False),
            sa.Column("experience_score", sa.Float(), nullable=False),
            sa.Column("overall_score", sa.Float(), nullable=False),
            sa.Column(
                "recommendation",
                sa.String(length=50),
                nullable=False,
            ),
            sa.Column("strengths", sa.JSON(), nullable=False),
            sa.Column("concerns", sa.JSON(), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["interview_id"],
                ["interviews.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("interview_id"),
        )

    # ---------------------------------------------------------
    # 3. INTERVIEW QUESTIONS
    # ---------------------------------------------------------

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "interview_questions" not in existing_tables:
        op.create_table(
            "interview_questions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("interview_id", sa.Integer(), nullable=False),
            sa.Column("question_text", sa.Text(), nullable=False),
            sa.Column(
                "category",
                sa.String(length=50),
                nullable=False,
            ),
            sa.Column(
                "difficulty",
                sa.String(length=30),
                nullable=False,
            ),
            sa.Column(
                "expected_points",
                sa.JSON(),
                nullable=False,
            ),
            sa.Column("weight", sa.Float(), nullable=False),
            sa.Column("sequence", sa.Integer(), nullable=False),
            sa.Column(
                "is_followup",
                sa.Boolean(),
                nullable=False,
            ),
            sa.Column(
                "parent_question_id",
                sa.Integer(),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["interview_id"],
                ["interviews.id"],
            ),
            sa.ForeignKeyConstraint(
                ["parent_question_id"],
                ["interview_questions.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    # ---------------------------------------------------------
    # 4. INTERVIEW ANSWERS
    # ---------------------------------------------------------

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "interview_answers" not in existing_tables:
        op.create_table(
            "interview_answers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("question_id", sa.Integer(), nullable=False),
            sa.Column("answer_text", sa.Text(), nullable=False),
            sa.Column(
                "semantic_score",
                sa.Float(),
                nullable=True,
            ),
            sa.Column("strengths", sa.JSON(), nullable=False),
            sa.Column("concerns", sa.JSON(), nullable=False),
            sa.Column(
                "evaluator_reasoning",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["question_id"],
                ["interview_questions.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    # ---------------------------------------------------------
    # 5. APPLICATION COLUMNS
    # ---------------------------------------------------------

    inspector = sa.inspect(bind)

    application_columns = {
        column["name"]
        for column in inspector.get_columns("applications")
    }

    # Already exists in your DB, so this condition skips it.
    if "recruiter_decision" not in application_columns:
        op.add_column(
            "applications",
            sa.Column(
                "recruiter_decision",
                sa.String(length=50),
                nullable=True,
            ),
        )

    # Already exists in your DB, so this condition skips it.
    if "recruiter_notes" not in application_columns:
        op.add_column(
            "applications",
            sa.Column(
                "recruiter_notes",
                sa.Text(),
                nullable=True,
            ),
        )

    # This is currently missing from your DB.
    if "approved_for_interview" not in application_columns:
        op.add_column(
            "applications",
            sa.Column(
                "approved_for_interview",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('applications', 'approved_for_interview')
    op.drop_column('applications', 'recruiter_notes')
    op.drop_column('applications', 'recruiter_decision')
    op.drop_table('interview_answers')
    op.drop_table('interview_questions')
    op.drop_table('interview_evaluations')
    op.drop_index(op.f('ix_interviews_id'), table_name='interviews')
    op.drop_table('interviews')
    # ### end Alembic commands ###
