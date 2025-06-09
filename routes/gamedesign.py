# routes/gamedesign.py - Módulo Game Design (VERSÃO CORRIGIDA)
from flask import Blueprint, render_template_string, jsonify

gamedesign_bp = Blueprint('gamedesign', __name__)

@gamedesign_bp.route('/')
def index():
    """Página principal do Game Design Canvas"""
    return render_template_string("""
    <h1>🎮 Game Design Canvas</h1>
    <p>Módulo Game Design funcionando!</p>
    <p><a href="/">← Voltar ao início</a></p>
    """)

@gamedesign_bp.route('/health')
def health():
    """Verificação de saúde do módulo"""
    return jsonify({
        'status': 'ok',
        'module': 'gamedesign',
        'message': 'Módulo funcionando'
    })
