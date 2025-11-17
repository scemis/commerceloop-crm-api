# alembic/versions/2fd05ef3f3c0_init.py
from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# revision identifiers, used by Alembic.
revision = "2fd05ef3f3c0"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # --- Enum for status ---
    status_enum = sa.Enum("pending", "completed", "canceled", name="statusenum")

    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("role_name", sa.String(50), nullable=False, unique=True),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False, unique=True),
        sa.Column("last_date_connection", sa.Date(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE")),
        sa.Column("hashed_pass", sa.Text, nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- personal_details ---
    op.create_table(
        "personal_details",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("phone_number", sa.String(15), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- companis (именно так в моделях) ---
    op.create_table(
        "companis",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("firm_name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False, unique=True),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- connect_companis (именно так в моделях) ---
    op.create_table(
        "connect_companis",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("worker_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("companis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("next_meeting", sa.DateTime, nullable=True),
        sa.Column("is_approved", sa.Boolean, nullable=True),
        sa.Column("status", status_enum, server_default="pending"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("last_update", sa.DateTime, nullable=True),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- categories ---
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- sub_categories ---
    op.create_table(
        "sub_categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("booked", sa.Integer, nullable=False, server_default="0"),
        sa.Column("length", sa.Integer, nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("price_per_piece", sa.Float, nullable=False, server_default="0"),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id")),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- products ---
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("length", sa.Integer, nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("last_update", sa.DateTime, nullable=True),
        sa.Column("status", status_enum, server_default="pending"),
        sa.Column("total_price", sa.Float, nullable=False, server_default="0"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="CASCADE")),
        sa.Column("sub_category_id", sa.Integer, sa.ForeignKey("sub_categories.id", ondelete="CASCADE")),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )

    # --- seed (без ORM; только SQL через bind) ---
    bind = op.get_bind()

    # роли
    for role_name in ("SuperAdmin", "Admin", "Worker"):
        bind.execute(sa.text(
            "INSERT IGNORE INTO roles (role_name) VALUES (:role_name)"
        ), {"role_name": role_name})

    # суперюзер (пароль-хеш поставьте свой, если нужно)
    res = bind.execute(sa.text("SELECT id FROM roles WHERE role_name = 'SuperAdmin'"))
    row = res.first()
    if row:
        role_id = row[0]
        bind.execute(sa.text("""
            INSERT INTO users (full_name, email, description, hashed_pass, role_id)
            SELECT :full_name, :email, :description, :hashed_pass, :role_id
            FROM DUAL
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = :email)
        """), {
            "full_name": "Den V",
            "email": "sa@cloop.ca",
            "description": "Leading tech firm",
            "hashed_pass": bcrypt_context.hash("Test123!"),
            "role_id": role_id,
        })

        # --- personal_details для этого пользователя (если ещё нет) ---
        u = bind.execute(sa.text(
            "SELECT id FROM users WHERE email = :email"
        ), {"email": "sa@osaco.ee"}).first()
        if u:
            uid = u[0]
            bind.execute(sa.text("""
                INSERT INTO personal_details (user_id, first_name, last_name, date_of_birth, city, country, phone_number)
                SELECT :uid, :first_name, :last_name, :dob, :city, :country, :phone
                FROM DUAL
                WHERE NOT EXISTS (SELECT 1 FROM personal_details WHERE user_id = :uid)
            """), {
                "uid": uid,
                "first_name": "Den",
                "last_name": "V",
                "dob": None,        # при желании задайте дату
                "city": None,
                "country": None,
                "phone": None,
            })

    # демо-данные категорий/подкатегорий/продуктов (идемпотентно)
    bind.execute(sa.text("""
        INSERT INTO categories (name)
        SELECT :name FROM DUAL WHERE NOT EXISTS (
            SELECT 1 FROM categories WHERE name = :name
        )
    """), {"name": "Electronics"})

    cat = bind.execute(sa.text(
        "SELECT id FROM categories WHERE name = :n"
    ), {"n": "Electronics"}).first()
    if cat:
        cat_id = cat[0]
        bind.execute(sa.text("""
            INSERT INTO sub_categories (name, count, booked, length, width, height, price_per_piece, category_id)
            SELECT :name, :count, 0, :length, :width, :height, :price, :cat_id
            FROM DUAL WHERE NOT EXISTS (
                SELECT 1 FROM sub_categories WHERE name = :name
            )
        """), {
            "name": "Smartphones", "count": 0,
            "length": 1, "width": 1, "height": 1, "price": 0, "cat_id": cat_id
        })

        sub = bind.execute(sa.text(
            "SELECT id FROM sub_categories WHERE name = :n"
        ), {"n": "Smartphones"}).first()
        if sub:
            sub_id = sub[0]
            bind.execute(sa.text("""
                INSERT INTO products (customer_name, count, length, width, height, status, category_id, sub_category_id)
                SELECT :customer_name, :count, :length, :width, :height, :status, :cat_id, :sub_id
                FROM DUAL WHERE NOT EXISTS (
                    SELECT 1 FROM products WHERE customer_name = :customer_name
                )
            """), {
                "customer_name": "John Doe", "count": 10,
                "length": 20, "width": 10, "height": 5,
                "status": "pending", "cat_id": cat_id, "sub_id": sub_id
            })

def downgrade():
    bind = op.get_bind()
    # Чистим данные (опционально)
    for table in ("products", "sub_categories", "categories", "connect_companis",
                  "companis", "personal_details", "users", "roles"):
        try:
            bind.execute(sa.text(f"DELETE FROM {table}"))
        except Exception:
            pass

    # Дроп таблиц (в обратном порядке зависимостей)
    op.drop_table("products")
    op.drop_table("sub_categories")
    op.drop_table("categories")
    op.drop_table("connect_companis")
    op.drop_table("companis")
    op.drop_table("personal_details")
    op.drop_table("users")
    op.drop_table("roles")

    # Дроп enum
    try:
        status_enum = sa.Enum(name="statusenum")
        status_enum.drop(bind, checkfirst=True)
    except Exception:
        pass
