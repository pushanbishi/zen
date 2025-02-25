from typing import List

from flask import Flask, request, jsonify
from openai import OpenAI
import configparser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def config(key: str):
    configuration = configparser.ConfigParser()
    configuration.read('../../config/zen.properties')
    value = configuration['perplexity'][key]
    return value

api_key = config('api_key')
client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")


def get_advice(messages):

    #print("api_key is ", api_key)
    print("message calling create is ", messages)
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    print("response from create is ", response.model_dump_json())
    content= response.choices[0].message.content
    #print("content is ", content)
    return content



@app.route('/chat', methods=['POST'])
def chat():
    #print("request is ", request)
    data = request.json
    #print("data is", data)
    user_input = data.get('user_input', '')
    #print("user_input is", user_input)

    messages = data.get('messages')

    if user_input.lower() == "exit":
        return jsonify({"response": "Ending the conversation. Take care!"})
    else:
        messages.append({"role": "user", "content": user_input})

    print("messages before get_advice is ", messages)
    ai_response = get_advice(messages)

    messages.append({"role": "assistant", "content": ai_response})

    return jsonify({"response": ai_response, "messages": messages})

@app.route('/config', methods=['GET'])
def get_config_route():
    key = request.args.get('key')
    value = config(key)
    return value



if __name__ == '__main__':
    app.run(debug=True, port=5001)
