from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time 
from collections import defaultdict
from typing import Dict


app = FastAPI()

class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records: Dict(str, float) = defaultdict(float)

    async def log_message(self, message: str):
        print(message)

    async def dispatch(self, request:Request, call_next):
        client_ip = request.client.host #get client ip address
        current_time = time.time() #get the time of the request

        if current_time - self.rate_limit_records[client_ip] < 1: #one request per second
            return Response(content="rate Limit exceeded", status_code=429)

        self.rate_limit_records[client_ip] = current_time #add to records if test pass.
        path = request.url.path
        await self.log_message(f"Request to {path}")

        # process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # add custom headers
        custom_headers = {"X-Process_time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)

        # async logging for processing times
        await self.log_message(f"Response for {path} took {process_time} seconds")

        return response



# adding the middleware to the app
app.add_middleware(AdvancedMiddleware)

@app.get("/")
async def main():
    return {"message": "grr, pow!"}


