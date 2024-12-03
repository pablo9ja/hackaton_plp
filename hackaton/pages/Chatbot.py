import os
import streamlit as st
import replicate
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load environment variables from .env file (if you're using it)
load_dotenv()

# Placeholder for dataset loading function
@st.cache_data
def load_data(file_path='fake_healthcare_2.csv'):
    # Replace with your dataset loading logic
    data = pd.read_csv('fake_healthcare_2.csv')
    return data

# Function to visualize data
def visualize_data(data, department, metric):
    filtered_data = data[data['departments'] == department]
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=filtered_data, x=filtered_data.index, y=metric)
    plt.title(f'{metric.capitalize()} Over Time for {department.capitalize()} Department')
    plt.xlabel('Date')
    plt.ylabel(metric.capitalize())
    st.pyplot(plt)

# Function to interpret and query dataset
def interpret_and_query_dataset(query):
    if 'average' in query.lower():
        metric = query.split('average of ')[-1]
        if metric in data.columns:
            average_value = data[metric].mean()
            return f"The average {metric} is {average_value:.2f}."
    elif 'total' in query.lower():
        metric = query.split('total of ')[-1]
        if metric in data.columns:
            total_value = data[metric].sum()
            return f"The total {metric} is {total_value:.2f}."
    return "I'm sorry, I don't understand the query."

data = load_data()

with st.sidebar:
    st.title('Llama 2 Chatbot')
    st.write('This chatbot is created using the open-source Llama 2 LLM model from Meta.')

    st.success('API key already provided!', icon='✅')

    replicate_api = st.text_input('Enter Replicate API token:', type='password')
    if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
        st.warning('Please enter your credentials!', icon='⚠️') 
    else:
        st.success('Proceed to entering your prompt message!', icon='👉')

    st.subheader('Models and parameters')
    selected_model = st.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

    st.subheader('Data Visualization')
    department = st.selectbox('Select Department', data['departments'].unique())
    metric = st.selectbox('Select Metric', ['daily_visits', 'daily_admissions', 'admission_rate', 'occupancy_rate'])
    if st.button('Visualize'):
        visualize_data(data, department, metric)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input, api_key):
    client = replicate.Client(api_token=api_key)
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    # Check if the prompt is a dataset-related query
    if 'dataset' in prompt_input.lower():
        response = interpret_and_query_dataset(prompt_input)
    else:
        output = client.run(
            llm,
            input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                   "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1}
        )
        response = ''.join(output)
    
    return response

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt, replicate_api)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
