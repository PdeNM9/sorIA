import streamlit as st
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from dotenv import load_dotenv, find_dotenv
from PyPDF2 import PdfReader
import prompt

# Carrega variáveis de ambiente
_ = load_dotenv(find_dotenv())

st.title("Análise da Inicial.")

# Carrega o modelo de linguagem treinado em português
model_name = "unicamp-dl/ptt5-base-portuguese-vocab"
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Função para gerar resposta
def generate_response(text):
    inputs = tokenizer.encode("translate English to Portuguese: " + text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=512, num_beams=4, early_stopping=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Upload do arquivo PDF
uploaded_file = st.file_uploader("Envie o arquivo PDF", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.session_state.messages.append({"role": "user", "content": "Arquivo PDF enviado e processado."})
    with st.chat_message("user"):
        st.markdown("Arquivo PDF enviado e processado.")

    # Gera a resposta usando o modelo
    full_response = generate_response(pdf_text)

    # Salva a resposta completa no histórico se for única
    if full_response not in st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Exibe a resposta em itens separados
    respostas = full_response.split('\n')
    for resposta in respostas:
        if resposta.strip():  # Verifica se a resposta não está vazia
            st.chat_message("assistant").markdown(resposta.strip())
