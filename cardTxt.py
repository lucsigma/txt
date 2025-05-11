
# -- coding: utf-8 --
import sqlite3
import streamlit as st
import pandas as pd

# Conexão com o banco de dados
conn = sqlite3.connect("cardapio.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    prato TEXT NOT NULL
)
""")
conn.commit()

# Corrigir prato com erro de digitação no banco
cursor.execute("UPDATE pedidos SET prato = 'panelada' WHERE prato = 'Paindada'")
conn.commit()

# Lista de pratos corrigida
pratos = ["cozidão", "peixe frito", "assado de panela", "frango frito",
          "porco frito", "chambari", "galinha caipira", "Panelada"]

st.title("Sistema de Pedidos - Cardápio")

st.subheader("Escolha seu prato")
nome = st.text_input("Digite seu nome")
escolha = st.selectbox("Escolha um prato:", pratos)

if st.button("Registrar Pedido"):
    if nome and escolha:
        cursor.execute("INSERT INTO pedidos (nome, prato) VALUES (?, ?)", (nome, escolha))
        conn.commit()
        st.success(f"{nome} escolheu {escolha} para o almoço")
    else:
        st.error("Por favor, preencha seu nome e escolha um prato.")

# Botão de exclusão com senha
st.subheader("Administração")
senha = st.text_input("Digite a senha para excluir todos os pedidos", type="password")
if st.button("Apagar todos os registros"):
    if senha == "1234":
        cursor.execute("DELETE FROM pedidos")
        conn.commit()
        with open("resumo_pedidos.txt", "w", encoding="utf-8") as f:
            f.write("")
        st.success("Todos os registros foram apagados.")
    else:
        st.error("Senha incorreta. A exclusão foi cancelada.")

# Resumo dos pedidos
st.subheader("Resumo dos Pedidos")

# Consulta geral dos pedidos
cursor.execute("SELECT nome, prato FROM pedidos")
todos_pedidos = cursor.fetchall()

# Cria DataFrame com todos os pedidos
df_pedidos = pd.DataFrame(todos_pedidos, columns=["Nome", "Prato"])

# Exibe a tabela completa
st.markdown("### Tabela de Pedidos")
st.dataframe(df_pedidos)

# Agrupa por prato para mostrar quantidade por prato
df_resumo = df_pedidos.groupby("Prato").size().reset_index(name="Quantidade")

# Exibe o resumo agrupado
st.markdown("### Resumo por Prato")
st.dataframe(df_resumo)

# Total de pedidos
total = df_pedidos.shape[0]
st.write(f"*Total de pratos escolhidos:* {total}")

# Gerar conteúdo formatado como tabela para salvar em TXT
resumo = f"{'Prato':<20} | {'Quantidade':<10} | {'Nomes'}\n"
resumo += "-" * 60 + "\n"

for _, row in df_resumo.iterrows():
    prato = row['Prato']
    qtd = row['Quantidade']
    nomes = df_pedidos[df_pedidos['Prato'] == prato]['Nome'].tolist()
    nomes_str = ", ".join(nomes)
    resumo += f"{prato:<20} | {qtd:<10} | {nomes_str}\n"

# Salvar como TXT
with open("resumo_pedidos.txt", "w", encoding="utf-8") as f:
    f.write(resumo)

with open("resumo_pedidos.txt", "rb") as f:
    st.download_button("Baixar resumo em TXT", f, file_name="resumo_pedidos.txt", mime="text/plain")