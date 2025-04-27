import json
import time
import requests
import os
from datetime import datetime
from tabulate import tabulate
from openai import OpenAI



SYS_PROMPT = "You will be used to support crisis helpline volunteers \
  in finding information about mental health, mental health care providers, facilities, and resources. \
  When responding to queries, prioritize presenting the following information in a clear and structured format:\
  Include the following information in your response: \
  Name, Address, Phone number, Website, Accepting new patients, Languages spoken, Insurance accepted, Cost, Specialties\
  You will not provide any information until you are asked to do so by the volunteer.\
  You will not provide any diagnosis or treatment advice. "
# Test prompts
TEST_PROMPTS = ["therapists in Raleigh, NC who accept Cigna"]
api_key = "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"
client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

# Parameter combinations to test
PARAMETER_COMBINATIONS = [
    {"temperature": 0.1, "max_tokens": 500, "top_p": 0.1},
     {"temperature": 0.1, "max_tokens": 500, "top_p": .5},
    {"temperature": 0.1, "max_tokens": 500, "top_p": 1.0},
    {"temperature": 0.1, "max_tokens": 1000, "top_p": 0.1},
    {"temperature": 0.1, "max_tokens": 1000, "top_p": .5},
    {"temperature": 0.1, "max_tokens": 1000, "top_p": 1.0},
    {"temperature": 0.1, "max_tokens": 2000, "top_p": 0.1},
    {"temperature": 0.1, "max_tokens": 2000, "top_p": .5},
    {"temperature": 0.1, "max_tokens": 2000, "top_p": 1.0},
    {"temperature": 0.5, "max_tokens": 500, "top_p": 0.1},
    {"temperature": 0.5, "max_tokens": 500, "top_p": .5},
    {"temperature": 0.5, "max_tokens": 500, "top_p": 1.0},
    {"temperature": 0.5, "max_tokens": 1000, "top_p": 0.1},
    {"temperature": 0.5, "max_tokens": 1000, "top_p": .5},
    {"temperature": 0.5, "max_tokens": 1000, "top_p": 1.0},
    {"temperature": 0.5, "max_tokens": 2000, "top_p": 0.1},
    {"temperature": 0.5, "max_tokens": 2000, "top_p": .5},
    {"temperature": 0.5, "max_tokens": 2000, "top_p": 1.0},
    {"temperature": 0.9, "max_tokens": 500, "top_p": 0.1},
    {"temperature": 0.9, "max_tokens": 500, "top_p": .5},
    {"temperature": 0.9, "max_tokens": 500, "top_p": 1.0},
    {"temperature": 0.9, "max_tokens": 1000, "top_p": 0.1},
    {"temperature": 0.9, "max_tokens": 1000, "top_p": .5},
    {"temperature": 0.9, "max_tokens": 1000, "top_p": 1.0},
    {"temperature": 0.9, "max_tokens": 2000, "top_p": 0.1},
    {"temperature": 0.9, "max_tokens": 2000, "top_p": .5},
    {"temperature": 0.9, "max_tokens": 2000, "top_p": 1.0}

]

def run_test(prompt, params):
    """Run a single test with the given prompt and parameters"""
    start_time = time.time()
    
    # Create messages for the prompt
    messages = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    # Prepare the request payload
    payload = {
        "user_input": prompt,
        "messages": messages,
        "parameters": {
            "temperature": params["temperature"],
            "max_tokens": params["max_tokens"],
            "top_p": params["top_p"]
        }
    }
    
    # Make the API request
    try:
        response_text = get_advice(messages, params)
        end_time = time.time()
        duration = end_time - start_time
        
        # Check if the response is an error message
        if response_text.startswith("Error:"):
            return {
                "success": False,
                "duration": duration,
                "error": response_text,
                "response": response_text
            }
        
        return {
            "success": True,
            "duration": duration,
            "response_length": len(response_text),
            "response": response_text
        }
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        return {
            "success": False,
            "duration": duration,
            "error": str(e),
            "response": "Error occurred"
        }

