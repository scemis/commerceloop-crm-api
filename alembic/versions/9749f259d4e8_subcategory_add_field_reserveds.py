from alembic import op
import sqlalchemy as sa

revision = "9749f259d4e8"
down_revision = "2fd05ef3f3c0"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("sub_categories")}
    if "booked" not in cols:
        op.add_column("sub_categories", sa.Column("booked", sa.Integer(), nullable=False, server_default="0"))
        op.create_index(op.f("ix_sub_categories_booked"), "sub_categories", ["booked"], unique=False)

def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("sub_categories")}
    if "booked" in cols:
        op.drop_index(op.f("ix_sub_categories_booked"), table_name="sub_categories")
        op.drop_column("sub_categories", "booked")
