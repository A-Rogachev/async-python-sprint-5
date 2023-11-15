import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import authorization, db_services, file_storage
from core.config import app_settings

app: FastAPI = FastAPI(
    title=app_settings.APP_TITLE,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(authorization.users_router, prefix='/api/v1')
app.include_router(db_services.db_services_router, prefix='/api/v1')
app.include_router(file_storage.files_router, prefix='/api/v1/files')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )

# -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000 src.main:app
