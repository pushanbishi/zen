from flask import Flask, request, jsonify
import openai
import configparser
from flask_cors import CORS
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_advice(messages):
    openai.api_key = config('api_key')
    print("api_key is ", openai.api_key)
    print("message calling create is ", messages)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_completion_tokens=10000
    )
    print("response from create is ", response.model_dump_json())
    content= response.choices[0].message.content
    #print("content is ", content)
    return content

def google_search(query):
    api_key = config('google_api_key')
    cse_id = config('google_cse_id')
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id).execute()
    search_results = ""
    print("Raw Search Results ", res['items'])
    for item in res.get('items', []):
        search_results += f"Title: {item['title']}\nSnippet: {item['snippet']}\nLink: {item['link']}\n\n"
    print("Formatted Raw Search Results ", search_results)
    return search_results

@app.route('/chat', methods=['POST'])
def options() -> List[str]:
    return

@app.route('/chat', methods=['POST'])
def chat():
    print("request is ", request)
    data = request.json
    print("data is", data)
    user_input = data.get('user_input', '')
    print("user_input is", user_input)
    #do a web search using user_input
    if user_input and user_input.strip():
        web_results = google_search(user_input)
        print("web_results is ", web_results)
        #alter user_input to include search results and ask it to combine search results with GPT
        context = "You are ChatGPT, a helpful assistant. Combine your knowledge with the following web search results to answer accurately:\n"
        context += "\n".join(web_results)
        context += f"\n\nUser query: {user_input}"

    messages = data.get('messages')

    if user_input.lower() == "exit":
        return jsonify({"response": "Ending the conversation. Take care!"})
    elif user_input.lower() != '':
        messages.append({"role": "user", "content": context})

    print("messages before get_advice is ", messages)

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
