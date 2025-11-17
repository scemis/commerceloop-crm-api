# alembic/versions/299b45f19533_add_activity_logs_table.py
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "299b45f19533"
down_revision: Union[str, None] = "9749f259d4e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

activity_enum = sa.Enum(
    "login", "logout", "create", "update", "delete",
    name="activitylogenum",
)

# ВАЖНО: здесь значения совпадают с core.enums.EntityEnum (множественное число)
entity_enum = sa.Enum(
    "users",
    "personal_details",
    "companis",
    "connect_companis",
    "categories",
    "sub_categories",
    "products",
    name="entityenum",
)

def upgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("action", activity_enum, nullable=False),        
        sa.Column("entity", entity_enum, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now(), nullable=True),
        sa.Column("emploee_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )

    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"], unique=False)
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"], unique=False)
    op.create_index("ix_activity_logs_entity", "activity_logs", ["entity"], unique=False)
    op.create_index("ix_activity_logs_emploee_id", "activity_logs", ["emploee_id"], unique=False)
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_activity_logs_user_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_emploee_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_entity", table_name="activity_logs")
    op.drop_index("ix_activity_logs_action", table_name="activity_logs")
    op.drop_index("ix_activity_logs_created_at", table_name="activity_logs")

    op.drop_table("activity_logs")
