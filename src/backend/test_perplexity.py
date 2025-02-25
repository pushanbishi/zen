from openai import OpenAI

YOUR_API_KEY = "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"

messages = [
    {
        "role": "system",
        "content": (
            "You will be used to support crisis helpline volunteers in finding information about mental health, mental health care providers, facilities, and resources. \
  in finding information about mental health, mental health care providers, facilities, and resources. \
  When responding to queries, prioritize presenting the following information in a clear and structured format:\
  Provider name, address, phone number, and website.\
   If you are unable to find the information, please let the volunteer know.\
   If you are unsure about the information, please let the volunteer know.\
  You will not provide any information until you are asked to do so by the volunteer.\
  You will not provide any diagnosis or treatment advice. You will politely decline to \
  provide any information about anything else except for the information about mental health,\
   mental health care providers, facilities, and resources."
         ),
    },
    {   
        "role": "user",
        "content": (
            'can  you recommend some movies showing near zip code 27705'
        ),
    },
    
]

client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

# chat completion without streaming
response = client.chat.completions.create(
    model="sonar-pro",
    messages=messages,
)
print(response.choices[0].message.content)

# chat completion with streaming
response_stream = client.chat.completions.create(
    model="sonar-pro",
    messages=messages,
    stream=True,
)
#for response in response_stream:
#    print(response)