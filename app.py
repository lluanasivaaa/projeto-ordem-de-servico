import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

from db_connection import (
    conectar,
    listar_clientes,
    inserir_cliente,
    listar_ordens,
    inserir_ordem,
    listar_servicos,
    inserir_servico,
    listar_itens,
    inserir_item
)

# Configuração da página
st.set_page_config(page_title="Sistema OS", layout="wide")
st.title("📋 Sistema de Ordem de Serviço e Orçamento")

# Conexão com o banco
conn = conectar()
if not conn:
    st.error("Erro ao conectar no banco de dados.")
    st.stop()

# Mapeamento de status
status_map = {
    "aberta": "Aberta",
    "em_andamento": "Em Andamento",
    "finalizada": "Finalizada",
    "cancelada": "Cancelada"
}

# Menu lateral
menu = st.sidebar.radio("Menu", ["Clientes", "Ordens de Serviço", "Serviços", "Itens"])

# Função para gerar PDF
def gerar_relatorio_cliente(conn, cliente_id):
    cursor = conn.cursor()

    cursor.execute("SELECT nome, email, telefone FROM clientes WHERE id = %s", (cliente_id,))
    cliente = cursor.fetchone()
    if not cliente:
        return None

    nome, email, telefone = cliente

    cursor.execute("SELECT id, data_abertura, status FROM ordens WHERE cliente_id = %s", (cliente_id,))
    ordens = cursor.fetchall()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Relatório do Cliente: {nome}", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Email: {email}", ln=True)
    pdf.cell(0, 10, f"Telefone: {telefone}", ln=True)
    pdf.ln(10)

    for ordem in ordens:
        ordem_id, data_abertura, status = ordem
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Ordem ID: {ordem_id} | Data: {data_abertura} | Status: {status}", ln=True)

        cursor.execute("SELECT descricao, valor FROM servicos WHERE ordem_id = %s", (ordem_id,))
        servicos = cursor.fetchall()
        if servicos:
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, "  Serviços:", ln=True)
            for s in servicos:
                pdf.cell(0, 8, f"   - {s[0]} (R$ {s[1]:.2f})", ln=True)

        cursor.execute("SELECT nome, quantidade, valor_unitario FROM itens WHERE ordem_id = %s", (ordem_id,))
        itens = cursor.fetchall()
        if itens:
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, "  Itens:", ln=True)
            for i in itens:
                nome_item, qtd, valor_unit = i
                pdf.cell(0, 8, f"   - {nome_item} x{qtd} (R$ {valor_unit:.2f})", ln=True)

        pdf.ln(5)

    nome_arquivo = f"relatorio_cliente_{cliente_id}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# ---------------- CLIENTES ----------------
if menu == "Clientes":
    st.subheader("👤 Cadastro de Clientes")
    with st.form(key="form_cliente"):
        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        btn_cadastrar = st.form_submit_button("Cadastrar Cliente")

        if btn_cadastrar:
            if nome.strip() == "" or email.strip() == "" or telefone.strip() == "":
                st.warning("Preencha todos os campos.")
            else:
                from db_connection import email_existe
                if email_existe(email):
                    st.error("Esse email já está cadastrado. Use outro.")
                else:
                    inserir_cliente(conn, nome, email, telefone)
                    st.success(f"Cliente '{nome}' cadastrado com sucesso!")

    st.divider()
    st.subheader("📋 Lista de Clientes")
    clientes = listar_clientes(conn)
    df_clientes = pd.DataFrame(clientes, columns=["ID", "Nome", "Email", "Telefone"])
    st.dataframe(df_clientes, use_container_width=True)

    st.subheader("📤 Gerar Relatório de Cliente")
    clientes_dict = {f"{c[1]} (ID {c[0]})": c[0] for c in clientes}
    cliente_selecionado = st.selectbox("Selecione o cliente", list(clientes_dict.keys()))
    btn_relatorio = st.button("📄 Gerar Relatório em PDF")

    if btn_relatorio:
        cliente_id = clientes_dict[cliente_selecionado]
        caminho_pdf = gerar_relatorio_cliente(conn, cliente_id)
        if caminho_pdf and os.path.exists(caminho_pdf):
            with open(caminho_pdf, "rb") as file:
                st.download_button(
                    label="📥 Baixar Relatório",
                    data=file,
                    file_name=caminho_pdf,
                    mime="application/pdf"
                )
        else:
            st.error("Erro ao gerar o relatório.")

