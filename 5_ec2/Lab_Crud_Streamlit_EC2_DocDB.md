## ⚠️ AVISO: Este não é um passo a passo exato (fatores ambientais, mudanças da console podem ocorrer). Portanto use-o como referência técnica para a solução.
## 💡 Visão Macro e Solução: A AWS espera que um Arquiteto de Soluções concentre-se no conceito e nas nuances dos serviços, não na memorização de detalhes!
#
# 🔧 Lab Final: CRUD Visual com Streamlit + Amazon DocumentDB

## 🎯 Objetivo

Desenvolver uma aplicação web completa usando Streamlit para operações CRUD (Create, Read, Update, Delete) conectada ao Amazon DocumentDB, demonstrando integração entre EC2, DocumentDB e desenvolvimento de aplicações web na AWS. **Nível: Avançado**.

## 💰 Custos e Cuidados

> 💡 **Free Tier - Contas Anteriores a 15/07/2025:**
> DocumentDB NÃO está no Free Tier. Custo mínimo: ~$200/mês por cluster.
>
> 💡 **Free Tier - Contas Posteriores a 15/07/2025:**
> Estimativa: custo ALTO para DocumentDB ($200+/mês). Este lab é conceitual/opcional. Se implementar, termine recursos imediatamente após teste para evitar extrapolar créditos do novo free tier
>
> **⚠️ Cuidados importantes:**
> * DocumentDB tem custo mínimo alto (cluster mínimo ~$200/mês)
> * Instância EC2 adicional para desenvolvimento
> * Transferência de dados entre serviços
> * Sempre **delete cluster DocumentDB** imediatamente após o lab
> * Este lab pode ser feito de forma CONCEITUAL sem criar recursos reais

## ⭐ Passos a Executar

### 1. Entender Arquitetura da Solução

**Componentes da aplicação:**
- **Amazon DocumentDB**: Database NoSQL MongoDB-compatível
- **EC2 Instance**: Servidor de aplicação Streamlit
- **Streamlit**: Framework Python para aplicações web
- **SSH Tunnel**: Conexão segura EC2 → DocumentDB
- **Security Groups**: Controle de acesso entre componentes

**Fluxo de dados:**
```
[User Browser] → [EC2:8501 Streamlit] → [DocumentDB:27017] → [Data Storage]
                      ↑
                [SSH Tunnel para segurança]
```

**Analogias para facilitar o entendimento:**
- **Streamlit**: Como criar um site sem saber HTML/CSS
- **DocumentDB**: Como MongoDB na nuvem, mas gerenciado pela AWS
- **SSH Tunnel**: Como um túnel privado entre dois pontos
- **CRUD**: Create (criar), Read (ler), Update (atualizar), Delete (deletar)

### 2. Preparar Ambiente de Desenvolvimento (Conceitual)

**Se fosse implementar realmente (CARO - não recomendado):**

1. **Criar DocumentDB Cluster**:
   - **Engine**: MongoDB 4.0 compatível
   - **Instance class**: db.t3.medium (mínimo)
   - **Cluster size**: 1 instância
   - **Username**: `admin`
   - **Password**: Senha segura
   - **VPC**: Sua VPC existente
   - **Subnet group**: Private subnets

2. **Security Groups necessários**:
   - **SG DocumentDB**: Port 27017 from EC2 security group
   - **SG EC2**: Port 22 (SSH), Port 8501 (Streamlit)

### 3. Desenvolver Aplicação Streamlit

**Estrutura do projeto:**
```
crud_streamlit/
├── app.py                  # Aplicação principal Streamlit
├── requirements.txt        # Dependências Python
├── database.py            # Módulo de conexão DocumentDB
├── models.py              # Modelos de dados
├── global-bundle.pem      # Certificado TLS DocumentDB
└── setup.sh               # Script de instalação
```

**1. Criar requirements.txt:**
```txt
streamlit==1.25.0
pymongo==4.4.1
pandas==2.0.3
python-dotenv==1.0.0
dnspython==2.3.0
```

