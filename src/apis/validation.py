import datetime
from functools import wraps
from flask import Response, request

from src.common.ConfigProvider import ConfigProvider
from src.common.config import MINIPILOT_RATE_LIMITER_ENABLED, MINIPILOT_RATE_LIMITER_CRITERIA, MINIPILOT_RATE_LIMITER_ALLOW
from src.common.utils import get_db


def rate_limiter(req):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cfg = ConfigProvider()
            if cfg.is_rate_limiter():
                if MINIPILOT_RATE_LIMITER_CRITERIA == "session":
                    token_minute = f'minipilot:limiter:{request.headers.get("session-id")}:{str(datetime.datetime.now().minute)}'
                elif MINIPILOT_RATE_LIMITER_CRITERIA == "ip":
                    token_minute = f'minipilot:limiter:{request.remote_addr}:{str(datetime.datetime.now().minute)}'
                else:
                    token_minute = f'minipilot:limiter:{request.remote_addr}:{request.headers.get("session-id")}:{str(datetime.datetime.now().minute)}'
                ops = get_db().get(token_minute)
                if (ops is not None) and (int(ops) > MINIPILOT_RATE_LIMITER_ALLOW):
                    return Response(response="You have exceeded the rate limit", status=429)
                p = get_db().pipeline(transaction=True)
                p.incr(token_minute)
                p.expire(token_minute, 59)
                p.execute()
            return f(*args, **kwargs)
        return decorated_function
    return decorator
