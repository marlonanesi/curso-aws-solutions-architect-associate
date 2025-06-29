import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

# String de conexão para o Amazon DocumentDB (via túnel local)
MONGO_URI = (
    "mongodb://userlab:docdb2025@localhost:27017/"
    "?tls=true"
    "&tlsCAFile=./global-bundle.pem"
    "&tlsAllowInvalidHostnames=true"
    "&readPreference=secondaryPreferred"
    "&retryWrites=false"
    "&directConnection=true"
)

# Conexão com o DocumentDB
client = MongoClient(MONGO_URI)
db = client["meubanco"]
collection = db["pessoas"]

st.set_page_config(page_title="CRUD DocumentDB", layout="centered")

st.title("📝 CRUD com Amazon DocumentDB + Streamlit")

# Inserção (Create)
st.header("➕ Inserir novo documento")
nome = st.text_input("Nome")
idade = st.number_input("Idade", min_value=0, step=1)

if st.button("Inserir"):
    if nome:
        collection.insert_one({"nome": nome, "idade": idade})
        st.success(f"Documento inserido: {nome}, {idade} anos")
        st.rerun()
    else:
        st.warning("Preencha o nome para inserir.")

st.divider()

# Leitura (Read)
st.header("📋 Documentos existentes")
docs = list(collection.find())
if docs:
    for doc in docs:
        st.write(f"🆔 {doc['_id']} | Nome: {doc.get('nome','')} | Idade: {doc.get('idade','')}")
else:
    st.info("Nenhum documento encontrado.")

st.divider()

# Atualização (Update)
st.header("✏️ Atualizar documento")
id_update = st.text_input("ID do documento para atualizar")
novo_nome = st.text_input("Novo nome")
nova_idade = st.number_input("Nova idade", min_value=0, step=1, key="nova_idade")

if st.button("Atualizar"):
    if id_update and novo_nome:
        try:
            result = collection.update_one(
                {"_id": ObjectId(id_update.strip())},
                {"$set": {"nome": novo_nome, "idade": nova_idade}}
            )
            if result.matched_count:
                st.success("Documento atualizado com sucesso!")
                st.rerun()
            else:
                st.warning("ID não encontrado.")
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Preencha o ID e o novo nome.")

st.divider()

# Exclusão (Delete)
st.header("🗑️ Deletar documento")
id_delete = st.text_input("ID do documento para deletar")

if st.button("Deletar"):
    if id_delete:
        try:
            result = collection.delete_one({"_id": ObjectId(id_delete.strip())})
            if result.deleted_count:
                st.success("Documento deletado com sucesso!")
                st.rerun()
            else:
                st.warning("ID não encontrado.")
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Preencha o ID para deletar.")
