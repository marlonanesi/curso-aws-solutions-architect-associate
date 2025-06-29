# Caso não possua a lib pymongo, instale com: pip install pymongo
# Para subir uma instância do MongoDB com Docker, use: docker run --name aula_mongo -d -p 27017:27017 mongo
from pymongo import MongoClient

# String de conexão para o Amazon DocumentDB
MONGO_URI = (
    "mongodb://userlab:docdb2025@localhost:27017/"
    "?tls=true"
    "&tlsCAFile=./global-bundle.pem"
    "&tlsAllowInvalidHostnames=true"
    "&readPreference=secondaryPreferred"
    "&retryWrites=false"
    "&directConnection=true"

)


# Conectar ao DocumentDB (certificado deve estar na mesma pasta do carga.py)
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,  # 5 segundos para seleção do servidor
    connectTimeoutMS=5000           # 5 segundos para conexão TCP
)
db = client['aula_mongodb']
collection = db['alunos']

# Testar a conexão com o DocumentDB
try:
    # Tenta listar os bancos de dados para testar a conexão
    print("Testando conexão com o DocumentDB...")
    print(client.list_database_names())
    print("✅ Conexão estabelecida com sucesso!")
except Exception as e:
    print("❌ Falha ao conectar no DocumentDB:")
    print(e)
    exit(1)

# Lista de dicionários com objetos mockados (pessoas)
pessoas = [
    {
        "nome": "Alice",
        "idade": 30,
        "cidade": "São Paulo",
        "email": "alice@example.com",
        "telefone": "11987654321",
        "endereco": {
            "rua": "Av. Paulista",
            "numero": 1000,
            "bairro": "Bela Vista",
            "cep": "01310-000"
        },
        "cursos": ["Python", "Data Science"]
    },
    {
        "nome": "Bob",
        "idade": 25,
        "cidade": "Rio de Janeiro",
        "email": "bob@example.com",
        "telefone": "21987654321",
        "UB": True,
        "endereco": {
            "rua": "Rua das Flores",
            "numero": 200,
            "bairro": "Centro",
            "cep": "20000-000"
        },
        "cursos": ["Java", "Spring Boot"]
    },
    {
        "nome": "Carol",
        "idade": 27,
        "cidade": "Belo Horizonte",
        "email": "carol@example.com",
        "telefone": "31987654321",
        "endereco": {
            "rua": "Av. Afonso Pena",
            "numero": 300,
            "bairro": "Centro",
            "cep": "30130-000"
        },
        "cursos": ["JavaScript", "React"]
    },
    {
        "nome": "David",
        "idade": 35,
        "cidade": "Curitiba",
        "email": "david@example.com",
        "telefone": "41987654321",
        "endereco": {
            "rua": "Rua XV de Novembro",
            "numero": 400,
            "bairro": "Centro",
            "cep": "80020-310"
        },
        "cursos": ["C#", ".NET"]
    },
    {
        "nome": "Eve",
        "idade": 22,
        "cidade": "Porto Alegre",
        "email": "eve@example.com",
        "telefone": "51987654321",
        "endereco": {
            "rua": "Av. Ipiranga",
            "numero": 500,
            "bairro": "Partenon",
            "cep": "90610-000"
        },
        "cursos": ["Ruby", "Rails"]
    }
]

# Inserir os documentos na coleção
result = collection.insert_many(pessoas)

# Exibir os IDs dos documentos inseridos
print(f'Documentos inseridos com os IDs: {result.inserted_ids}')