import logging
import time
from logging import handlers

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from constants import API_PORT, API_RELOAD, LOG_LEVEL, WEB_UI_PATH
from rest_api.admin_api import admin_api
from rest_api.security_api import security_api
from rest_api.user_api import users_api

LOG_FILENAME = f'data/logs/API.log'

USERS_PREFIX = '/users'
SECURITY_PREFIX = '/security'
ADMIN_PREFIX = '/admin'

handler = handlers.TimedRotatingFileHandler(filename=LOG_FILENAME, when='midnight', backupCount=60)
logging.basicConfig(format='[%(asctime)s] - %(levelname)s %(message)s', level=LOG_LEVEL, handlers=[handler])

tags_metadata = [
    {
        "name": "Security",
        "description": "Operations about authentication and authorization"
    },
    {
        "name": "Admin",
        "description": "Admin functionalities"
    },
    {
        "name": "Users",
        "description": "Operations with users"
    }
]

app = FastAPI(title="AInterviewer",
              description="API documentation for backend services in AInterviewer",
              version="1.0.0",
              openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEB_UI_PATH],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def not_log_methods(request: Request):
    methods = [
        (USERS_PREFIX, 'POST'),
        (USERS_PREFIX, 'PATCH'),
        (f'{SECURITY_PREFIX}/login', 'POST'),
        (f'{SECURITY_PREFIX}/change_password', 'PATCH')
    ]
    for m in methods:
        if m[0] in request.url.path and m[1] == request.method:
            return True
    return False


async def log_json(request: Request):
    if not not_log_methods(request) and await request.body():
        logging.info(
            f'method={request.method}, url={request.url.path}, query_params={request.query_params}, '
            f'path_params={request.path_params}, request.json={await request.json()}')
    else:
        logging.info(
            f'method={request.method}, url={request.url.path}, query_params={request.query_params}, '
            f'path_params={request.path_params}')


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)

    logging.info(
        f'method={request.method}, path={request.url.path}, completed_in={formatted_process_time}ms, '
        f'status_code={response.status_code}')

    return response


app.include_router(security_api, prefix=SECURITY_PREFIX, dependencies=[Depends(log_json)])
app.include_router(admin_api, prefix=ADMIN_PREFIX, dependencies=[Depends(log_json)])
app.include_router(users_api, prefix=USERS_PREFIX, dependencies=[Depends(log_json)])

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=API_PORT, reload=API_RELOAD)
