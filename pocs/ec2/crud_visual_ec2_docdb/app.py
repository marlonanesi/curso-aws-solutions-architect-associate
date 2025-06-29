import streamlit as st 
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

# Função para identificar a instância EC2
def get_instance_id():
    try:
        # Tentar IMDSv1 primeiro
        response = requests.get("http://169.254.169.254/latest/meta-data/instance-id", timeout=2)
        if response.status_code == 200:
            return response.text
    except:
        pass
    
    try:
        # Tentar IMDSv2
        token_response = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        if token_response.status_code == 200:
            token = token_response.text
            response = requests.get(
                "http://169.254.169.254/latest/meta-data/instance-id",
                headers={"X-aws-ec2-metadata-token": token},
                timeout=2
            )
            return response.text
    except:
        pass
    
    return "ID não disponível"


# String de conexão para o Amazon DocumentDB (via túnel local usar localhost na EC2 o endpoint)
# Aplicação base progressiva depois evoluiremos com o uso de variáveis de ambiente
# Para produção, considere usar variáveis de ambiente ou serviços de gerenciamento de segredos
MONGO_URI = (
    "mongodb://userlab:docdb2025@docdb-condominio.cluster-ctk6u26y28ic.sa-east-1.docdb.amazonaws.com:27017/"
    "?tls=true"
    "&tlsCAFile=./global-bundle.pem"
    "&tlsAllowInvalidHostnames=true"
    "&readPreference=secondaryPreferred"
    "&retryWrites=false"
    "&directConnection=true"
)

# Conexão com o DocumentDB
client = MongoClient(MONGO_URI)
db = client["meu_querido_docdb"]
collection = db["pessoas"]

# Interface Streamlit
st.set_page_config(page_title="CRUD DocumentDB", layout="centered")
st.title("📝 CRUD com Amazon DocumentDB + Streamlit")

# Mostrar ID da instância EC2
instance_id = get_instance_id()
st.markdown(f"🖥️ **Instância EC2**: `{instance_id}`")

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
