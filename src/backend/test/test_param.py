import boto3

# Test parameter access
ssm = boto3.client('ssm')

# Test API key access
api_key = ssm.get_parameter(
    Name='/myapp/secrets/test/perplexity-api-key',
    WithDecryption=True
)
print("API Key retrieved successfully! ", api_key)

# Test config access
config = ssm.get_parameter(
    Name='/myapp/config/test/zen-properties'
)
#print("Config retrieved successfully!")
#print(config['Parameter']['Value'])