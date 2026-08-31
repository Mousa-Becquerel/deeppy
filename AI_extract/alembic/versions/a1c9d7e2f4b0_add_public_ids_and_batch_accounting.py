"""add public IDs + batch accounting fields

Adds:
  - public_id (int, unique) on products / batches / items — the human-readable
    incremental integer that goes into public URLs and QR codes, alongside the
    UUID primary key. Backfilled for existing rows so old products get stable
    IDs too.
  - available_quantity + available_unit on batches — the real "how much this
    batch is" number, used for the parent-vs-child availability check.

Note: SQLite doesn't have SERIAL, so public_id is a plain Integer with a
UNIQUE constraint; the repository fills it via SELECT COALESCE(MAX(...), 0)+1
at insert time. Alembic add_column doesn't auto-fill, so a manual UPDATE at
migration time backfills existing rows with a rowid-based ordering.

Revision ID: a1c9d7e2f4b0
Revises: ea3ad743d8c1
Create Date: 2026-08-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1c9d7e2f4b0'
# Linearize on top of audit_log (3b9f1c2d4e80), the actual current head on
# prod. Picked ea3ad743d8c1 initially — that was the parent of audit_log,
# which would have created a two-headed graph and blocked `alembic upgrade`.
down_revision: Union[str, None] = '3b9f1c2d4e80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add public_id on the three levels. Nullable during backfill; a unique
    # index is added AFTER the backfill so the intermediate NULLs don't clash.
    for table in ("products", "batches", "items"):
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.add_column(sa.Column("public_id", sa.Integer(), nullable=True))
        # Backfill: order by created_at (fall back to rowid) so numbering is
        # deterministic and matches the sequence people would expect (oldest
        # gets 1). SQLite's ROW_NUMBER() window function is available since
        # 3.25, which is fine for any modern container.
        op.execute(
            f"""
            WITH ordered AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, rowid) AS rn
                FROM {table}
            )
            UPDATE {table}
            SET public_id = (SELECT rn FROM ordered WHERE ordered.id = {table}.id)
            """
        )
        # Now enforce uniqueness. Kept as an index rather than a table
        # constraint to keep the batch_alter dance simple on SQLite.
        op.create_index(f"ix_{table}_public_id", table, ["public_id"], unique=True)

    with op.batch_alter_table("batches", schema=None) as batch_op:
        batch_op.add_column(sa.Column("available_quantity", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("available_unit", sa.String(length=16), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("batches", schema=None) as batch_op:
        batch_op.drop_column("available_unit")
        batch_op.drop_column("available_quantity")

    for table in ("items", "batches", "products"):
        op.drop_index(f"ix_{table}_public_id", table_name=table)
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.drop_column("public_id")