**2. Criar database.py:**
```python
import pymongo
import ssl
import os
from urllib.parse import quote_plus

class DocumentDBConnection:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self, host, port, username, password, database_name):
        """Conecta ao Amazon DocumentDB"""
        try:
            # URL de conexão para DocumentDB
            connection_string = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/{database_name}?ssl=true&ssl_ca_certs=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
            
            # Criar cliente MongoDB
            self.client = pymongo.MongoClient(connection_string)
            self.db = self.client[database_name]
            
            # Testar conexão
            self.client.admin.command('ismaster')
            print("✅ Conectado ao DocumentDB com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar ao DocumentDB: {e}")
            return False
    
    def get_database(self):
        """Retorna instância do database"""
        return self.db
    
    def close(self):
        """Fecha conexão"""
        if self.client:
            self.client.close()
```

**3. Criar models.py:**
```python
from datetime import datetime
import streamlit as st

class UserModel:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, name, email, age, city):
        """Criar novo usuário"""
        user = {
            "name": name,
            "email": email,
            "age": age,
            "city": city,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        try:
            result = self.collection.insert_one(user)
            return str(result.inserted_id)
        except Exception as e:
            st.error(f"Erro ao criar usuário: {e}")
            return None
    
    def get_all_users(self):
        """Buscar todos os usuários"""
        try:
            users = list(self.collection.find())
            return users
        except Exception as e:
            st.error(f"Erro ao buscar usuários: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        """Buscar usuário por ID"""
        try:
            from bson import ObjectId
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception as e:
            st.error(f"Erro ao buscar usuário: {e}")
            return None
    
    def update_user(self, user_id, name, email, age, city):
        """Atualizar usuário"""
        try:
            from bson import ObjectId
            update_data = {
                "name": name,
                "email": email,
                "age": age,
                "city": city,
                "updated_at": datetime.now()
            }
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Erro ao atualizar usuário: {e}")
            return False
    
    def delete_user(self, user_id):
        """Deletar usuário"""
        try:
            from bson import ObjectId
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Erro ao deletar usuário: {e}")
            return False
    
    def search_users(self, search_term):
        """Buscar usuários por termo"""
        try:
            query = {
                "$or": [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}},
                    {"city": {"$regex": search_term, "$options": "i"}}
                ]
            }
            users = list(self.collection.find(query))
            return users
        except Exception as e:
            st.error(f"Erro na busca: {e}")
            return []
```

