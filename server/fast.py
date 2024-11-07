
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import aiohttp
import time
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from functools import wraps
import pickle
import sys
from fastapi.logger import logger
import logging
from logging.handlers import RotatingFileHandler

class DiscordAuth(BaseModel):
    code: str

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('[%(levelname)s] - %(asctime)s - %(name)s - %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Create a global logger
global_logger = setup_logger('global_logger', 'log.txt')
#
logger.handlers = global_logger.handlers
logger.setLevel(logging.INFO)

logger.info('API is starting up')
app = FastAPI()

REQUEST_TIMEOUT_ERROR = 50  # Threshold (in seconds)

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        logger.info(f"trying to post {request.base_url}{request.url.path}")
        start_time = time.time()
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT_ERROR)
    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        logger.error(f"timeout! {request.base_url}{request.url.path}", process_time, request.base_url)
        return JSONResponse(
            {'detail': 'Request processing time exceeded limit', 'processing_time': process_time},
            status_code=HTTP_504_GATEWAY_TIMEOUT
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def log_duration(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Record the start time
        start_time = time.time()

        # Extract the JSON data from the request body
        try:
            json_data = request.json()
        except Exception as e:
            json_data = {}
            logger.error(f"Failed to parse JSON data: {e}")

        # Execute the original function
        response = await func(request, *args, **kwargs)

        # Calculate the duration
        duration = (time.time() - start_time) * 1000
        logger.info(
            f"[{func.__name__}][{duration:.2f}ms] data={json_data} response={response}")

        return response

    return wrapper

@app.post("/discord_auth")
@log_duration
async def discord_auth(request: DiscordAuth):
    # 从环境变量中获取信息
    client_id = "1283000047155544066"
    client_secret = "Z_B1P2SKX9kGh11hLNmnd_5eyoMz9b1D"

    # 从请求体中获取 code
    code = request.code

    # 构建请求数据
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code
    }

    # 发送 POST 请求
    async with aiohttp.ClientSession() as session:
        async with session.post('https://discord.com/api/oauth2/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}) as response:
            if response.status == 200:
                json_response = await response.json()
                access_token = json_response.get('access_token')
                return {"success": True, "access_token": access_token}
            else:
                logger.error("discord auth failed")
                return {"success": False, "status": str(response.status)}




