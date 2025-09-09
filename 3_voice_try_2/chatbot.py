from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories.file import FileChatMessageHistory
from langchain.chains import LLMChain

def get_llm():
    return OllamaLLM(
        model = "gemma3n:e2b",
        temperature = 0.1,
    )

def get_chat_prompt_template():
    return ChatPromptTemplate(
        input_variables = ["content", "messages"],
        messages = [
            SystemMessagePromptTemplate.from_template("You are a helpful ai assistant. Try to answer to the best of your knowledge"),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessagePromptTemplate.from_template("{content}"),
        ],
    )

def get_memory():
    return ConversationBufferMemory(
        memory_key="messages",
        chat_memory= FileChatMessageHistory(file_path="memory.json"),
        return_messages=True,
        input_key="content",
    )

def create_chain(llm, prompt):
    return LLMChain(llm = llm, prompt = prompt, memory = get_memory())

llm = get_llm()
prompt = get_chat_prompt_template()
chain = create_chain(llm, prompt)

# print("Type your query (or 'q' to exit): ")
# while True:
#     question = input (">>> ")
#     if question.lower() == 'q':
#         break
#     response = chain.invoke({'content': question})
#     print(response['text'] if isinstance(response, dict) else response )

import speech_recognition as sr 
import pyttsx3

recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Sorry, I did not understand.")
        return ""
    except sr.RequestError:
        print("Speech recognition service failed.")
        return ""
    
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()


print("Say something (or say 'quit' to end): ")
while True:
    question = listen()
    if "quit" in question.lower():
        break
    if question:
        print("You said: ", question)
        response = chain.invoke({"content": question})
        answer = response['text'] if isinstance(response, dict) else response
        print("Assistant: ", answer)
        speak(answer)