**4. Criar app.py (aplicação principal):**
```python
import streamlit as st
import pandas as pd
from database import DocumentDBConnection
from models import UserModel
import os

# Configuração da página
st.set_page_config(
    page_title="CRUD DocumentDB",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🗄️ Sistema CRUD com Amazon DocumentDB")
st.markdown("---")

# Sidebar para configuração
st.sidebar.header("⚙️ Configuração de Conexão")

# Variáveis de conexão (em produção, usar variáveis de ambiente)
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False

# Formulário de conexão
with st.sidebar.form("connection_form"):
    host = st.text_input("Host DocumentDB", 
                         value="docdb-cluster.cluster-xxx.docdb.amazonaws.com")
    port = st.number_input("Porta", value=27017)
    username = st.text_input("Usuário", value="admin")
    password = st.text_input("Senha", type="password")
    database_name = st.text_input("Nome do Database", value="crud_app")
    
    connect_button = st.form_submit_button("🔌 Conectar")

# Gerenciar conexão
if connect_button:
    with st.spinner("Conectando ao DocumentDB..."):
        db_conn = DocumentDBConnection()
        if db_conn.connect(host, port, username, password, database_name):
            st.session_state.db_connected = True
            st.session_state.db_conn = db_conn
            st.session_state.user_model = UserModel(db_conn.get_database())
            st.sidebar.success("✅ Conectado com sucesso!")
        else:
            st.sidebar.error("❌ Falha na conexão")

# Interface principal
if st.session_state.db_connected:
    # Tabs para diferentes operações
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Criar", "📋 Listar", "🔍 Buscar", "✏️ Editar", "🗑️ Deletar"])
    
    # CREATE - Criar usuário
    with tab1:
        st.header("➕ Criar Novo Usuário")
        
        with st.form("create_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome completo")
                email = st.text_input("Email")
            
            with col2:
                age = st.number_input("Idade", min_value=1, max_value=120, value=25)
                city = st.text_input("Cidade")
            
            submit_create = st.form_submit_button("➕ Criar Usuário")
            
            if submit_create:
                if name and email and city:
                    user_id = st.session_state.user_model.create_user(name, email, age, city)
                    if user_id:
                        st.success(f"✅ Usuário criado com sucesso! ID: {user_id}")
                        st.balloons()
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios")
    
    # READ - Listar usuários
    with tab2:
        st.header("📋 Lista de Usuários")
        
        if st.button("🔄 Atualizar Lista"):
            users = st.session_state.user_model.get_all_users()
            
            if users:
                # Converter para DataFrame para exibição
                df_users = pd.DataFrame(users)
                df_users['_id'] = df_users['_id'].astype(str)
                
                # Reorganizar colunas
                columns_order = ['_id', 'name', 'email', 'age', 'city', 'created_at', 'updated_at']
                df_users = df_users[columns_order]
                
                st.dataframe(df_users, use_container_width=True)
                st.info(f"📊 Total de usuários: {len(users)}")
            else:
                st.warning("⚠️ Nenhum usuário encontrado")
    
    # SEARCH - Buscar usuários
    with tab3:
        st.header("🔍 Buscar Usuários")
        
        search_term = st.text_input("Digite o termo de busca (nome, email ou cidade)")
        
        if st.button("🔍 Buscar"):
            if search_term:
                users = st.session_state.user_model.search_users(search_term)
                
                if users:
                    df_users = pd.DataFrame(users)
                    df_users['_id'] = df_users['_id'].astype(str)
                    st.dataframe(df_users, use_container_width=True)
                    st.success(f"✅ Encontrados {len(users)} usuários")
                else:
                    st.warning("⚠️ Nenhum usuário encontrado com esse termo")
            else:
                st.error("❌ Digite um termo para busca")
    
    # UPDATE - Editar usuário
    with tab4:
        st.header("✏️ Editar Usuário")
        
        # Selecionar usuário para editar
        users = st.session_state.user_model.get_all_users()
        
        if users:
            user_options = {f"{user['name']} ({user['email']})": str(user['_id']) for user in users}
            selected_user = st.selectbox("Selecione o usuário para editar", options=list(user_options.keys()))
            
            if selected_user:
                user_id = user_options[selected_user]
                user_data = st.session_state.user_model.get_user_by_id(user_id)
                
                if user_data:
                    with st.form("edit_user"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            name = st.text_input("Nome completo", value=user_data['name'])
                            email = st.text_input("Email", value=user_data['email'])
                        
                        with col2:
                            age = st.number_input("Idade", min_value=1, max_value=120, value=user_data['age'])
                            city = st.text_input("Cidade", value=user_data['city'])
                        
                        submit_update = st.form_submit_button("✏️ Atualizar Usuário")
                        
                        if submit_update:
                            if name and email and city:
                                success = st.session_state.user_model.update_user(user_id, name, email, age, city)
                                if success:
                                    st.success("✅ Usuário atualizado com sucesso!")
                                    st.rerun()
                            else:
                                st.error("❌ Por favor, preencha todos os campos")
        else:
            st.warning("⚠️ Nenhum usuário disponível para edição")
    
    # DELETE - Deletar usuário
    with tab5:
        st.header("🗑️ Deletar Usuário")
        
        users = st.session_state.user_model.get_all_users()
        
        if users:
            user_options = {f"{user['name']} ({user['email']})": str(user['_id']) for user in users}
            selected_user = st.selectbox("Selecione o usuário para deletar", options=list(user_options.keys()), key="delete_select")
            
            if selected_user:
                user_id = user_options[selected_user]
                user_data = st.session_state.user_model.get_user_by_id(user_id)
                
                if user_data:
                    st.warning("⚠️ **ATENÇÃO**: Esta ação não pode ser desfeita!")
                    
                    # Mostrar dados do usuário
                    st.json({
                        "Nome": user_data['name'],
                        "Email": user_data['email'],
                        "Idade": user_data['age'],
                        "Cidade": user_data['city']
                    })
                    
                    confirm = st.checkbox("Confirmo que desejo deletar este usuário")
                    
                    if st.button("🗑️ Deletar Usuário", type="secondary"):
                        if confirm:
                            success = st.session_state.user_model.delete_user(user_id)
                            if success:
                                st.success("✅ Usuário deletado com sucesso!")
                                st.rerun()
                        else:
                            st.error("❌ Por favor, confirme a exclusão")
        else:
            st.warning("⚠️ Nenhum usuário disponível para exclusão")

else:
    st.warning("⚠️ Configure a conexão com o DocumentDB na barra lateral para começar")
    
    # Informações sobre DocumentDB
    st.info("""
    **📋 Sobre este lab:**
    
    Esta aplicação demonstra operações CRUD (Create, Read, Update, Delete) 
    conectando-se ao Amazon DocumentDB através de uma instância EC2.
    
    **🔧 Componentes:**
    - Amazon DocumentDB (MongoDB compatível)
    - EC2 Instance (servidor de aplicação)
    - Streamlit (interface web)
    - PyMongo (driver de conexão)
    """)

# Footer
st.markdown("---")
st.markdown("**🏗️ Lab AWS Solutions Architect Associate** | Desenvolvido com Streamlit + DocumentDB")
```

