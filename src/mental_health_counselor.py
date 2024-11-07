# file: mental_health_counselor.py

import openai
import configparser

# Load API key from properties file
config = configparser.ConfigParser()
config.read('./config/zen.properties')
openai.api_key = config['openai']['api_key']
prompt = config['openai']['initial_prompt']


def get_advice(user_prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",  # OpenAI's powerful model, replaceable with 'gpt-4' if available
        messages=[{
            "role": "system",
            "content": user_prompt}],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    user_input = prompt
    print("You asked:", user_input)
    print("Here's the advice:")

    advice = get_advice(user_input)
    print(advice)
