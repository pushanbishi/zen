from flask import Flask, request, jsonify
import openai
import configparser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# Load API key from properties file
config = configparser.ConfigParser()
config.read('../config/zen.properties')
openai.api_key = config['openai']['api_key']
print("api_key is ", openai.api_key)

def get_advice(messages):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    content= response.choices[0].message.content
    print("content is ", content)
    return content

@app.route('/chat', methods=['POST'])

def chat():
    print("request is ", request)
    data = request.json
    user_input = data.get('user_input', '')
    print("data is", data)
    messages = data.get('messages')

    if user_input.lower() == "exit":
        return jsonify({"response": "Ending the conversation. Take care!"})

    # messages.append({"role": "user", "content": user_input})
    ai_response = get_advice(messages)
    messages.append({"role": "assistant", "content": ai_response})

    return jsonify({"response": ai_response, "messages": messages})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