**5. Criar setup.sh:**
```bash
#!/bin/bash

echo "🚀 Configurando ambiente para aplicação Streamlit + DocumentDB"

# Atualizar sistema
sudo yum update -y

# Instalar Python 3 e pip
sudo yum install -y python3 python3-pip

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar diretório para logs
mkdir -p logs

echo "✅ Ambiente configurado com sucesso!"
echo "📋 Para executar:"
echo "   source venv/bin/activate"
echo "   streamlit run app.py --server.port=8501 --server.address=0.0.0.0"
```

### 4. Implementação Conceitual (Sem Custos)

**Como seria o fluxo completo se implementássemos:**

1. **Upload dos arquivos para EC2:**
   ```bash
   # Compactar projeto
   zip -r crud_streamlit.zip app.py requirements.txt database.py models.py setup.sh global-bundle.pem
   
   # Enviar para EC2
   scp -i sua-chave.pem crud_streamlit.zip ec2-user@ip-publico-ec2:/home/ec2-user/
   ```

2. **Configuração na instância EC2:**
   ```bash
   # Conectar via SSH
   ssh -i sua-chave.pem ec2-user@ip-publico-ec2
   
   # Descompactar e configurar
   unzip crud_streamlit.zip
   chmod +x setup.sh
   ./setup.sh
   
   # Ativar ambiente virtual
   source venv/bin/activate
   
   # Executar aplicação
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

3. **Acesso à aplicação:**
   - Configurar Security Group: porta 8501 liberada
   - Acessar: `http://ip-publico-ec2:8501`

### 5. Configurar Túnel SSH para DocumentDB

**Para conexão segura ao DocumentDB:**

```bash
# Na instância EC2, criar túnel SSH
ssh -i sua-chave.pem -L 27017:docdb-cluster.cluster-xxx.amazonaws.com:27017 ec2-user@ip-publico-ec2

# Ou usar Session Manager para túnel sem SSH
aws ssm start-session --target i-1234567890abcdef0 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["27017"],"localPortNumber":["27017"]}'
```

### 6. Funcionalidades da Aplicação

**Operações CRUD implementadas:**

