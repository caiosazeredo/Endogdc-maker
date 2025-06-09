# routes/home.py - Rotas da Página Inicial
from flask import Blueprint, render_template, redirect, url_for
from models import BrainstormSession, db
from datetime import datetime

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """Página inicial - cria nova sessão de brainstorming"""
    return render_template('home/index.html')

@home_bp.route('/start-session')
def start_session():
    """Inicia uma nova sessão de design de jogo"""
    session = BrainstormSession(
        start_time=datetime.utcnow(),
        status='active',
        theme='Novo Jogo Educativo'
    )
    
    db.session.add(session)
    db.session.commit()
    
    return redirect(url_for('brainstorm.index', session_id=session.id))