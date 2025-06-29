from dotenv import load_dotenv
import os

def str2bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")

# Carregar variáveis de ambiente do arquivo .env, caso não possua, criar um arquivo .env com a chave API_KEY
load_dotenv()

API_KEY = os.getenv('API_KEY')
MODO_LOCAL = str2bool(os.getenv('MODO_LOCAL', False))  # Altere para False para usar a API OpenAI
HABILITAR_LOGIN = str2bool(os.getenv('HABILITAR_LOGIN', False))  # Altere para True para habilitar o login
NOTIFICACOES_HABILITADAS = str2bool(os.getenv('NOTIFICACOES_HABILITADAS', False))  # Altere para True para habilitar notificações
MINHAS_MENSAGENS_HABILITADAS = str2bool(os.getenv('MINHAS_MENSAGENS_HABILITADAS', False))  # Altere para True para habilitar mensagens personalizadas

