# routes/socratic.py - Rotas do Módulo Socrático
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import BrainstormSession, Card, SocraticSessionAnswers, db
from services.groq_service import GroqService
import json

socratic_bp = Blueprint('socratic', __name__)

@socratic_bp.route('/')
def index():
    """Página principal do agente socrático"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    session = BrainstormSession.query.get_or_404(session_id)
    cards = Card.query.filter_by(session_id=session_id).all()
    existing_answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
    
    return render_template('socratic/index.html', 
                         session=session, cards=cards, answers=existing_answers)

@socratic_bp.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    """Obtém sugestões socráticas da IA"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        cards = Card.query.filter_by(session_id=session_id).all()
        
        if not cards:
            return jsonify({
                'success': False, 
                'error': 'Nenhuma ideia encontrada para análise'
            }), 400
        
        groq_service = GroqService()
        result = groq_service.generate_socratic_suggestions(cards, session_id)
        
        if result['success']:
            try:
                # Tentar fazer parse do JSON da resposta
                response_text = result['content'].strip()
                
                # Limpar possíveis caracteres extras
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                suggestions = json.loads(response_text)
                
                return jsonify({
                    'success': True,
                    'suggestions': suggestions
                })
            except json.JSONDecodeError:
                # Se não conseguir fazer parse, retornar texto bruto
                return jsonify({
                    'success': True,
                    'suggestions': {
                        'problem': result['content'][:200] + '...',
                        'justification': 'Analise as justificativas das ideias propostas...',
                        'impact': 'Considere o impacto educacional das ideias...',
                        'motivation': 'Pense nos elementos motivacionais dos jogos...'
                    }
                })
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@socratic_bp.route('/save-answers', methods=['POST'])
def save_answers():
    """Salva as respostas socráticas"""
    data = request.get_json()
    
    try:
        session_id = data.get('session_id')
        
        # Verificar se já existe resposta para esta sessão
        existing_answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        if existing_answers:
            # Atualizar respostas existentes
            existing_answers.problem = data.get('problem', '').strip()
            existing_answers.justification = data.get('justification', '').strip()
            existing_answers.impact = data.get('impact', '').strip()
            existing_answers.motivation = data.get('motivation', '').strip()
        else:
            # Criar novas respostas
            answers = SocraticSessionAnswers(
                session_id=session_id,
                problem=data.get('problem', '').strip(),
                justification=data.get('justification', '').strip(),
                impact=data.get('impact', '').strip(),
                motivation=data.get('motivation', '').strip()
            )
            db.session.add(answers)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('bloom.index', session_id=session_id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@socratic_bp.route('/skip', methods=['POST'])
def skip():
    """Pula o módulo socrático"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    # Criar respostas vazias para manter a consistência
    existing_answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
    if not existing_answers:
        answers = SocraticSessionAnswers(
            session_id=session_id,
            problem='Não especificado',
            justification='Não especificado',
            impact='Não especificado', 
            motivation='Não especificado'
        )
        db.session.add(answers)
        db.session.commit()
    
    return jsonify({
        'success': True,
        'redirect_url': url_for('bloom.index', session_id=session_id)
    })