import uvicorn
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
@limiter.limit("60/minute")
async def rate_limit_endpoint(request: Request):
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("mock_server:app", host="0.0.0.0", limit_concurrency=2, port=3000, workers=1)
