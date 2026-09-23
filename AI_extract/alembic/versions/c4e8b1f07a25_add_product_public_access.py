"""add products.public_access

Sept 23 client feedback: only a hand-picked set of published products may be
opened as a full public DPP from the landing page. Everything else still shows
as a card, but the passport itself stays gated.

Defaults to False for every existing row — publishing something must never
have made it publicly readable retroactively. The two products the client
named are switched on separately (deploy/set_public_access.py), not here,
so the flag stays data rather than schema.

Revision ID: c4e8b1f07a25
Revises: a1c9d7e2f4b0
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4e8b1f07a25"
down_revision: Union[str, None] = "a1c9d7e2f4b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "public_access",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "public_access")
