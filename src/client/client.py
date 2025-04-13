import requests
import json



url = "http://127.0.0.1:5001"
headers = {"Content-Type": "application/json"}

# Get configuration from server
try:
    response = requests.get(f"{url}/config", params={"key": 'system_prompt'}, headers=headers)
     
    #print("response:: ", response.json())
    
    config_data = response.json()
    sys_prompt = config_data['value']
    
    response = requests.get(f"{url}/config", params={"key": 'default_ai_prompt'}, headers=headers)
    config_data = response.json()
     
    default_ai_prompt = config_data['value']
except Exception as e:
    print(f"Error fetching configuration: {e}")
    raise e

print(f"AI: {default_ai_prompt}")
# Initialize conversation history
messages = [{"role": "system", "content": sys_prompt}]

user_input = input("You: ")
if user_input.lower() == "exit":
    print("Ending the conversation. Take care!")
    exit()
   

# Send request to the server
print("messages before first call:: ", messages)
response = requests.post(f"{url}/chat", headers=headers, data=json.dumps({"user_input": user_input, "messages": messages}))
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
    #messages.append({"role": "user", "content": user_input})
    #print("messages:: ", messages)

    # Send request to the server
    response = requests.post(f"{url}/chat", headers=headers, data=json.dumps({"user_input": user_input, "messages": messages}))
    print("response:: ", response)
    # Get the response from the server
    response_data = response.json()
    ai_response = response_data["response"]
    messages = response_data["messages"]

    # Print the AI response
    print(f"AI: {ai_response}")