from langchain.vectorstores import FAISS

from langchain.embeddings.openai import AzureOpenAIEmbeddings

from langchain.chat_models import AzureChatOpenAI

from langchain.chains import ConversationalRetrievalChain

from langchain.schema import HumanMessage, AIMessage

import openai

import json


# Mock function simulating system status check

def check_system_status(device_id: str) -> str:

status_map = {

"printer01": "Online and functioning normally.",

"router23": "Offline - requires restart.",

"server07": "Online but high CPU usage.",

}

return status_map.get(device_id, "Device not found.")


# Prepare mock documents

mock_docs = [

"How to reset my password? Visit the password reset page and follow instructions.",

"My computer is slow. Restart, close apps, run antivirus scan.",

"Connect to VPN by installing client from IT portal and login.",

"Printer issues: check power, connection, ink and paper.",

]


# Step 1: Generate embeddings

embeddings = AzureOpenAIEmbeddings( model="text-embedding-3-large", # azure_endpoint="https://<your-endpoint>.openai.azure.com/", If not provided, will read env variable AZURE_OPENAI_ENDPOINT # api_key=... # Can provide an API key directly. If missing read env variable AZURE_OPENAI_API_KEY # openai_api_version=..., # If not provided, will read env variable AZURE_OPENAI_API_VERSION )


# Step 2: Create FAISS index from mock docs embeddings

vectorstore = FAISS.from_texts(mock_docs, embedding=embeddings)


# Step 3: Initialize AzureChatOpenAImodel

chat = AzureChatOpenAI(

azure_deployment="gpt-4o-mini",

azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT"), # or your deployment

api_version="2024-07-01-preview", # or your api version

api_key= os.getenv("AZURE_OPENAI_API_KEY"),

# other params...

)



# Step 4: Setup Conversational Retrieval Chain

retrieval_chain = ConversationalRetrievalChain.from_llm(

llm=chat,

retriever=vectorstore.as_retriever(),

return_source_documents=True,

)


# Step 5: Define OpenAI functions metadata

functions = [

{

"name": "check_system_status",

"description": "Checks device status by device ID",

"parameters": {

"type": "object",

"properties": {

"device_id": {

"type": "string",

"description": "Device unique identifier"

}

},

"required": ["device_id"],

},

}

]


# Step 6: Conversation with function calling

def chat_with_functions(user_input, chat_history):

messages = [{"role": "system", "content": "You are an IT helpdesk assistant."}]

for q, a in chat_history:

messages.append({"role": "user", "content": q})

messages.append({"role": "assistant", "content": a})

messages.append({"role": "user", "content": user_input})


response = openai.ChatCompletion.create(

model="gpt-4o-mini",

messages=messages,

functions=functions,

function_call="auto"

)

message = response["choices"][0]["message"]


if message.get("function_call"):

func_name = message["function_call"]["name"]

args = json.loads(message["function_call"]["arguments"])

if func_name == "check_system_status":

result = check_system_status(args["device_id"])

chat_history.append((user_input, result))

return result, chat_history


reply = message["content"]

chat_history.append((user_input, reply))

return reply, chat_history


# Example interactive loop

if __name__ == "__main__":

chat_history = []

print("Welcome to IT Helpdesk RAG Chatbot!")

while True:

query = input("You: ")

if query.lower() in ("exit", "quit"):

break


# Retrieve relevant docs and generate answer

rag_result = retrieval_chain({"question": query, "chat_history": chat_history})

print(f"RAG Answer: {rag_result['answer']}")


# Generate answer using function calling if needed

func_answer, chat_history = chat_with_functions(query, chat_history)

print(f"Function Call Answer: {func_answer}\n")