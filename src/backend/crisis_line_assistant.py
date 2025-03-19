from typing import List

from flask import Flask, request, jsonify
from openai import OpenAI
import configparser
from flask_cors import CORS
import boto3
import json
import os
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_config(key: str):
    """Get configuration from AWS Parameter Store or local file based on environment"""
    # Check environment variable to determine running mode
    env = os.environ.get('APP_ENV', 'local').lower()  # Default to local if not set
    
    try:
        if env == 'test':
            # Read from AWS Parameter Store for test environment
            ssm = boto3.client('ssm', region_name='us-east-1')
            response = ssm.get_parameter(
                Name='/myapp/config/test/zen-properties'
            )
            # Parse the JSON response
            config_json = json.loads(response['Parameter']['Value'])
            # Access the nested 'crisis_line_assistant' dictionary
            return config_json['crisis_line_assistant'][key]
        
        elif env == 'production':
            # Read from AWS Parameter Store for production environment
            ssm = boto3.client('ssm', region_name='us-east-1')
            response = ssm.get_parameter(
                Name='/myapp/config/production/zen-properties'
            )
            # Parse the JSON response
            config_json = json.loads(response['Parameter']['Value'])
            # Access the nested 'crisis_line_assistant' dictionary
            return config_json['crisis_line_assistant'][key]
        
        else:
            # Read from local properties file
            configuration = configparser.ConfigParser()
            configuration.read('../../config/zen.properties')
            section = 'crisis_line_assistant.local'
            return configuration[section][key]
            
    except Exception as e:
        print(f"Error getting parameter {key}: {e}")
        raise e

@app.route('/config', methods=['GET'])
def get_config():
    """Route handler that wraps the fetch_config function"""
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "Missing key parameter"}), 400
    
    try:
        value = fetch_config(key)
        return value
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize with safer defaults
try:
    api_key = fetch_config('api_key')
    system_prompt = fetch_config('system_prompt')
    default_ai_prompt = fetch_config('default_ai_prompt')
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
except Exception as e:
    print(f"Error initializing configuration: {e}")
   
client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")


def get_advice(messages):

    print("message calling create is ", messages)
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    #print("response from create is ", response.model_dump_json())
    content= response.choices[0].message.content
    #print("content is ", content)
    return content



@app.route('/chat', methods=['POST'])
def chat():
    #print("request is ", request)
    data = request.json
    #print("data is", data)
    user_input = data.get('user_input', '')
    #print("user_input is", user_input)

    messages = data.get('messages')

    if user_input.lower() == "exit":
        return jsonify({"response": "Ending the conversation. Take care!"})
    else:
        messages.append({"role": "user", "content": user_input})

    #rint("messages before get_advice is ", messages)
    ai_response = get_advice(messages)

    messages.append({"role": "assistant", "content": ai_response})

    return jsonify({"response": ai_response, "messages": messages})

@app.route('/')
def index():
    return "Hello World"  # or your actual homepage response


if __name__ == '__main__':
    app.run(debug=True, port=5001)