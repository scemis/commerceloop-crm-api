from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from core.logger import logger as _logger

# auth dependency
from api.auth.deps import get_current_user

# Routers
from api.auth.routes import router as auth_router
from api.roles.routes import router as roles_router
from api.users.routes import router as users_router
from api.companies.routes import router as companies_router
from api.connect_companies.routes import router as connect_companies_router
from api.categories.routes import router as categories_router
from api.products.routes import router as products_router
from api.activity_logs.routes import router as activity_logs_router

app = FastAPI(
    swagger_ui_parameters={
        "persistAuthorization": True,
        "syntaxHighlight": {"theme": "obsidian"}
    },
    title="Commerce Loop CRM API",
    version="1.0.0",
    #root_path="/api/v1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Открытые маршруты
app.include_router(auth_router)

# Защищённые маршруты — токен будет подставляться из ключика в Swagger
app.include_router(users_router,             dependencies=[Depends(get_current_user)])
app.include_router(roles_router,             dependencies=[Depends(get_current_user)])
app.include_router(companies_router,         dependencies=[Depends(get_current_user)])
app.include_router(connect_companies_router, dependencies=[Depends(get_current_user)])
app.include_router(categories_router,        dependencies=[Depends(get_current_user)])
app.include_router(products_router,          dependencies=[Depends(get_current_user)])
app.include_router(activity_logs_router,     dependencies=[Depends(get_current_user)])

# test purpose
echo_router = APIRouter(
    prefix="/api",
    tags=["Testing & Healthcheck"]
)

@echo_router.get("/echo")
def echo_test():
    """
    A simple GET endpoint that returns a test message.
    This can be used for health checks or basic connectivity tests.
    """
    return {"message": "Echo test successful", "status": "ok"}

app.include_router(echo_router)