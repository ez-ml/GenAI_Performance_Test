import argparse
import asyncio
import httpx
import statistics
from time import perf_counter_ns
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
import json
import math


def calculate_ramp_up_step(start_requests, max_requests, duration):
    """Calculate the ramp-up step based on the start requests, max requests, and total duration."""
    total_steps = duration // 5  # Assuming 5 seconds per step
    ramp_up_step = math.ceil((max_requests - start_requests) / total_steps)
    return ramp_up_step


async def send_request(client, url, payload):
    """Send a single request and measure the processing time in milliseconds."""
    start_time = perf_counter_ns()
    response = await client.post(url, json=payload)
    end_time = perf_counter_ns()
    process_time_ms = (end_time - start_time) / 1_000_000  # Convert nanoseconds to milliseconds
    return process_time_ms


async def ramp_up_requests(url, payload, num_requests, duration):
    """Send concurrent requests for a specified duration and collect response times."""
    async with httpx.AsyncClient() as client:
        start_time = perf_counter_ns()
        process_times = []
        while (perf_counter_ns() - start_time) / 1_000_000_000 < duration:
            tasks = [send_request(client, url, payload) for _ in range(num_requests)]
            response_times = await asyncio.gather(*tasks)
            process_times.extend(response_times)
        return process_times


async def main():
    """Main function to parse arguments, run the test, and generate the report."""
    parser = argparse.ArgumentParser(description="Performance testing tool for FastAPI services.")

    parser.add_argument('--url', type=str, required=True, help="The URL of the FastAPI endpoint.")
    parser.add_argument('--payload', type=str, required=True,
                        help="The JSON payload to send with each request. Pass as a string.")
    parser.add_argument('--start-requests', type=int, required=True, help="Initial number of concurrent requests.")
    parser.add_argument('--max-requests', type=int, required=True, help="Maximum number of concurrent requests.")
    parser.add_argument('--duration', type=int, required=True, help="Total duration of the test in seconds.")
    parser.add_argument('--output-file', type=str, help="The name of the output HTML file.")

    args = parser.parse_args()

    url = args.url
    payload = json.loads(args.payload)  # Convert the JSON string to a dictionary
    start_requests = args.start_requests
    max_requests = args.max_requests
    duration = args.duration

    # Calculate ramp-up step based on provided arguments
    ramp_up_step = calculate_ramp_up_step(start_requests, max_requests, duration)
    duration_per_step = 5  # Fixed duration per step in seconds

    # Generate default output filename if not provided
    if args.output_file:
        output_file = args.output_file
    else:
        output_file = f"Load_Test_{start_requests}_{max_requests}_{duration}sec.html"

    # HTML title and heading derived from the output file name
    html_title = output_file.replace(".html", "")

    # Data structures to store results
    average_response_times = []
    concurrent_users = []
    all_process_times = []

    for num_requests in range(start_requests, max_requests + 1, ramp_up_step):
        print(f"Running with {num_requests} concurrent requests...")
        process_times = await ramp_up_requests(url, payload, num_requests, duration_per_step)

        if process_times:
            avg_response_time = statistics.mean(process_times)
            average_response_times.append(avg_response_time)
            concurrent_users.append(num_requests)
            all_process_times.append(process_times)
            print(f"Average response time with {num_requests} users: {avg_response_time:.2f} ms")

        # Ramp-up interval (sleep 1 second between steps)
        await asyncio.sleep(1)

    # Generate the interactive Plotly report
    save_plots_to_html(concurrent_users, average_response_times, all_process_times, duration_per_step, output_file,
                       html_title)


