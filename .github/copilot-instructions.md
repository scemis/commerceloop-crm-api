# Project Cheat Sheet: commerceloop-crm-api

---

## Architecture Overview

### Main Directories & Files

```
commerceloop-crm-api/
├── api/                          # Domain modules (CRUD operations, routes, models)
│   ├── activity_logs/            # Activity/audit logging
│   ├── auth/                      # Authentication & authorization
│   ├── categories/               # Product categories
│   ├── companies/                # Company management
│   ├── connect_companies/        # Worker-to-Company relationships
│   ├── products/                 # Product catalog
│   ├── roles/                    # Role-based access control
│   └── users/                    # User management & personal details
│
├── core/                         # Core utilities & infrastructure
│   ├── config.py                 # Environment & settings (Pydantic BaseSettings)
│   ├── db.py                     # Database engine, session factory, declarative base
│   ├── deps.py                   # Dependency injection (get_db for all routes)
│   ├── enums.py                  # Shared enums (StatusEnum, ActivityLogEnum, EntityEnum)
│   ├── logger.py                 # Custom logging utility
│   └── security.py               # JWT, password hashing, token creation
│
├── alembic/                      # Database migrations (Alembic)
│   ├── versions/                 # Migration scripts
│   │   ├── 2fd05ef3f3c0_init.py  # Initial schema setup
│   │   ├── 299b45f19533_add_activity_logs_table.py
│   │   └── 9749f259d4e8_subcategory_add_field_reserveds.py
│   ├── env.py                    # Alembic environment config
│   └── alembic.ini               # Alembic configuration
│
├── main.py                       # FastAPI app entry point
├── database.py                   # Legacy DB setup (duplicates core/db.py)
├── config.py                     # Legacy settings (duplicates core/config.py)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container image definition
├── localhost-cert.pem            # HTTPS certificate (local dev)
├── localhost-cert-key.pem        # HTTPS private key (local dev)
└── .env                          # Environment variables (not in repo)
```

### Key Technologies

- **FastAPI** – Modern async web framework
- **SQLAlchemy** – ORM for database operations
- **Pydantic** – Data validation & serialization (schemas)
- **Alembic** – Database migrations
- **JWT (python-jose)** – Token-based authentication
- **bcrypt (passlib)** – Password hashing
- **Azure Database for PostgreSQL** – Primary database engine (migrated from MySQL)

---

## Key Components & Patterns

### 1. **Dependency Injection Pattern** ✅

Used throughout to provide request-scoped resources:

```python
# core/deps.py
from core.db import SessionLocal
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in routes
@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return crud.list_users(db)
```

**Where it's used:**
- `get_db` – Every route that accesses the database
- `get_current_user` – Every protected route that requires authentication

---

### 2. **CRUD Pattern** ✅

Each domain module follows the CRUD structure:

```
api/{domain}/
├── models.py      # SQLAlchemy ORM models
├── schemas.py     # Pydantic request/response schemas
├── crud.py        # Database operations (Create, Read, Update, Delete)
├── routes.py      # FastAPI endpoints
└── __init__.py
```

**Example:** `api/users/`
- **models.py** → `Users`, `PersonalDetails` (SQLAlchemy)
- **schemas.py** → `SearchUserRequest`, `EditUserRequest` (Pydantic)
- **crud.py** → `get_user_by_id()`, `list_users_joined()`, `update_user()`
- **routes.py** → GET/PUT/POST endpoints

---

