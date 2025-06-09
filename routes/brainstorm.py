# routes/brainstorm.py - Corrigido para funcionar com a estrutura real do banco
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import BrainstormSession, Card, GameGroup
from datetime import datetime

brainstorm_bp = Blueprint('brainstorm', __name__)

@brainstorm_bp.route('/')
def index():
    """Página principal do brainstorming"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        cards = Card.query.filter_by(session_id=session_id).all()
        
        return render_template('brainstorm/index.html', 
                             session=session, 
                             cards=cards)
    except Exception as e:
        print(f"❌ Erro no brainstorm index: {e}")
        return redirect(url_for('home.index'))

@brainstorm_bp.route('/add-card', methods=['POST'])
def add_card():
    """Adiciona uma nova carta de ideia"""
    try:
        data = request.get_json() or {}
        
        # Validação básica
        if not data.get('session_id'):
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        if not data.get('text') and not data.get('content'):
            return jsonify({'success': False, 'error': 'text ou content é obrigatório'}), 400
        
        # Verificar se sessão existe
        session = BrainstormSession.query.get(data['session_id'])
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # Criar card usando a estrutura real do banco
        card = Card(
            session_id=data['session_id'],
            content=data.get('text') or data.get('content'),  # Usar 'content' no banco
            category=data.get('category', 'geral'),
            color=data.get('color', '#FFD700'),
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0)
        )
        
        db.session.add(card)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'card': {
                'id': card.id,
                'text': card.content,  # Retornar como 'text' para compatibilidade
                'content': card.content,
                'category': card.category,
                'color': card.color,
                'position_x': card.position_x,
                'position_y': card.position_y
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao adicionar card: {e}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': f'Erro interno: {str(e)}'
        }), 500

@brainstorm_bp.route('/update-card', methods=['POST'])
def update_card():
    """Atualiza uma carta existente"""
    try:
        data = request.get_json() or {}
        
        if not data.get('card_id'):
            return jsonify({'success': False, 'error': 'card_id é obrigatório'}), 400
        
        card = Card.query.get(data['card_id'])
        if not card:
            return jsonify({'success': False, 'error': 'Card não encontrado'}), 404
        
        # Atualizar campos se fornecidos
        if 'text' in data or 'content' in data:
            card.content = data.get('text') or data.get('content')
        if 'category' in data:
            card.category = data['category']
        if 'color' in data:
            card.color = data['color']
        if 'position_x' in data:
            card.position_x = data['position_x']
        if 'position_y' in data:
            card.position_y = data['position_y']
        
        # Atualizar updated_at se existir
        if hasattr(card, 'updated_at'):
            card.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'card': {
                'id': card.id,
                'text': card.content,
                'content': card.content,
                'category': card.category,
                'color': card.color,
                'position_x': card.position_x,
                'position_y': card.position_y
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao atualizar card: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brainstorm_bp.route('/delete-card', methods=['POST'])
def delete_card():
    """Remove uma carta"""
    try:
        data = request.get_json() or {}
        
        if not data.get('card_id'):
            return jsonify({'success': False, 'error': 'card_id é obrigatório'}), 400
        
        card = Card.query.get(data['card_id'])
        if not card:
            return jsonify({'success': False, 'error': 'Card não encontrado'}), 404
        
        db.session.delete(card)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Erro ao deletar card: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brainstorm_bp.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    """Obtém sugestões de IA para ideias"""
    try:
        data = request.get_json() or {}
        
        if not data.get('session_id'):
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        session = BrainstormSession.query.get(data['session_id'])
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # Por enquanto, retornar sugestões fixas (para debug)
        # TODO: Implementar integração real com IA
        suggestions = [
            "Sistema de pontuação por progresso",
            "Desafios colaborativos em equipe",
            "Narrativa interativa com escolhas",
            "Elementos de realidade aumentada",
            "Mecânica de construção progressiva"
        ]
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'message': 'Sugestões geradas com sucesso!'
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar sugestões: {e}")
        return jsonify({
            'success': False, 
            'error': f'Erro ao gerar sugestões: {str(e)}'
        }), 500

@brainstorm_bp.route('/create-group', methods=['POST'])
def create_group():
    """Cria um grupo para organizar cartas"""
    try:
        data = request.get_json() or {}
        
        if not data.get('session_id'):
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'name é obrigatório'}), 400
        
        group = GameGroup(
            session_id=data['session_id'],
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#87CEEB')
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
        print(f"❌ Erro ao criar grupo: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brainstorm_bp.route('/finish-session', methods=['POST'])
def finish_session():
    """Finaliza a sessão de brainstorming"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        session = BrainstormSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # Atualizar status da sessão
        session.status = 'completed'
        if hasattr(session, 'end_time'):
            session.end_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('socratic.index', session_id=session_id)
        })
        
    except Exception as e:
        print(f"❌ Erro ao finalizar sessão: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brainstorm_bp.route('/clear-all', methods=['POST'])
def clear_all():
    """Remove todas as cartas da sessão"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        # Deletar todas as cartas da sessão
        Card.query.filter_by(session_id=session_id).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Todas as cartas foram removidas'})
        
    except Exception as e:
        print(f"❌ Erro ao limpar cartas: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brainstorm_bp.route('/export', methods=['GET'])
def export_session():
    """Exporta dados da sessão"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
    
    try:
        session = BrainstormSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        cards = Card.query.filter_by(session_id=session_id).all()
        groups = GameGroup.query.filter_by(session_id=session_id).all()
        
        export_data = {
            'session': {
                'id': session.id,
                'theme': session.theme,
                'description': getattr(session, 'description', ''),
                'status': session.status,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': getattr(session, 'end_time', None)
            },
            'cards': [{
                'id': card.id,
                'content': card.content,
                'category': getattr(card, 'category', ''),
                'color': card.color,
                'position_x': getattr(card, 'position_x', 0),
                'position_y': getattr(card, 'position_y', 0)
            } for card in cards],
            'groups': [{
                'id': group.id,
                'name': group.name,
                'description': getattr(group, 'description', ''),
                'color': getattr(group, 'color', '#87CEEB')
            } for group in groups]
        }
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        print(f"❌ Erro ao exportar sessão: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500