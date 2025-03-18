import configparser
import json
import boto3

# Read existing zen.properties
config = configparser.ConfigParser()
config.read('../../../config/zen.properties')

# Get test values from zen.properties
api_key = config['crisis_line_assistant.test']['api_key']
system_prompt = config['crisis_line_assistant.test']['system_prompt']
default_ai_prompt = config['crisis_line_assistant.test']['default_ai_prompt']

# Create AWS SSM client
ssm = boto3.client('ssm')


# Store other config
config_json = json.dumps({
    "crisis_line_assistant": {
        "api_key": api_key,
        "system_prompt": system_prompt,
        "default_ai_prompt": default_ai_prompt
    }
})

ssm.put_parameter(
    Name='/myapp/config/test/zen-properties',
    Value=config_json,
    Type='String',
    Overwrite=True
)

# Get production values from zen.properties
api_key = config['crisis_line_assistant.production']['api_key']
system_prompt = config['crisis_line_assistant.production']['system_prompt']
default_ai_prompt = config['crisis_line_assistant.production']['default_ai_prompt']

# Create AWS SSM client
ssm = boto3.client('ssm')


# Store other config
config_json = json.dumps({
    "crisis_line_assistant": {
        "api_key": api_key,
        "system_prompt": system_prompt,
        "default_ai_prompt": default_ai_prompt
    }
})

ssm.put_parameter(
    Name='/myapp/config/production/zen-properties',
    Value=config_json,
    Type='String',
    Overwrite=True
)

print("Parameters successfully created in AWS Parameter Store!")