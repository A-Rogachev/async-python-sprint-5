import time

import psycopg2
import redis
from fastapi import APIRouter, Depends

from api.v1.authorization import oauth2_scheme, token_required
from core.config import app_settings
from db.redis_cache import get_redis_client
from schemas.db_services import DbServicesPing

files_router: APIRouter = APIRouter()