# run.py - Script de Execução
import os
from app import create_app
from extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Criar tabelas se não existirem
        try:
            db.create_all()
            print("Banco de dados inicializado com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
    
    # Configurações de execução
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print(f"Iniciando aplicação em http://{host}:{port}")
    print("Pressione Ctrl+C para parar")
    
    app.run(
        debug=debug_mode,
        host=host,
        port=port
    )