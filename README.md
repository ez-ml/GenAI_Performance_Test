# GenAI Performance Testing Tool

## Description

`GenAI_Performance_Test` is a performance testing tool designed to evaluate the response times and throughput of FastAPI services under varying loads. It utilizes `asyncio` for concurrency, `httpx` for making HTTP requests, and `Plotly` for generating interactive charts. The results are saved in a comprehensive HTML report that includes various metrics, providing insights into how your FastAPI service performs under different levels of stress.

## Features

- **Automatic Ramp-Up Calculation**: Automatically determines the ramp-up step based on the provided start, max requests, and duration.
- **Interactive HTML Report**: Generates an HTML report with interactive charts, making it easy to analyze the performance of your FastAPI service.
- **Customizable Parameters**: Users can customize the URL, payload, and ramp-up configuration through command-line arguments.
- **High-Resolution Timing**: Uses high-resolution timing to measure response times in milliseconds.
- **Decorator for FastAPI Endpoints**: Leverages Python decorators to extend the project easily to any FastAPI endpoint, making it modular and reusable.

## Getting Started

### 1. Clone the Repository
```bash
git clone <repository_url>
cd GenAI_Performance_Test
```
### 2. Install pipenv dependencies:
```bash
pipenv install
```
### 3. Activate the Virtual Environment:
```bash
pipenv shell
```
### 4. Running the Project:
```bash
pipenv run python main.py --url "http://localhost:8000/calculate-power" \
                          --payload '{"number": 100, "power": 3}' \
                          --start-requests 10 \
                          --max-requests 50 \
                          --duration 30
Note :- Please replace the --url with your FASTApi endpoint and --payload with appripriate payload for your API.
```
### 4. View the Report:
```bash
Open the generated HTML file in your web browser to view the interactive performance report.
```

## Charts Included in the Report
- **Average Response Time vs. Number of Concurrent Users**: Shows how the average response time changes as the number of concurrent users increases..
- **Maximum Response Time vs. Number of Concurrent Users**: Provides the maximum response time observed during the test, helping to identify any significant outliers.
- **95th Percentile Response Time vs. Number of Concurrent Users**: Displays the 95th percentile response time, highlighting the upper limit of response times that most users experience.
- **Response Time Distribution**: A histogram showing the distribution of response times for different levels of concurrency.
- **Throughput vs. Number of Concurrent Users**:Illustrates how the throughput (requests per second) varies with the number of concurrent users.

## Utilizing Decorators for FastAPI Endpoints
Please try to leverage decorator pattern with FastAPI endpoint . This approach allows you to enhance or modify the behavior of your FastAPI routes in a clean, modular, and reusable way.
- **Why Use Decorators**: Decorators in Python provide a convenient way to wrap a function and modify its behavior without changing the function itself. When applied to FastAPI endpoints, decorators can be used to add additional functionality—such as logging, timing, authentication checks, or performance monitoring—across multiple routes with minimal code duplication.
- **How to Implement a Decorator in FastAPI**: To illustrate this, let's walk through an example where we create a timing decorator that measures the execution time of a FastAPI endpoint and returns the response along with the processing time.
```bash
Create a decorator that calculates the time taken for the request to be processed by the endpoint:

rom fastapi import FastAPI, Request
import time

app = FastAPI()

def timing_decorator(func):
    async def wrapper(request: Request):
        # Start the timer
        start_time = time.perf_counter_ns()
        # Execute the original function
        response = await func(request)
        # Stop the timer
        end_time = time.perf_counter_ns()
        # Calculate processing time in milliseconds
        process_time_ms = (end_time - start_time) / 1_000_000
        # Return the original response along with the processing time
        return {"result": response, "process_time_ms": process_time_ms}
    return wrapper

In this decorator:

Start Timer: We start the timer just before the endpoint's function is executed.
Execute Function: The original function (endpoint) is called using await func(request).
Stop Timer: After the function completes, we stop the timer and calculate the time difference.
Return Enhanced Response: The original response is returned, along with the processing time in milliseconds.

Apply the Decorator to Your FastAPI Endpoints
@app.post("/calculate-power")
@timing_decorator
async def calculate_power(request: Request):
    data = await request.json()
    number = data['number']
    power = data['power']
    result = number ** power
    return result

```