def run_all_tests():
    """Run all tests with all parameter combinations"""
    results = []
    
    for prompt in TEST_PROMPTS:
        for params in PARAMETER_COMBINATIONS:
            print(f"Testing prompt: '{prompt}' with params: {params}")
            result = run_test(prompt, params)
            
            results.append({
                "prompt": prompt,
                "temperature": params["temperature"],
                "max_tokens": params["max_tokens"],
                "top_p": params["top_p"],
                "success": result["success"],
                "duration": f"{result['duration']:.2f}s",
                "response_length": result.get("response_length", 0),
                "response": result["response"]
            })
    
    return results

def display_results(results):
    """Display results in a tabular format with enhanced visualization"""
    # Prepare data for tabulate
    table_data = []
    for result in results:
        # Truncate response for display
        response_preview = result["response"]
        if len(response_preview) > 100:
            response_preview = response_preview[:100] + "..."
        
        table_data.append([
            result["prompt"][:30] + "..." if len(result["prompt"]) > 30 else result["prompt"],
            result["temperature"],
            result["max_tokens"],
            result["top_p"],
            "✅" if result["success"] else "❌",
            result["duration"],
            result["response_length"],
            response_preview
        ])
    
    # Define headers
    headers = ["Prompt", "Temp", "Max Tokens", "Top P", "Success", "Duration", "Length", "Response Preview"]
    
    # Print the table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Print summary statistics
    success_count = sum(1 for r in results if r["success"])
    avg_duration = sum(float(r["duration"].replace("s", "")) for r in results) / len(results)
    
    print("\nSummary Statistics:")
    print(f"Total tests: {len(results)}")
    print(f"Successful tests: {success_count} ({success_count/len(results)*100:.1f}%)")
    print(f"Average duration: {avg_duration:.2f}s")
    
    # Generate HTML report
    generate_html_report(results)

def generate_html_report(results):
    """Generate a simple HTML report with detailed results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"parameter_test_report_{timestamp}.html"
    
    # Calculate statistics
    success_count = sum(1 for r in results if r["success"])
    success_rate = success_count / len(results) * 100
    avg_duration = sum(float(r["duration"].replace("s", "")) for r in results) / len(results)
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Parameter Test Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .summary {{ background-color: #e6f7ff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .response {{ max-height: 200px; overflow-y: auto; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>Parameter Test Results</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p>Total tests: {len(results)}</p>
            <p>Successful tests: {success_count} ({success_rate:.1f}%)</p>
            <p>Average duration: {avg_duration:.2f}s</p>
            <p>Test date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <h2>Test Results</h2>
        <table>
            <tr>
                <th>Prompt</th>
                <th>Temperature</th>
                <th>Max Tokens</th>
                <th>Top P</th>
                <th>Success</th>
                <th>Duration</th>
                <th>Length</th>
                <th>Response</th>
            </tr>
    """
    
    # Add all results to a single table
    for result in results:
        success_class = "success" if result["success"] else "failure"
        success_symbol = "✅" if result["success"] else "❌"
        
        html_content += f"""
        <tr>
            <td>{result["prompt"]}</td>
            <td>{result["temperature"]}</td>
            <td>{result["max_tokens"]}</td>
            <td>{result["top_p"]}</td>
            <td class="{success_class}">{success_symbol}</td>
            <td>{result["duration"]}</td>
            <td>{result["response_length"]}</td>
            <td class="response">{result["response"]}</td>
        </tr>
        """
    
    html_content += """
        </table>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(report_path, "w") as f:
        f.write(html_content)
    
    print(f"\nHTML report generated: {report_path}")

def get_advice(messages, params):
    try:
        print("messages before call is", messages)
        response = client.chat.completions.create(
            model="sonar-pro",                    # The model to use for completion
            temperature=params["temperature"],    # Controls randomness (0-2). Lower values are more focused
            max_tokens=params["max_tokens"],     # Maximum number of tokens to generate
            top_p=params["top_p"],               # Controls diversity via nucleus sampling (0-1)
            messages=messages                     # Add the messages parameter
        )
        
        #print("response from create is ", response.model_dump_json())
        # Handle the tool call response
        message = response.choices[0].message
        
        # If no tool calls or different tool, return the regular content
        return message.content
        
    except Exception as e:
        print(f"Error in get_advice: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Running parameter tests for emergency contacts...")
    results = run_all_tests()
    display_results(results) 