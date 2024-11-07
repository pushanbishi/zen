# file: mental_health_counselor_loop.py

import openai
import configparser


# Load API key from properties file
config = configparser.ConfigParser()
config.read('../config/zen.properties')
openai.api_key = config['openai']['api_key']
initial_prompt = config['openai']['initial_prompt']


def get_advice(messages):
    response = openai.chat.completions.create(
        model="gpt-4",  # Specify the OpenAI model (e.g., 'gpt-4' or 'gpt-3.5-turbo')
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content


def start_conversation():
    print("Welcome to the mental health counselor. Type 'exit' to end the conversation.")

    # Initialize the conversation with a system prompt
    messages = [
        {"role": "system", "content": initial_prompt}
    ]
    print("You asked:", initial_prompt)

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if the user wants to exit
        if user_input.lower() == "exit":
            print("Ending the conversation. Take care!")
            break

        # Append the user message to the conversation history
        messages.append({"role": "user", "content": user_input})

        # Get advice from the AI based on conversation history
        ai_response = get_advice(messages)

        # Append AI response to the conversation history
        messages.append({"role": "assistant", "content": ai_response})

        # Print the AI's response
        print("Counselor:", ai_response)


if __name__ == "__main__":
    start_conversation()
