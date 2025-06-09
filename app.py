# app.py - Aplicação Principal Flask
from flask import Flask
from config import Config
from extensions import db, migrate
from routes.brainstorm import brainstorm_bp
from routes.socratic import socratic_bp  
from routes.bloom import bloom_bp
from routes.gamedesign import gamedesign_bp
from routes.home import home_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(brainstorm_bp, url_prefix='/brainstorm')
    app.register_blueprint(socratic_bp, url_prefix='/socratic')
    app.register_blueprint(bloom_bp, url_prefix='/bloom')
    app.register_blueprint(gamedesign_bp, url_prefix='/gamedesign')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)