1. **CREATE**: Formulário para criar novos usuários
2. **READ**: Lista paginada de todos os usuários
3. **UPDATE**: Edição de usuários existentes
4. **DELETE**: Remoção com confirmação
5. **SEARCH**: Busca por nome, email ou cidade

**Recursos adicionais:**
- Interface responsiva com Streamlit
- Validação de dados
- Tratamento de erros
- Conexão segura com TLS
- Visualização em tabelas
- Feedback visual (success/error messages)

### 7. Monitoramento e Troubleshooting

**Logs da aplicação:**
```bash
# Executar com logs detalhados
streamlit run app.py --logger.level debug

# Verificar logs do sistema
tail -f /var/log/messages

# Monitorar conexões DocumentDB
netstat -an | grep 27017
```

**Problemas comuns:**
- **Conexão**: Verificar Security Groups
- **Certificado**: Garantir que global-bundle.pem está presente
- **Performance**: Monitorar uso de CPU/memória
- **Rede**: Verificar conectividade EC2 ↔ DocumentDB

### 8. Otimizações de Produção

**Melhorias para ambiente real:**

1. **Segurança:**
   ```bash
   # Usar variáveis de ambiente
   export DOCDB_HOST="cluster.docdb.amazonaws.com"
   export DOCDB_USER="admin"
   export DOCDB_PASS="password_segura"
   ```

2. **Performance:**
   ```python
   # Connection pooling
   client = pymongo.MongoClient(connection_string, maxPoolSize=50)
   
   # Indexes para busca
   collection.create_index([("name", "text"), ("email", "text")])
   ```

3. **Escalabilidade:**
   ```bash
   # Load balancer para múltiplas instâncias
   # Auto Scaling Groups
   # Cache com ElastiCache
   ```

### 9. Configurar como Serviço Systemd

**Para execução automática:**

```bash
# Criar arquivo de serviço
sudo tee /etc/systemd/system/streamlit-app.service << 'EOF'
[Unit]
Description=Streamlit CRUD App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user
Environment=PATH=/home/ec2-user/venv/bin
ExecStart=/home/ec2-user/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar serviço
sudo systemctl enable streamlit-app
sudo systemctl start streamlit-app
sudo systemctl status streamlit-app
```

### 10. Limpeza de Recursos (IMPORTANTE)

**Se implementou recursos reais:**

1. **Pare a aplicação:**
   ```bash
   sudo systemctl stop streamlit-app
   sudo systemctl disable streamlit-app
   ```

2. **Delete cluster DocumentDB:**
   - Console DocumentDB > Clusters
   - Delete cluster (CRÍTICO - economiza $200+/mês)

3. **Termine instância EC2:**
   - EC2 > Instances > Terminate

4. **Limpe Security Groups:**
   - Delete security groups criados para o lab

## ✅ Conclusão

Você dominou o desenvolvimento de aplicações web completas na AWS:

**✅ Checklist de Conquistas:**
- [ ] Arquitetura de aplicação web com DocumentDB compreendida
- [ ] Aplicação Streamlit com CRUD completo desenvolvida
- [ ] Conexão segura EC2 ↔ DocumentDB configurada
- [ ] Interface de usuário responsiva criada
- [ ] Operações CRUD (Create, Read, Update, Delete) implementadas
- [ ] Tratamento de erros e validação de dados aplicados
- [ ] Túnel SSH para segurança configurado
- [ ] Serviço systemd para produção preparado
- [ ] Considerações de custos analisadas (DocumentDB é caro!)
- [ ] Recursos limpos para evitar cobranças altas

**🎓 Conceitos Reforçados:**
* **Full-stack development**: Frontend + Backend + Database na AWS
* **DocumentDB integration**: NoSQL MongoDB-compatível gerenciado
* **Streamlit framework**: Desenvolvimento rápido de interfaces web
* **SSH tunneling**: Conexões seguras para databases
* **CRUD operations**: Operações fundamentais de banco de dados
* **Cost awareness**: DocumentDB tem custos altos, planejar adequadamente
