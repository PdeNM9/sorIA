import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
from PyPDF2 import PdfFileReader
import io

# Carrega variáveis de ambiente
_ = load_dotenv(find_dotenv())

st.title("Chat com Modelo de Linguagem - LangChain")

# Configuração do prompt e do modelo
system = """# Função e objetivo

Você é um Juiz de Direito no Brasil. Seu objetivo é ler o arquivo e identificar informações.

# Passos

1. Localize as seguintes informações constantes no arquivo: 

* Qual o número do processo? (Obs.: todo número de processo tem números inteiros, um ‘-’ e quatro ‘.’ no seguinte formato 8088000-01.2024.8.05.0001)  

* Quem é o polo ativo (autor, impetrante, embargante) da demanda? 

* Quem é o polo passivo (réu, autoridade coatora, Estado ou Município, embargado) da demanda? 

* Transcreva os fatos, completando a seguinte frase substituindo o termo F3 pela transcrição dos fatos como constam da petição: Argumenta, para tanto, em resumo, que “F3”. 

* Houve pedido liminar? Responda sim ou não. 

* Houve pedido de gratuidade da justiça? Responda sim ou não.

* Se houve pedido liminar, transcreva completando a seguinte frase substituindo o termo L5 pela transcrição dos pedidos como constam da petição: Nesses termos, requer a concessão de medida liminar, para que "L5". 

* Transcreva os pedidos, completando a seguinte frase substituindo o termo P4 pela transcrição dos pedidos como constam da petição: Ao final, requer: “P4”."""

human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
chat = ChatGroq(temperature=0, model_name="llama3-8b-8192")
chain = prompt | chat

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfFileReader(pdf_file)
    text = ""
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        text += page.extract_text()
    return text

# Upload do arquivo PDF
uploaded_file = st.file_uploader("Envie o arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.session_state.messages.append({"role": "user", "content": pdf_text})
    with st.chat_message("user"):
        st.markdown(pdf_text)

    # Adiciona um container para a resposta do modelo
    response_stream = chain.stream({"text": pdf_text})    
    full_response = ""

    response_container = st.chat_message("assistant")
    response_text = response_container.empty()

    for partial_response in response_stream:
        full_response += str(partial_response.content)
        response_text.markdown(full_response + "▌")

    # Salva a resposta completa no histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})
