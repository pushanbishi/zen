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
import logging
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to load .env file but don't fail if it doesn't exist
load_dotenv(override=True)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
env = os.environ.get('APP_ENV', 'local').lower()

def fetch_config(key: str):
    #print("fetching config for key ", key)
    """Get configuration from AWS Parameter Store or local file based on environment"""
    # Check environment variable to determine running mode
    #env = os.environ.get('APP_ENV', 'local').lower()  # Default to local if not set
    #print("env is ", env)

    try:
        if env == 'test':
            # Set parameter store name for test environment
            parameter_name = '/myapp/config/test/zen-properties'
        elif env == 'production':
            # Set parameter store name for production environment
            parameter_name = '/myapp/config/production/zen-properties'
        
        logger.info(f"Fetching configuration for key: {key} in environment: {env}")
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

# Initialize S3 client
s3 = boto3.client('s3')

def save_conversation_to_s3(conversation_id, messages):
    try:
        # Get bucket name from environment variable
        bucket_name = os.environ.get('CONVERSATION_BUCKET')
        logger.info(f"Saving conversation {conversation_id} to S3 bucket: {bucket_name}")
        if not bucket_name:
            logger.error("CONVERSATION_BUCKET environment variable not set")
            return

        # Prepare conversation data
        conversation_data = {
            'conversation_id': conversation_id,
            'timestamp': datetime.utcnow().isoformat(),
            'messages': messages
        }

        # Save to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=f'conversations/{conversation_id}.json',
            Body=json.dumps(conversation_data, indent=2),
            ContentType='application/json'
        )
        logger.info(f"Saved conversation {conversation_id} to S3")
    except Exception as e:
        logger.error(f"Error saving conversation to S3: {str(e)}")
        logger.error(traceback.format_exc())

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        messages = data.get('messages', [])
        parameters = data.get('parameters', {})
        
        logger.info(f"Received chat request with input: {user_input}")
        logger.debug(f"Messages: {messages}")
        logger.debug(f"Parameters: {parameters}")

        # Generate a unique conversation ID if this is the first message
        if not messages:
            conversation_id = str(uuid.uuid4())
        else:
            # Extract conversation ID from the first message
            conversation_id = messages[0].get('conversation_id', str(uuid.uuid4()))

        # Add conversation ID to messages if not present
        if not any('conversation_id' in msg for msg in messages):
            for msg in messages:
                msg['conversation_id'] = conversation_id

        if user_input.lower() == "exit":
            return jsonify({"response": "Ending the conversation. Take care!"})
        else:
            messages.append({"role": "user", "content": user_input})

        print("CONVERSATION:: User Input is ", user_input)
        ai_response = get_advice(messages)
        print("CONVERSATION:: ai_response is ", ai_response)
        messages.append({"role": "assistant", "content": ai_response})

        # After getting the AI response, save the conversation
        logger.info(f"Environment is {env}")
        if env == 'production':
            logger.info(f"Saving conversation {conversation_id} to S3")
            save_conversation_to_s3(conversation_id, messages)
        else:
            logger.info(f"Not saving conversation {conversation_id} to S3 in non-production environment")

        return jsonify({
            "response": ai_response,
            "messages": messages,
            "conversation_id": conversation_id
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Hello World"  # or your actual homepage response


if __name__ == '__main__':
    app.run(debug=True, port=5001)