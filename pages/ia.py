import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
from PyPDF2 import PdfReader
import prompt

# Carrega variáveis de ambiente
_ = load_dotenv(find_dotenv())

st.title("Análise da Inicial.")

# Configuração do prompt e do modelo
system = prompt.prompt

human = "{text}"
chat_prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
chat = ChatGroq(temperature=1, model_name="llama3-8b-8192")
chain = chat_prompt | chat

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Upload do arquivo PDF
uploaded_file = st.file_uploader("Envie o arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.session_state.messages.append({"role": "user", "content": "Arquivo PDF enviado e processado."})
    with st.chat_message("user"):
        st.markdown("Arquivo PDF enviado e processado.")

    # Adiciona um container para a resposta do modelo
    response_stream = chain.stream({"text": pdf_text})    
    full_response = ""

    response_container = st.chat_message("assistant")
    response_text = response_container.empty()

    for partial_response in response_stream:
        full_response += str(partial_response.content)
        response_text.markdown(full_response + "▌")

    # Corrige a resposta para remover o caractere de continuidade
    full_response = full_response.replace("▌", "").strip()

    # Salva a resposta completa no histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Exibe a resposta em itens separados
    respostas = full_response.split('\n')
    for resposta in respostas:
        if resposta.strip():  # Verifica se a resposta não está vazia
            st.chat_message("assistant").markdown(resposta.strip())
