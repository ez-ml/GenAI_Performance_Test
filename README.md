# GenAI Performance Testing Tool

## Description

`GenAI_Performance_Test` is a performance testing tool designed to evaluate the response times and throughput of FastAPI services under varying loads. It utilizes `asyncio` for concurrency, `httpx` for making HTTP requests, and `Plotly` for generating interactive charts. The results are saved in a comprehensive HTML report that includes various metrics, providing insights into how your FastAPI service performs under different levels of stress.

## Features

- **Automatic Ramp-Up Calculation**: Automatically determines the ramp-up step based on the provided start, max requests, and duration.
- **Interactive HTML Report**: Generates an HTML report with interactive charts, making it easy to analyze the performance of your FastAPI service.
- **Customizable Parameters**: Users can customize the URL, payload, and ramp-up configuration through command-line arguments.
- **High-Resolution Timing**: Uses high-resolution timing to measure response times in milliseconds.
- **Decorator for FastAPI Endpoints**: Leverages Python decorators to extend the project easily to any FastAPI endpoint, making it modular and reusable.

## Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd GenAI_Performance_Test
