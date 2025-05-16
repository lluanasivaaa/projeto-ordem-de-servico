import streamlit as st
from db_connection import (
    listar_clientes, listar_ordens, inserir_cliente,
    listar_servicos, inserir_servico,
    listar_itens, inserir_item
)
import re
import datetime

def main(conexao):
    def validar_email(email):
        padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(padrao, email) is not None

    st.title("🔧 Sistema de Ordem de Serviço e Orçamento")

    # --- Cadastro cliente ---
    with st.sidebar.form("form_novo_cliente", clear_on_submit=True):
        st.subheader("Cadastrar novo cliente")
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        salvar_cliente = st.form_submit_button("Salvar")

        if salvar_cliente:
            if not nome.strip():
                st.warning("Nome é obrigatório.")
            elif not email.strip():
                st.warning("Email é obrigatório.")
            elif not validar_email(email):
                st.warning("Email inválido.")
            elif not telefone.strip():
                st.warning("Telefone é obrigatório.")
            else:
                inserir_cliente(conexao, nome, email, telefone)
                st.success("✅ Cliente cadastrado com sucesso!")

    # --- Listar clientes ---
    st.subheader("📋 Clientes cadastrados")
    clientes = listar_clientes(conexao)
    if clientes:
        st.dataframe(clientes, use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado.")

    # --- Cadastro ordem ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cadastrar nova ordem de serviço")

    with st.sidebar.form("form_nova_ordem", clear_on_submit=True):
        if clientes:
            opcoes_clientes = {f"{c[1]} (ID: {c[0]})": c[0] for c in clientes}
            cliente_selecionado = st.selectbox("Cliente", list(opcoes_clientes.keys()))
            cliente_id = opcoes_clientes[cliente_selecionado]

            data_abertura = st.date_input("Data de Abertura", datetime.date.today())
            status = st.selectbox("Status", ["Aberta", "Em andamento", "Fechada"])

            salvar_ordem = st.form_submit_button("Salvar ordem")

            if salvar_ordem:
                try:
                    cursor = conexao.cursor()
                    query = "INSERT INTO ordens (cliente_id, data_abertura, status, total) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (cliente_id, data_abertura, status, 0.0))
                    conexao.commit()
                    st.sidebar.success("✅ Ordem de serviço cadastrada com sucesso!")
                    cursor.close()
                except Exception as e:
                    st.sidebar.error(f"Erro ao cadastrar ordem: {e}")
        else:
            st.sidebar.warning("⚠️ Nenhum cliente cadastrado para associar à ordem.")

    # --- Listar ordens ---
    st.subheader("📝 Ordens de Serviço cadastradas")
    ordens = listar_ordens(conexao)
    if ordens:
        st.dataframe(ordens, use_container_width=True)
    else:
        st.info("Nenhuma ordem de serviço cadastrada.")

    # --- Cadastro serviços vinculados à ordem ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cadastrar serviço na ordem")

    with st.sidebar.form("form_novo_servico", clear_on_submit=True):
        ordens = listar_ordens(conexao)
        if ordens:
            opcoes_ordens = {f"Ordem ID {o[0]} - Cliente ID {o[1]}": o[0] for o in ordens}
            ordem_selecionada = st.selectbox("Selecione a ordem", list(opcoes_ordens.keys()))
            ordem_id = opcoes_ordens[ordem_selecionada]

            descricao_servico = st.text_input("Descrição do serviço")
            valor_servico = st.number_input("Valor do serviço", min_value=0.0, format="%.2f")

            salvar_servico = st.form_submit_button("Salvar serviço")

            if salvar_servico:
                if not descricao_servico.strip():
                    st.warning("Descrição do serviço é obrigatória.")
                elif valor_servico <= 0:
                    st.warning("Valor do serviço deve ser maior que zero.")
                else:
                    try:
                        inserir_servico(conexao, ordem_id, descricao_servico, valor_servico)
                        st.sidebar.success("✅ Serviço cadastrado com sucesso!")
                    except Exception as e:
                        st.sidebar.error(f"Erro ao cadastrar serviço: {e}")
        else:
            st.sidebar.warning("⚠️ Nenhuma ordem cadastrada para adicionar serviços.")

    # --- Cadastro itens vinculados à ordem ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cadastrar item na ordem")

    with st.sidebar.form("form_novo_item", clear_on_submit=True):
        ordens = listar_ordens(conexao)
        if ordens:
            opcoes_ordens = {f"Ordem ID {o[0]} - Cliente ID {o[1]}": o[0] for o in ordens}
            ordem_selecionada = st.selectbox("Selecione a ordem para item", list(opcoes_ordens.keys()), key="ordem_item")
            ordem_id = opcoes_ordens[ordem_selecionada]

            descricao_item = st.text_input("Descrição do item", key="descricao_item")
            valor_item = st.number_input("Valor do item", min_value=0.0, format="%.2f", key="valor_item")

            salvar_item = st.form_submit_button("Salvar item")

            if salvar_item:
                if not descricao_item.strip():
                    st.warning("Descrição do item é obrigatória.")
                elif valor_item <= 0:
                    st.warning("Valor do item deve ser maior que zero.")
                else:
                    try:
                        inserir_item(conexao, ordem_id, descricao_item, valor_item)
                        st.sidebar.success("✅ Item cadastrado com sucesso!")
                    except Exception as e:
                        st.sidebar.error(f"Erro ao cadastrar item: {e}")
        else:
            st.sidebar.warning("⚠️ Nenhuma ordem cadastrada para adicionar itens.")

    # --- Listar serviços ---
    st.subheader("🛠️ Serviços cadastrados")
    servicos = listar_servicos(conexao)
    if servicos:
        st.dataframe(servicos, use_container_width=True)
    else:
        st.info("Nenhum serviço cadastrado.")

    # --- Listar itens ---
    st.subheader("📦 Itens cadastrados")
    itens = listar_itens(conexao)
    if itens:
        st.dataframe(itens, use_container_width=True)
    else:
        st.info("Nenhum item cadastrado.")
