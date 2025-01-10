from flask import Flask, request, jsonify
import openai
import configparser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_advice(messages):
    openai.api_key = config('api_key')
    print("api_key is ", openai.api_key)
    #print("message calling create is ", messages)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_completion_tokens=10000
    )
    print("response from create is ", response.model_dump_json())
    print("prompt_tokens from create is ", response.usage.prompt_tokens)
    print("completion_tokens from create is ", response.usage.completion_tokens)
    content= response.choices[0].message.content
    #print("content is ", content)
    return content

@app.route('/chat', methods=['POST'])
def chat():
    print("request is ", request)
    data = request.json
    print("data is", data)
    user_input = data.get('user_input', '')
    print("user_input is", user_input)
    messages = data.get('messages')

    if user_input.lower() == "exit":
        return jsonify({"response": "Ending the conversation. Take care!"})
    elif user_input.lower() != '':
        messages.append({"role": "user", "content": user_input})


    ai_response = get_advice(messages)
    messages.append({"role": "assistant", "content": ai_response})

    return jsonify({"response": ai_response, "messages": messages})

@app.route('/config', methods=['GET'])
def get_config_route():
    key = request.args.get('key')
    value = config(key)
    return value

def config(key: str):
    configuration = configparser.ConfigParser()
    configuration.read('../../config/zen.properties')
    value = configuration['openai'][key]
    return value


if __name__ == '__main__':
    app.run(debug=True, port=5001)
