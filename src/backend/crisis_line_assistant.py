from typing import List

from flask import Flask, request, jsonify
from openai import OpenAI
import configparser
from flask_cors import CORS
import boto3
import json
import os
import traceback
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_config(key: str):
    #print("fetching config for key ", key)
    """Get configuration from AWS Parameter Store or local file based on environment"""
    # Check environment variable to determine running mode
    env = os.environ.get('APP_ENV', 'local').lower()  # Default to local if not set
    #print("env is ", env)

    try:
        if env == 'test':
            # Set parameter store name for test environment
            parameter_name = '/myapp/config/test/zen-properties'
        elif env == 'production':
            # Set parameter store name for production environment
            parameter_name = '/myapp/config/production/zen-properties'
        
        if env in ['test', 'production']:
            #print(f"Attempting to fetch from AWS Parameter Store: {parameter_name}")
            # Read from AWS Parameter Store
            ssm = boto3.client('ssm', region_name='us-east-1')
            response = ssm.get_parameter(
                Name=parameter_name
            )
            #print("Got response from Parameter Store")
            # Parse the JSON response
            config_json = json.loads(response['Parameter']['Value'])
            #print("Parsed JSON response")
            value = config_json['crisis_line_assistant'][key]
            value = value.replace('\\\n', '').replace('\\', '')
            #print("value from config_json is ", value)
            return value
        elif env == 'local' or env == None:
            #print("Reading from local properties file")
            # Read from local properties file
            configuration = configparser.ConfigParser()
            configuration.read('../../config/zen.properties')
            section = 'crisis_line_assistant.local'
            value = configuration[section][key]
            #print("value before cleaning is ", value)
            # Clean up the value by removing backslashes and joining lines
            value = value.replace('\\\n', '').replace('\\', '')
            #print("value after cleaning is ", value)
            return value
        else:
            raise ValueError(f"Invalid environment: {env}")
            
    except Exception as e:
        print(f"Error getting parameter {key}: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise e

@app.route('/config', methods=['GET'])
def get_config():
    """Route handler that wraps the fetch_config function"""
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "Missing key parameter"}), 400
    
    try:
        value = fetch_config(key)
        return jsonify({"value": value})  # Wrap the value in a JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize with safer defaults
try:
    print("Starting configuration initialization...")
    # Get API key from configuration
    api_key = fetch_config('api_key').strip()
    #print("api_key is ", api_key)
    # Initialize OpenAI client with Perplexity base URL
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    #print("client is ", client)
except Exception as e:
    print(f"Error initializing configuration: {str(e)}")
    print(f"Error type: {type(e)}")
    import traceback
    print(f"Full traceback: {traceback.format_exc()}")
   

def get_advice(messages):
    #print("client before call is", client.api_key , "and model is ")
    response = client.chat.completions.create(
        model="sonar-pro",                    # The model to use for completion
        temperature=0.3,                      # Controls randomness (0-2). Lower values are more focused
        max_tokens=1000,                      # Maximum number of tokens to generate
        top_p=0.3,                             # Controls diversity via nucleus sampling (0-1)
        messages=messages                    # The conversation history
     )
    
    # Handle the tool call response
    message = response.choices[0].message
    
    # If no tool calls or different tool, return the regular content
    return message.content

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    #print("data is", data)
    user_input = data.get('user_input', '')
    #print("user_input is", user_input)

    messages = data.get('messages')

    if user_input.lower() == "exit":
        return jsonify({"response": "Ending the conversation. Take care!"})
    else:
        messages.append({"role": "user", "content": user_input})

    print("CONVERSATION:: User Input is ", user_input)
    ai_response = get_advice(messages)
    print("CONVERSATION:: ai_response is ", ai_response)
    messages.append({"role": "assistant", "content": ai_response})

    return jsonify({"response": ai_response, "messages": messages})

@app.route('/')
def index():
    return "Hello World"  # or your actual homepage response


if __name__ == '__main__':
    app.run(debug=True, port=5001)