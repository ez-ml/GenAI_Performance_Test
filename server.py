from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
import logging
import uvicorn
from functools import wraps

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Decorator for logging response time
def log_response_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        response = await func(*args, **kwargs)
        process_time = time.time() - start_time
        logging.info(f"Response time: {process_time} seconds")
        return {'process_time':process_time}
    return wrapper

# Pydantic model for power request payload
class PowerRequest(BaseModel):
    number: float
    power: int

# Pydantic model for square request payload
class SquareRequest(BaseModel):
    number: float

# Endpoint to calculate power of a given number
@app.post("/calculate-power")
@log_response_time
async def calculate_power(payload: PowerRequest):
    result = payload.number ** payload.power
    return {"result": result}

# Endpoint to calculate square of a given number
@app.post("/calculate-square")
@log_response_time
async def calculate_square(payload: SquareRequest):
    result = payload.number ** 2
    return {"result": result}

# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

