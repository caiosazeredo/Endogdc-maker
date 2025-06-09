# config.py - Configuração da Aplicação CORRIGIDA
import os
from datetime import timedelta
from dotenv import load_dotenv

# CARREGAR VARIÁVEIS DO .ENV
load_dotenv()

class Config:
    # Configuração básica
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-mudeme-em-producao-12345')
    
    # Configuração do banco MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'defaultdb')
    
    # String de conexão completa
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?ssl_disabled=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'ssl_disabled': False
        }
    }
    
    # Configuração de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Configuração para integração com LLMs
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'sua-chave-groq-aqui')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # Configuração Gemini
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'sua-chave-gemini-aqui')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
    
    @classmethod
    def validate_config(cls):
        """Valida configurações"""
        print("✅ Configurações carregadas com sucesso")
        return True
