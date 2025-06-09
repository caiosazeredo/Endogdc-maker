# app.py - Aplicação Principal Flask Atualizada (raiz do projeto)
from flask import Flask
from config import Config
from extensions import db, migrate

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos (necessário para migrations)
    from models import (
        BrainstormSession, Card, SocraticSessionAnswers, 
        BloomTaxonomyLevel, BloomObjective, GdcTemplate, 
        GdcSection, GdcNote, GroqResponse
    )
    
    # Registrar blueprints
    try:
        from routes.home import home_bp
        app.register_blueprint(home_bp)
    except ImportError:
        print("⚠️  routes.home não encontrado - criando rota básica")
        
        @app.route('/')
        def index():
            return '''
            <h1>🎮 Endo-GDC Maker</h1>
            <p>Sistema funcionando! Configure as rotas para funcionalidade completa.</p>
            <p><a href="/health">Verificar saúde do sistema</a></p>
            '''
    
    try:
        from routes.brainstorm import brainstorm_bp
        app.register_blueprint(brainstorm_bp, url_prefix='/brainstorm')
    except ImportError:
        print("⚠️  routes.brainstorm não encontrado")
    
    try:
        from routes.socratic import socratic_bp
        app.register_blueprint(socratic_bp, url_prefix='/socratic')
    except ImportError:
        print("⚠️  routes.socratic não encontrado")
    
    try:
        from routes.bloom import bloom_bp
        app.register_blueprint(bloom_bp, url_prefix='/bloom')
    except ImportError:
        print("⚠️  routes.bloom não encontrado")
    
    try:
        from routes.gamedesign import gamedesign_bp
        app.register_blueprint(gamedesign_bp, url_prefix='/gamedesign')
    except ImportError:
        print("⚠️  routes.gamedesign não encontrado")
    
    # Rota de health check
    @app.route('/health')
    def health_check():
        """Verificação de saúde do sistema"""
        try:
            # Testar conexão com banco
            with app.app_context():
                db.engine.execute('SELECT 1')
            
            return {
                'status': 'healthy',
                'database': 'connected',
                'message': 'Sistema funcionando corretamente'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
    
    app.run(debug=True)