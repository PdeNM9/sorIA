import streamlit as st
from sqlalchemy.sql.expression import text

# Inicializar conexão.
conexao = st.connection('mysql', type='sql')

def buscar_minutas_por_nome(conexao, name_input):
    # Formatar a string de entrada para evitar problemas de SQL Injection
    name_input_formatted = '%' + name_input + '%'

    # Realizar a consulta ao banco de dados
    query = f"SELECT Nome_da_Minuta, Conteudo_da_Minuta, Campos, Fase, Ramo, Tipo, Variáveis FROM minutas WHERE Nome_da_Minuta LIKE '{name_input_formatted}'"
    resultados = conexao.query(query)

    # Verificar se o DataFrame está vazio
    if resultados is not None and not resultados.empty:
        return resultados
    else:
        return None

def atualizar_minuta(conexao, nome_da_minuta, campos, conteudo_da_minuta, fase, ramo, tipo, variaveis):
    try:
        # Construir o comando SQL para atualizar os dados da minuta
        comando_sql = f"""
        UPDATE minutas
        SET Nome_da_Minuta = '{nome_da_minuta}', Campos = '{campos}', Conteudo_da_Minuta = '{conteudo_da_minuta}', Fase = '{fase}', Ramo = '{ramo}', Tipo = '{tipo}', Variáveis = '{variaveis}'
        WHERE Nome_da_Minuta = '{nome_da_minuta}'
        """

        # Declarar o comando SQL como string segura
        comando_sql = text(comando_sql)

        # Utilizando a sessão para executar o comando SQL
        with conexao.session as s:
            s.execute(comando_sql)
            s.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar minuta: {e}")
        return False

# Cria sidebar
def sidebar():
    st.sidebar.title('Informações')
    st.sidebar.markdown(f"""Desenvolvido por **PdeNM9**. Contribua para o projeto pela chave PIX: pdenm9@gmail.com""")