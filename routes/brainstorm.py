# routes/brainstorm.py - Rotas do Módulo Brainstorming
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import BrainstormSession, Card, GameGroup, db
from services.groq_service import GroqService
from datetime import datetime
import json

brainstorm_bp = Blueprint('brainstorm', __name__)

@brainstorm_bp.route('/')
def index():
    """Página principal do brainstorming"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    session = BrainstormSession.query.get_or_404(session_id)
    cards = Card.query.filter_by(session_id=session_id).all()
    
    return render_template('brainstorm/index.html', session=session, cards=cards)

@brainstorm_bp.route('/add-card', methods=['POST'])
def add_card():
    """Adiciona um novo card à sessão"""
    data = request.get_json()
    
    try:
        card = Card(
            session_id=data['session_id'],
            text=data['text'].strip(),
            color=data.get('color', '#ffd700'),
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0),
            is_ai_generated=data.get('is_ai_generated', False)
        )
        
        db.session.add(card)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'card': {
                'id': card.id,
                'text': card.text,
                'color': card.color,
                'position_x': card.position_x,
                'position_y': card.position_y,
                'is_ai_generated': card.is_ai_generated
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@brainstorm_bp.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    """Obtém sugestões de IA para brainstorming"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        existing_cards = Card.query.filter_by(session_id=session_id).all()
        
        groq_service = GroqService()
        result = groq_service.generate_brainstorm_suggestions(existing_cards, session_id)
        
        if result['success']:
            # Dividir as sugestões em linhas e criar cards automaticamente
            suggestions = [s.strip() for s in result['content'].split('\n') if s.strip()]
            new_cards = []
            
            for i, suggestion in enumerate(suggestions[:3]):  # Limitar a 3 sugestões
                card = Card(
                    session_id=session_id,
                    text=suggestion,
                    color='#90EE90',  # Verde claro para cards da IA
                    position_x=100 + (i * 250),
                    position_y=300,
                    is_ai_generated=True
                )
                db.session.add(card)
                new_cards.append(card)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'cards': [{
                    'id': card.id,
                    'text': card.text,
                    'color': card.color,
                    'position_x': card.position_x,
                    'position_y': card.position_y,
                    'is_ai_generated': card.is_ai_generated
                } for card in new_cards]
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@brainstorm_bp.route('/update-card-position', methods=['POST'])
def update_card_position():
    """Atualiza a posição de um card"""
    data = request.get_json()
    
    try:
        card = Card.query.get_or_404(data['card_id'])
        card.position_x = data['position_x']
        card.position_y = data['position_y']
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@brainstorm_bp.route('/delete-card', methods=['POST'])
def delete_card():
    """Remove um card"""
    data = request.get_json()
    
    try:
        card = Card.query.get_or_404(data['card_id'])
        db.session.delete(card)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@brainstorm_bp.route('/group-ideas')
def group_ideas():
    """Página para agrupar ideias"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    session = BrainstormSession.query.get_or_404(session_id)
    cards = Card.query.filter_by(session_id=session_id).all()
    groups = GameGroup.query.filter_by(session_id=session_id).all()
    
    return render_template('brainstorm/group_ideas.html', 
                         session=session, cards=cards, groups=groups)

@brainstorm_bp.route('/create-group', methods=['POST'])
def create_group():
    """Cria um novo grupo de ideias"""
    data = request.get_json()
    
    try:
        group = GameGroup(
            session_id=data['session_id'],
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#87ceeb')
        )
        
        db.session.add(group)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'color': group.color
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@brainstorm_bp.route('/add-card-to-group', methods=['POST'])
def add_card_to_group():
    """Adiciona um card a um grupo"""
    data = request.get_json()
    
    try:
        card = Card.query.get_or_404(data['card_id'])
        card.group_id = data['group_id']
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@brainstorm_bp.route('/finish-session', methods=['POST'])
def finish_session():
    """Finaliza a sessão de brainstorming"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        session.end_time = datetime.utcnow()
        session.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('socratic.index', session_id=session_id)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400