def save_plots_to_html(concurrent_users, average_response_times, all_process_times, duration_per_step, output_file,
                       html_title):
    """Generates and saves interactive performance plots as an HTML file."""

    # Plot: Average Response Time vs Number of Concurrent Users
    fig_avg_response = go.Figure()
    fig_avg_response.add_trace(
        go.Scatter(x=concurrent_users, y=average_response_times, mode='lines+markers', name='Avg Response Time'))
    fig_avg_response.update_layout(title='Average Response Time vs Number of Concurrent Users',
                                   xaxis_title='Number of Concurrent Users',
                                   yaxis_title='Average Response Time (ms)')

    # Plot: 95th Percentile Response Time vs Number of Concurrent Users
    percentiles = [np.percentile(times, 95) for times in all_process_times]
    fig_95th_percentile = go.Figure()
    fig_95th_percentile.add_trace(
        go.Scatter(x=concurrent_users, y=percentiles, mode='lines+markers', name='95th Percentile Response Time',
                   line=dict(color='orange')))
    fig_95th_percentile.update_layout(title='95th Percentile Response Time vs Number of Concurrent Users',
                                      xaxis_title='Number of Concurrent Users',
                                      yaxis_title='95th Percentile Response Time (ms)')

    # Plot: Maximum Response Time vs Number of Concurrent Users
    max_times = [max(times) for times in all_process_times]
    fig_max_response = go.Figure()
    fig_max_response.add_trace(
        go.Scatter(x=concurrent_users, y=max_times, mode='lines+markers', name='Max Response Time',
                   line=dict(color='red')))
    fig_max_response.update_layout(title='Maximum Response Time vs Number of Concurrent Users',
                                   xaxis_title='Number of Concurrent Users',
                                   yaxis_title='Maximum Response Time (ms)')

    # Plot: Response Time Distribution
    fig_distribution = go.Figure()
    for users, times in zip(concurrent_users, all_process_times):
        fig_distribution.add_trace(go.Histogram(x=times, name=f'{users} Users', opacity=0.75))
    fig_distribution.update_layout(title='Response Time Distribution for Different Concurrent Users',
                                   xaxis_title='Response Time (ms)',
                                   yaxis_title='Frequency',
                                   barmode='overlay')
    fig_distribution.update_traces(opacity=0.5)

    # Plot: Throughput vs Number of Concurrent Users
    throughputs = [len(times) / duration_per_step for times in all_process_times]
    fig_throughput = go.Figure()
    fig_throughput.add_trace(go.Scatter(x=concurrent_users, y=throughputs, mode='lines+markers', name='Throughput',
                                        line=dict(color='green')))
    fig_throughput.update_layout(title='Throughput vs Number of Concurrent Users',
                                 xaxis_title='Number of Concurrent Users',
                                 yaxis_title='Throughput (Requests per Second)')

    # Combine plots into a table format
    plots = [
        pio.to_html(fig_avg_response, full_html=False),
        pio.to_html(fig_95th_percentile, full_html=False),
        pio.to_html(fig_max_response, full_html=False),
        pio.to_html(fig_distribution, full_html=False),
        pio.to_html(fig_throughput, full_html=False)
    ]

    # Create the HTML structure with a table
    html_content = f"""
    <html>
    <head>
        <title>{html_title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
                border-radius: 10px 10px 0 0;
                overflow: hidden;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: center;
            }}
            th {{
                background-color: #009879;
                color: #ffffff;
                text-transform: uppercase;
                font-weight: 600;
            }}
            tr {{
                border-bottom: 1px solid #dddddd;
            }}
            tr:nth-of-type(even) {{
                background-color: #f3f3f3;
            }}
            tr:last-of-type {{
                border-bottom: 2px solid #009879;
            }}
            .plot-container {{
                padding: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>{html_title}</h1>
        <table>
            <tr>
                <td class="plot-container">{plots[0]}</td>
                <td class="plot-container">{plots[1]}</td>
            </tr>
            <tr>
                <td class="plot-container">{plots[2]}</td>
                <td class="plot-container">{plots[3]}</td>
            </tr>
            <tr>
                <td class="plot-container" colspan="2">{plots[4]}</td>
            </tr>
        </table>
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"Interactive performance report saved to '{output_file}'.")


if __name__ == "__main__":
    asyncio.run(main())

