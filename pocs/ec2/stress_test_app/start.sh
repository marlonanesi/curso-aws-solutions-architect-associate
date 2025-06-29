#!/bin/bash

# Log de início
echo "$(date): Iniciando start.sh" >> /home/ec2-user/startup.log

# Navegar para o diretório correto
cd /home/ec2-user

# Atualizar pacotes
sudo yum update -y

# Instalar Python e ferramentas
sudo yum install -y python3 python3-pip git

# Criar e ativar ambiente virtual como ec2-user
sudo -u ec2-user python3 -m venv venv

# Instalar dependências como ec2-user
sudo -u ec2-user bash -c 'source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'

# Executar Streamlit como ec2-user (persistente)
sudo -u ec2-user bash -c 'cd /home/ec2-user && source venv/bin/activate && nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &'

# Log de conclusão
echo "$(date): Streamlit iniciado" >> /home/ec2-user/startup.log
