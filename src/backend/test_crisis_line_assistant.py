import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from io import StringIO

# Import the Flask app
from crisis_line_assistant import app, fetch_config, get_advice

class TestCrisisLineAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = app.test_client()
        self.app.testing = True
        # Save original environment
        self.original_env = os.environ.copy()
        # Set up environment variables for testing
        os.environ['APP_ENV'] = 'local'

    def tearDown(self):
        """Reset environment variables after tests."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('configparser.ConfigParser')
    def test_fetch_config_local(self, mock_configparser):
        """Test fetching config from local file."""
        # Setup mock
        mock_config = MagicMock()
        mock_configparser.return_value = mock_config
        mock_config.read.return_value = ['../../config/zen.properties']
        mock_config.__getitem__.return_value.__getitem__.return_value = "test_value"

        # Test fetch_config
        result = fetch_config('test_key')
        self.assertEqual(result, "test_value")
        mock_configparser.assert_called_once()

    @patch('boto3.client')
    def test_fetch_config_test_env(self, mock_boto3_client):
        """Test fetching config from AWS Parameter Store in test environment."""
        # Set environment
        os.environ['APP_ENV'] = 'test'
        
        # Setup mock for API key
        mock_ssm = MagicMock()
        mock_boto3_client.return_value = mock_ssm
        mock_ssm.get_parameter.return_value = {
            'Parameter': {'Value': 'test_api_key'}
        }
        
        # Test fetch_config for API key
        result = fetch_config('perplexity_api_key')
        self.assertEqual(result, "test_api_key")
        mock_ssm.get_parameter.assert_called_with(
            Name='/myapp/secrets/test/perplexity-api-key',
            WithDecryption=True
        )
        
        # Setup mock for other config
        mock_ssm.get_parameter.return_value = {
            'Parameter': {'Value': json.dumps({'perplexity': {'system_prompt': 'test_prompt'}})}
        }
        
        # Test fetch_config for other config
        result = fetch_config('system_prompt')
        self.assertEqual(result, "test_prompt")

    @patch('boto3.client')
    def test_fetch_config_production_env(self, mock_boto3_client):
        """Test fetching config from AWS Parameter Store in production environment."""
        # Set environment
        os.environ['APP_ENV'] = 'production'
        
        # Setup mock
        mock_ssm = MagicMock()
        mock_boto3_client.return_value = mock_ssm
        mock_ssm.get_parameter.return_value = {
            'Parameter': {'Value': 'prod_api_key'}
        }
        
        # Test fetch_config
        result = fetch_config('perplexity_api_key')
        self.assertEqual(result, "prod_api_key")
        mock_ssm.get_parameter.assert_called_with(
            Name='/myapp/secrets/production/perplexity-api-key',
            WithDecryption=True
        )

    def test_index_route(self):
        """Test the index route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "Hello World")

    @patch('crisis_line_assistant.fetch_config')
    def test_config_route(self, mock_fetch_config):
        """Test the config route."""
        # Setup mock
        mock_fetch_config.return_value = "test_config_value"
        
        # Test with key
        response = self.app.get('/config?key=test_key')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "test_config_value")
        mock_fetch_config.assert_called_with('test_key')
        
        # Test without key
        response = self.app.get('/config')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['error'], "Missing key parameter")

    @patch('crisis_line_assistant.get_advice')
    def test_chat_route(self, mock_get_advice):
        """Test the chat route."""
        # Setup mock
        mock_get_advice.return_value = "AI response"
        
        # Test chat endpoint
        response = self.app.post('/chat',
                             data=json.dumps({
                                 'user_input': 'Hello',
                                 'messages': [{'role': 'system', 'content': 'You are a helpful AI'}]
                             }),
                             content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['response'], "AI response")
        self.assertEqual(len(data['messages']), 3)  # system + user + AI
        self.assertEqual(data['messages'][-1]['content'], "AI response")
        
        # Test exit command
        response = self.app.post('/chat',
                             data=json.dumps({
                                 'user_input': 'exit',
                                 'messages': []
                             }),
                             content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['response'], "Ending the conversation. Take care!")

    @patch('openai.OpenAI')
    def test_get_advice(self, mock_openai):
        """Test the get_advice function."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices = [MagicMock(message=MagicMock(content="AI response"))]
        
        # Redirect stdout to capture prints
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Test get_advice
        messages = [{"role": "user", "content": "Hello"}]
        result = get_advice(messages)
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        self.assertEqual(result, "AI response")
        mock_client.chat.completions.create.assert_called_with(
            model="sonar-pro",
            messages=messages
        )
        
        # Check that the function printed the messages
        self.assertIn("message calling create is", captured_output.getvalue())

if __name__ == '__main__':
    unittest.main() 