### 3. **Centralized Configuration** ✅

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()  # Loads from .env
```

**Access anywhere:**
```python
from core.config import settings
db_url = settings.DATABASE_URL
secret = settings.SECRET_KEY
```

---

### 4. **JWT-Based Authentication** ✅

Two-layer security:

```python
# core/security.py
def create_access_token(payload: dict, expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    to_encode['exp'] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return {'email': payload['email'], 'id': payload['id'], 'role': payload['role']}
```

**Token includes:** `email`, `id` (user ID), `role` (role ID)

**Applied to routes:**
```python
# Open routes (auth only)
app.include_router(auth_router)

# Protected routes (require token)
app.include_router(users_router, dependencies=[Depends(get_current_user)])
app.include_router(companies_router, dependencies=[Depends(get_current_user)])
```

---

### 5. **Activity Logging Pattern** ✅

Every action is logged for audit trails:

```python
# From api/auth/routes.py
activity_crud.create_activity_log(
    db,
    ActivityLogCreate(
        action=ActivityLogEnum.create,
        description=f"Created user {user.email}",
        entity=EntityEnum.users,
        actor_id=request.state.user['id'],
        target_user_id=user.id,
        ip_address=request.client.host
    )
)
```

**Logged entities:** users, personal_details, companies, products, categories, etc.

---

### 6. **Request Logging Pattern** ✅

Every endpoint logs key metadata:

```python
from core.logger import logger

@router.get("/users/by-id/{userId}")
def read_user(request: Request, userId: int, db: Session = Depends(get_db)):
    obj = crud.get_user_by_id(db, userId)
    
    # Log with context
    logger.info(
        f"[USER][GET_BY_ID] actor_id={request.state.user['id']} "
        f"target_user_id={userId} found={bool(obj)} ip={request.client.host}"
    )
    return obj
```

**Standard fields logged:**
- `actor_id` – Who performed the action
- `target_id` – What was affected
- `ip` – Request source
- `action` – What happened (GET, PUT, DELETE, etc.)

---

## Reusable Utilities & Helpers

### Don't Reinvent the Wheel – Use These!

#### **1. Database Session** 🔄
```python
from core.deps import get_db
from sqlalchemy.orm import Session

# In any route
def my_route(db: Session = Depends(get_db)):
    users = db.query(Users).all()
    return users
```

---

#### **2. Configuration** 🔧
```python
from core.config import settings

DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
```

---

#### **3. Security Utilities** 🔐
```python
from core.security import (
    hash_password,              # Hash plain passwords for storage
    verify_password,            # Verify plain vs hashed password
    create_access_token,        # Create JWT token
    get_current_user            # Dependency to extract current user
)

# Hash password before storing
hashed = hash_password("mypassword")

# Verify on login
if verify_password("mypassword", user.hashed_pass):
    token = create_access_token({"email": user.email, "id": user.id})
```

---

#### **4. Logger** 📝
```python
from core.logger import logger

logger.info("User created successfully")
logger.error("Database connection failed")
logger.warning("Request timeout")
```

---

#### **5. Enums (Shared Constants)** 📋
```python
from core.enums import ActivityLogEnum, EntityEnum, StatusEnum

# ActivityLogEnum: login, create, edit, delete, email
# EntityEnum: users, personal_details, companis, products, categories, etc.
# StatusEnum: pending, completed, canceled
```

---

#### **6. Activity Logging** 📊
```python
from api.activity_logs import crud as activity_crud
from api.activity_logs.schemas import ActivityLogCreate
from core.enums import ActivityLogEnum, EntityEnum

activity_crud.create_activity_log(
    db,
    ActivityLogCreate(
        action=ActivityLogEnum.create,        # What happened
        description="User profile updated",   # Details
        entity=EntityEnum.users,              # What was modified
        actor_id=current_user_id,             # Who did it
        user_id=target_user_id,               # Who it affected
    )
)
```

---

## Repeated Components & Patterns

### ✅ Components Used Over and Over

| Component | Where Used | Purpose |
|-----------|-----------|---------|
| `Session = Depends(get_db)` | Every CRUD route | Get DB connection |
| `Request` parameter | Most routes | Extract user info & IP |
| `request.state.user` | All protected routes | Get authenticated user data |
| `logger.info(f"[ENTITY][ACTION]...")` | All routes | Audit trail |
| `activity_crud.create_activity_log()` | After mutations | Track entity changes |
| `HTTPException(status_code=404)` | CRUD ops | Error handling |
| `db.query(Model).filter(...).first()` | CRUD `get` | Fetch single record |
| `db.query(Model).offset().limit()` | List endpoints | Pagination |
| `db.commit()` | All mutations | Persist changes |

### 📋 Route Structure Pattern

Every route follows this template:

```python
@router.get("/endpoint")
def endpoint_name(
    request: Request,                           # Always include for logging
    db: Session = Depends(get_db),             # Always for DB access
    # ... other parameters
):
    # 1. Perform operation
    result = crud.operation(db, ...)
    
    # 2. Log the action
    logger.info(f"[ENTITY][ACTION] actor_id={request.state.user['id']} ...")
    
    # 3. (Optional) Create activity log
    activity_crud.create_activity_log(db, ActivityLogCreate(...))
    
    # 4. Return result
    return result
```

---

## APIs and Data Flow

### **Frontend ↔ Backend Communication**

#### **1. Authentication Flow** 🔐

```
┌─────────────┐                                  ┌──────────────┐
│   Frontend  │                                  │   Backend    │
└──────┬──────┘                                  └──────┬───────┘
       │                                                 │
       │  1. POST /auth/token (email + password)        │
       │────────────────────────────────────────────────>│
       │                                                 │
       │                        2. Validate credentials  │
       │                        3. Hash & compare pwd    │
       │                                                 │
       │  4. Return JWT token + user data               │
       │<────────────────────────────────────────────────│
       │                                                 │
       │  5. Store token (localStorage/cookie)          │
       │                                                 │
       │  6. Include in Authorization header            │
       │    or Cookie for next requests                 │
       │                                                 │
```

**Endpoints:**
- `POST /auth/token` – Login (returns access token)
- `POST /auth/employee/add` – Create new user

---

#### **2. CRUD Operations Flow** 📊

**Example: Get User**

```
┌─────────────┐                                  ┌──────────────┐
│   Frontend  │                                  │   Backend    │
└──────┬──────┘                                  └──────┬───────┘
       │                                                 │
       │  GET /auth/users/by-id/5                       │
       │  Header: Authorization: Bearer {token}         │
       │────────────────────────────────────────────────>│
       │                                                 │
       │                        1. Validate token       │
       │                           (get_current_user)   │
       │                        2. Extract user ID from │
       │                           request.state.user   │
       │                        3. Query DB:            │
       │                           Users.get(5)         │
       │                        4. Log action            │
       │                                                 │
       │  Return: { id, full_name, email, role, ... }  │
       │<────────────────────────────────────────────────│
       │                                                 │
```

**Endpoints (Protected):**
- `GET /auth/users/by-id/{userId}` – Get user by ID
- `GET /auth/user/all` – List all users (paginated)
- `PUT /auth/user/edit/{userId}` – Update user
- `DELETE /auth/user/{userId}` – Delete user (implied)

---

#### **3. Relationship/Join Queries** 🔗

**Example: List users with their details and roles**

```python
# Query: Users JOIN PersonalDetails JOIN Roles
users = db.query(Users, PersonalDetails, Roles) \
    .join(PersonalDetails, PersonalDetails.user_id == Users.id) \
    .join(Roles, Users.role_id == Roles.id) \
    .offset(skip).limit(limit).all()

# Response transformation
return [
    SearchUserRequest(
        userId=u.id,
        first_name=det.first_name,
        email=u.email,
        role=role.role_name,
        # ... other fields
    )
    for u, det, role in users
]
```

---

#### **4. Request/Response Data Flow** 📤

```
Frontend Request:
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "city": "New York",
  "country": "USA",
  "role_id": 2
}

           ↓
           
   Pydantic Schema Validation
   (api/{domain}/schemas.py)
   
           ↓
           
   CRUD Operation
   (api/{domain}/crud.py)
   - Users table insert
   - PersonalDetails insert
   
           ↓
           
