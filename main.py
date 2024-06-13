import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from annotated_text import annotated_text
import re

# Configuração da página deve ser a primeira coisa a ser chamada
caput = st.set_page_config(page_title="Assessor 2.0!", page_icon="📣", layout="centered")
import funcoes
import variaveis



funcoes.sidebar()

@st.cache
def create_annotated_text(text, annotations):
    # Usando expressão regular para otimizar a criação do texto anotado
    pattern = re.compile("|".join(re.escape(v) for v in annotations.values()))
    result = []
    last_end = 0
    for match in pattern.finditer(text):
        if last_end < match.start():
            result.append(text[last_end:match.start()])
        result.append((match.group(), list(annotations.keys())[list(annotations.values()).index(match.group())]))
        last_end = match.end()
    if last_end < len(text):
        result.append(text[last_end:])
    return result

st.title('Consulta de Minutas.')

# Input para buscar pelo nome da minuta
name_input = st.text_input("Digite uma palavra para pesquisar:", key="input_search")

if name_input:
    resultados = funcoes.buscar_minutas_por_nome(funcoes.conexao, name_input)
    if resultados is not None and not resultados.empty:
        # Ajuste para extrair nomes das minutas de um DataFrame
        nomes_minutas = resultados['Nome_da_Minuta'].tolist()
        escolha = st.selectbox("Escolha uma minuta:", nomes_minutas, key="select_minuta")

        # Ajuste para extrair o conteúdo da minuta selecionada
        conteudo_da_minuta = resultados.loc[resultados['Nome_da_Minuta'] == escolha, 'Conteudo_da_Minuta'].values[0]

        # Identificar variáveis no conteúdo da minuta com base no dicionário de variáveis
        variaveis_encontradas = {descricao: variaveis.data[descricao]
                                 for descricao in variaveis.data if variaveis.data[descricao] in conteudo_da_minuta}
        valores_variaveis = {}
        for idx, (descricao, identificador) in enumerate(variaveis_encontradas.items()):
            valores_variaveis[identificador] = st.sidebar.text_input(f"{descricao}:", key=f"{identificador}_{idx}")

        # Substituir as variáveis no conteúdo da minuta pelos valores inseridos
        conteudo_modificado = conteudo_da_minuta
        for identificador, valor in valores_variaveis.items():
            conteudo_modificado = conteudo_modificado.replace(identificador, valor)

        if conteudo_modificado == conteudo_da_minuta:
            st.write("### Conteúdo Original da Minuta:")
            anotacoes = create_annotated_text(conteudo_da_minuta, variaveis.data)
            annotated_text(*anotacoes)
            st_copy_to_clipboard(conteudo_da_minuta, "Copiar Conteúdo Original", "✅ Conteúdo Original Copiado!")
        else:
            # Criando colunas para exibir os textos lado a lado
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Conteúdo Original da Minuta:")
                anotacoes = create_annotated_text(conteudo_da_minuta, variaveis.data)
                annotated_text(*anotacoes)
                st_copy_to_clipboard(conteudo_da_minuta, "Copiar Conteúdo Original", "✅ Conteúdo Original Copiado!")

            with col2:
                st.write("### Conteúdo Modificado:")
                st.write(conteudo_modificado)
                st_copy_to_clipboard(conteudo_modificado, "Copiar Conteúdo Modificado", "✅ Conteúdo Modificado Copiado!")
    else:
        st.warning("Nenhum registro encontrado para o termo pesquisado.")