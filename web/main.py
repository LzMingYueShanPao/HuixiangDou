import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import web.api.access as access
import web.api.qalib as qalib
import web.api.statistic as statistic
from web.api import chat, message
from web.config.logging import LOGGING_CONFIG
from web.middleware.token import check_hxd_token
from web.scheduler.huixiangdou_task import start_scheduler, stop_scheduler
from web.util.log import log

# log
logger = log(__name__)

# define global variable
API_VER = 'v1'

# FastAPI setting
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=access.access_api, prefix=f"/api/{API_VER}/access")
app.include_router(router=qalib.qalib_api, prefix=f"/api/{API_VER}/qalib", dependencies=[Depends(check_hxd_token)])
app.include_router(router=statistic.statistic_api, prefix=f"/api/{API_VER}/statistic")
app.include_router(router=chat.chat_api, prefix=f"/api/{API_VER}/chat", dependencies=[Depends(check_hxd_token)])
app.include_router(router=message.message_api, prefix=f"/api/{API_VER}/message")


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.exception_handler(HTTPException)
async def global_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


def main():
    """
    main function
    start server use uvicorn
    default workers: 3
    default port: 23333
    """
    uvicorn.run(
        "web.main:app",
        host='0.0.0.0',
        port=23333,
        timeout_keep_alive=600,
        workers=3,
        log_config=LOGGING_CONFIG
    )


if __name__ == "__main__":
    main()
