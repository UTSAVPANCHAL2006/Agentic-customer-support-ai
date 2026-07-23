import redis
import json
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.config import REDIS_URL

# how many requests allowed per window
MAX_REQUESTS = 20

# time window in seconds
TIME_WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        # connect to redis
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    async def dispatch(self, request: Request, call_next):

        # only apply rate limit to /chat endpoint
        if request.url.path != "/chat":
            return await call_next(request)

        # read the request body to get thread_id
        # (IP-based limiting fails in Docker — all requests come from same container IP)
        try:
            body = await request.body()
            body_json = json.loads(body)
            thread_id = body_json.get("thread_id", None)
        except Exception:
            thread_id = None

        # fallback to IP if thread_id not found
        if thread_id:
            key = f"ratelimit:thread:{thread_id}"
        else:
            client_ip = request.client.host
            key = f"ratelimit:ip:{client_ip}"

        # increment the counter for this session
        count = self.redis_client.incr(key)

        # if this is the first request, set expiry
        if count == 1:
            self.redis_client.expire(key, TIME_WINDOW)

        # if user exceeded the limit, block them
        if count > MAX_REQUESTS:
            seconds_left = self.redis_client.ttl(key)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests! Please slow down.",
                    "retry_after_seconds": seconds_left
                }
            )

        # rebuild request with body so downstream can still read it
        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive

        # everything is fine, pass the request through
        return await call_next(request)
