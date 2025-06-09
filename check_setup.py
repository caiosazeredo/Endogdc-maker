# check_setup.py - Verificação de Configuração
import os
import sys
import requests
from config import Config

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} - Versão muito antiga!")
        print("   Necessário Python 3.8 ou superior")
        return False

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_migrate', 
        'pymysql', 'requests', 'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✓ {package} - Instalado")
        except ImportError:
            print(f"   ✗ {package} - NÃO instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   Para instalar as dependências faltantes:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_database_connection():
    """Verifica conexão com o banco de dados"""
    print("\n🗄️  Verificando conexão com o banco de dados...")
    
    try:
        import pymysql
        
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            ssl_disabled=False
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        connection.close()
        
        print(f"   ✓ Conexão com MySQL - OK")
        print(f"   ✓ Host: {Config.MYSQL_HOST}")
        print(f"   ✓ Database: {Config.MYSQL_DATABASE}")
        return True
        
    except Exception as e:
        print(f"   ✗ Erro na conexão com MySQL: {e}")
        return False

def check_groq_api():
    """Verifica se a API do Groq está configurada"""
    print("\n🤖 Verificando configuração da API Groq...")
    
    api_key = os.environ.get('GROQ_API_KEY') or Config.GROQ_API_KEY
    
    if not api_key or api_key == 'your-groq-api-key-here':
        print("   ✗ Chave da API Groq não configurada")
        print("   Configure a variável GROQ_API_KEY no arquivo .env")
        return False
    
    # Testar a API
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'max_tokens': 10
        }
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✓ API Groq - OK")
            print("   ✓ Chave de API válida")
            print(f"   ✓ Modelo: {Config.GROQ_MODEL}")
            return True
        else:
            print(f"   ✗ Erro na API Groq: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Erro ao testar API Groq: {e}")
        return False

def check_gemini_api():
    """Verifica se a API do Gemini está configurada"""
    print("\n🧠 Verificando configuração da API Gemini...")
    
    api_key = os.environ.get('GEMINI_API_KEY') or Config.GEMINI_API_KEY
    
    if not api_key or api_key == 'your-gemini-api-key-here':
        print("   ✗ Chave da API Gemini não configurada")
        print("   Configure a variável GEMINI_API_KEY no arquivo .env")
        return False
    
    # Testar a API
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Hello"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 10,
                "temperature": 0.7
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("   ✓ API Gemini - OK")
            print("   ✓ Chave de API válida")
            print(f"   ✓ Modelo: {Config.GEMINI_MODEL}")
            return True
        else:
            print(f"   ✗ Erro na API Gemini: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Erro ao testar API Gemini: {e}")
        return False

def check_flask_config():
    """Verifica configurações do Flask"""
    print("\n⚡ Verificando configurações do Flask...")
    
    if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
        print("   ⚠️  SECRET_KEY usando valor padrão (OK para desenvolvimento)")
    else:
        print("   ✓ SECRET_KEY configurada")
    
    print(f"   ✓ Modelo Groq: {Config.GROQ_MODEL}")
    
    return True

def main():
    """Função principal de verificação"""
    print("🔍 VERIFICAÇÃO DE CONFIGURAÇÃO DO SISTEMA")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_database_connection(),
        check_groq_api(),
        check_gemini_api(),
        check_flask_config()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        print("   O sistema está pronto para uso.")
        print("   Execute: python run.py")
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM!")
        print("   Corrija os problemas acima antes de executar o sistema.")
    
    print("=" * 50)

if __name__ == '__main__':
    main()