Backend Response:
{
  "id": 42,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role_id": 2,
  "created_at": "2025-11-17T10:30:00"
}
```

---

#### **5. Activity Logging Data Flow** 📋

Every mutation creates an audit trail:

```
User edits profile
        ↓
PUT /auth/user/edit/{userId}
        ↓
crud.update_user(db, userId, data)
        ↓
db.commit()  ← Changes saved to DB
        ↓
activity_crud.create_activity_log(
    db,
    ActivityLogCreate(
        action='edit',
        entity='users',
        actor_id=current_user_id,
        user_id=target_user_id,
        description='Profile updated'
    )
)
        ↓
ActivityLogs table INSERT
        ↓
Audit trail created → Later queryable for compliance/debugging
```

---

## PostgreSQL Database Configuration

### **Connection String** 🔗

The project uses **Azure Database for PostgreSQL** (migrated from MySQL).

```python
# From .env file
DATABASE_URL=postgresql+psycopg2://username:password@hostname:5432/database_name

# Example Azure configuration
DATABASE_URL=postgresql+psycopg2://master:password@postgresql-server-crm.postgres.database.azure.com:5432/crm_db
```

**Components:**
- **Driver:** `postgresql+psycopg2` (uses psycopg2-binary)
- **User:** PostgreSQL username
- **Password:** PostgreSQL password
- **Host:** Database server hostname
- **Port:** 5432 (PostgreSQL default)
- **Database:** Database name

### **Database Setup** 📋

1. **Create database in PostgreSQL:**
   ```sql
   CREATE DATABASE crm_db;
   ```

2. **Configure `.env` file:**
   ```properties
   DATABASE_URL=postgresql+psycopg2://master:password@postgresql-server-crm.postgres.database.azure.com:5432/crm_db
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=480
   ```

3. **Install PostgreSQL driver:**
   ```bash
   pip install psycopg2-binary==2.9.11
   ```

4. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

### **Migration History** 📊

The project has 3 database migrations (all PostgreSQL-compatible):

| Migration ID | Description | Tables |
|--------------|-------------|--------|
| `2fd05ef3f3c0` | Initial schema | roles, users, personal_details, companies, categories, sub_categories, products |
| `9749f259d4e8` | Sub-category fields | Added `booked` field to sub_categories |
| `299b45f19533` | Activity logging | activity_logs table with enum types |

### **PostgreSQL-Specific Notes** ⚠️

1. **Boolean Defaults**
   - PostgreSQL requires `true` or `false`, not `0` or `1`
   - Default: `server_default=sa.text("false")`

2. **Enum Types**
   - PostgreSQL uses native ENUM types
   - Enums: `statusenum`, `activitylogenum`, `entityenum`
   - SQLAlchemy automatically manages enum creation/deletion

3. **Upsert Operations**
   - PostgreSQL: `ON CONFLICT DO NOTHING`
   - Not MySQL: `INSERT IGNORE` (no longer used)

4. **Insert Syntax**
   - PostgreSQL: Direct `VALUES` clause
   - Not MySQL: `FROM DUAL` (no longer used)

### **Connection Troubleshooting** 🔧

**Error: "password authentication failed"**
- Verify username and password in `.env`
- Check Azure PostgreSQL server credentials

**Error: "no pg_hba_conf entry"**
- Add your IP to Azure PostgreSQL firewall rules
- Go to Azure Portal → PostgreSQL Server → Firewall Rules → Add Client IP

**Error: "database does not exist"**
- Create the database manually: `CREATE DATABASE crm_db;`
- Run migrations: `alembic upgrade head`

**Error: "relation does not exist"**
- Migrations not applied: `alembic upgrade head`
- Check migration status: `alembic current`

---

## Common Tasks & Quick Reference

### **Adding a New CRUD Endpoint**

1. **Create model** (`api/{domain}/models.py`)
   ```python
   class MyEntity(Base):
       __tablename__ = "my_entities"
       id = Column(Integer, primary_key=True)
       name = Column(String(100))
   ```

2. **Create schema** (`api/{domain}/schemas.py`)
   ```python
   class MyEntityCreate(BaseModel):
       name: str
   ```

3. **Create CRUD** (`api/{domain}/crud.py`)
   ```python
   def create_entity(db: Session, data: MyEntityCreate):
       entity = MyEntity(**data.dict())
       db.add(entity)
       db.commit()
       return entity
   ```

4. **Add route** (`api/{domain}/routes.py`)
   ```python
   @router.post("/entities")
   def create(data: MyEntityCreate, db: Session = Depends(get_db), request: Request):
       entity = crud.create_entity(db, data)
       logger.info(f"[ENTITY][CREATE] actor_id={...} entity_id={entity.id}")
       return entity
   ```

5. **Create migration** (Alembic)
   ```bash
   alembic revision --autogenerate -m "Add MyEntity table"
   alembic upgrade head
   ```

---

### **Debugging Checklist**

- ✅ **Token expired?** → Check `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`
- ✅ **DB query slow?** → Add indexes, use `.offset().limit()`
- ✅ **Missing activity log?** → Ensure `activity_crud.create_activity_log()` is called
- ✅ **CORS issues?** → Check `allow_origins` in `main.py`
- ✅ **Password hashing?** → Always use `hash_password()` from `core.security`
- ✅ **Migration failed?** → Check `alembic/versions/` for conflicts
- ✅ **PostgreSQL connection error?** → Check `.env` DATABASE_URL and firewall rules
- ✅ **Boolean column errors?** → Ensure defaults use `false` not `0` (PostgreSQL-specific)
- ✅ **Enum type errors?** → Let SQLAlchemy manage enums, don't create manually

---

This cheat sheet covers everything you need to work efficiently in this FastAPI + SQLAlchemy + PostgreSQL + JWT project! 🚀
