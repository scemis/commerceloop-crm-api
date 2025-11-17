from enum import Enum

class StatusEnum(str, Enum):
    pending = 'pending'
    completed = 'completed'
    canceled = 'canceled'

class ActivityLogEnum(str, Enum):    
    login = 'login'
    create = 'create'
    edit = 'edit'
    delete = 'delete'
    email = 'email'

class EntityEnum(str, Enum):
    users = "users"
    personal_details = "personal_details"
    companis = "companis"
    connect_companis = "connect_companis"
    categories = "categories"
    sub_categories = "sub_categories"
    products = "products"