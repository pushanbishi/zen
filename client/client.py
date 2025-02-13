import requests
import json
import configparser


url = "http://127.0.0.1:5001/chat"
headers = {"Content-Type": "application/json"}

# Load API key from properties file
config = configparser.ConfigParser()
config.read('../config/zen.properties')
sys_prompt = config['perplexity']['system_prompt']
user_prompt = config['perplexity']['user_prompt']
#print("initial_prompt:: ", initial_prompt)

# Initialize conversation history
messages = [{"role": "system", "content": sys_prompt}]
#user_input = "Hello, I am a volunteer with a crisis help line and need help finding some information a caller needs. Is it ok if I ask you a few questions?"
messages.append({"role": "user", "content": user_prompt})

# Send request to the server
print("messages before first call:: ", messages)
response = requests.post(url, headers=headers, data=json.dumps({"user_input": user_prompt, "messages": messages}))
print("response after first call:: ", response)
response_data = response.json()
ai_response = response_data["response"]
messages = response_data["messages"]

# Print the AI response
print(f"AI: {ai_response}")


while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Ending the conversation. Take care!")
        break

    # Add user input to messages
    messages.append({"role": "user", "content": user_input})
    print("messages:: ", messages)

    # Send request to the server
    response = requests.post(url, headers=headers, data=json.dumps({"user_input": user_input, "messages": messages}))
    print("response:: ", response)
    # Get the response from the server
    response_data = response.json()
    ai_response = response_data["response"]
    messages = response_data["messages"]

    # Print the AI response
    print(f"AI: {ai_response}")