# ---------------- ORDENS DE SERVIÇO ----------------
elif menu == "Ordens de Serviço":
    st.subheader("🛠️ Cadastro de Ordens de Serviço")

    clientes = listar_clientes(conn)
    clientes_dict = {f"{c[1]} (ID {c[0]})": c[0] for c in clientes}

    with st.form(key="form_ordem"):
        cliente_nome_id = st.selectbox("Cliente", list(clientes_dict.keys()))
        cliente_id = clientes_dict[cliente_nome_id]
        data_abertura = st.date_input("Data de abertura", value=datetime.today())
        status_legivel = st.selectbox("Status", list(status_map.values()))

        btn_cadastrar_ordem = st.form_submit_button("Cadastrar Ordem")
        if btn_cadastrar_ordem:
            status_chave = [k for k, v in status_map.items() if v == status_legivel][0]
            inserir_ordem(conn, cliente_id, data_abertura, status_chave)
            st.success("✅ Ordem cadastrada com sucesso!")

    st.divider()
    st.subheader("📑 Ordens Cadastradas")
    ordens = listar_ordens(conn)
    df_ordens = pd.DataFrame(ordens, columns=["ID", "Cliente", "Data de Abertura", "Status", "Total (R$)"])
    df_ordens["Status"] = df_ordens["Status"].map(status_map)
    st.dataframe(df_ordens, use_container_width=True)

# ---------------- SERVIÇOS ----------------
elif menu == "Serviços":
    st.subheader("🧰 Cadastro de Serviços")

    ordens = listar_ordens(conn)
    ordens_dict = {f"Ordem {o[0]} - {o[1]}": o[0] for o in ordens}

    with st.form(key="form_servico"):
        ordem_id = st.selectbox("Ordem de Serviço", list(ordens_dict.keys()))
        descricao = st.text_input("Descrição do serviço")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
        btn_add_servico = st.form_submit_button("Adicionar Serviço")

        if btn_add_servico:
            inserir_servico(conn, ordens_dict[ordem_id], descricao, valor)
            st.success("✅ Serviço adicionado!")

    st.divider()
    st.subheader("📋 Serviços Cadastrados")
    servicos = listar_servicos(conn)
    df_servicos = pd.DataFrame(servicos, columns=["ID", "Ordem ID", "Descrição", "Valor (R$)"])
    st.dataframe(df_servicos, use_container_width=True)

# ---------------- ITENS ----------------
elif menu == "Itens":
    st.subheader("📦 Cadastro de Itens")

    ordens = listar_ordens(conn)
    ordens_dict = {f"Ordem {o[0]} - {o[1]}": o[0] for o in ordens}

    with st.form(key="form_item"):
        ordem_id = st.selectbox("Ordem de Serviço", list(ordens_dict.keys()))
        nome_item = st.text_input("Nome do item")
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        valor_unitario = st.number_input("Valor unitário (R$)", min_value=0.0, step=1.0)
        btn_add_item = st.form_submit_button("Adicionar Item")

        if btn_add_item:
            inserir_item(conn, ordens_dict[ordem_id], nome_item, quantidade, valor_unitario)
            st.success("✅ Item adicionado!")

    st.divider()
    st.subheader("📋 Itens Cadastrados")
    itens = listar_itens(conn)
    df_itens = pd.DataFrame(itens, columns=["ID", "Ordem ID", "Nome do Item", "Quantidade", "Valor Unitário (R$)"])
    st.dataframe(df_itens, use_container_width=True)









