# config.py - Configuração da Aplicação
import os
from datetime import timedelta

class Config:
    # Configuração básica
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    
    # Configuração do banco MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
    
    # Validação das variáveis MySQL obrigatórias
    required_mysql_vars = [MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]
    if not all(required_mysql_vars):
        raise ValueError("MySQL environment variables are required: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE")
    
    # String de conexão completa
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?ssl_ca=&ssl_disabled=False'
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
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # Configuração Gemini
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
    
    # Validação das APIs (opcional - remova se não quiser validação obrigatória)
    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY not set")
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set")