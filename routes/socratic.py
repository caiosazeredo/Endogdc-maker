# routes/socratic.py - Corrigido para funcionar com a estrutura real do banco
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import BrainstormSession, Card, SocraticSessionAnswers
from datetime import datetime

socratic_bp = Blueprint('socratic', __name__)

@socratic_bp.route('/')
def index():
    """Página principal da reflexão socrática"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        cards = Card.query.filter_by(session_id=session_id).all()
        
        # Buscar respostas socráticas existentes
        answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        return render_template('socratic/index.html', 
                             session=session, 
                             cards=cards,
                             answers=answers)
    except Exception as e:
        print(f"❌ Erro no socratic index: {e}")
        return redirect(url_for('home.index'))

@socratic_bp.route('/save-answers', methods=['POST'])
def save_answers():
    """Salva as respostas socráticas"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        # Verificar se sessão existe
        session = BrainstormSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # Verificar se já existem respostas
        answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        if answers:
            # Atualizar respostas existentes
            if 'problem' in data:
                answers.problem = data['problem']
            if 'justification' in data:
                answers.justification = data['justification']
            if 'impact' in data:
                answers.impact = data['impact']
            if 'motivation' in data:
                answers.motivation = data['motivation']
            
            # Atualizar timestamp se existir
            if hasattr(answers, 'updated_at'):
                answers.updated_at = datetime.utcnow()
        else:
            # Criar novas respostas usando o construtor corrigido
            answers = SocraticSessionAnswers(
                session_id=session_id,
                problem=data.get('problem', ''),
                justification=data.get('justification', ''),
                impact=data.get('impact', ''),
                motivation=data.get('motivation', '')
            )
            db.session.add(answers)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Respostas salvas com sucesso!',
            'answers': {
                'problem': answers.problem,
                'justification': answers.justification,
                'impact': answers.impact,
                'motivation': answers.motivation
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao salvar respostas socráticas: {e}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': f'Erro ao salvar: {str(e)}'
        }), 500

@socratic_bp.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    """Obtém sugestões de IA para reflexão socrática"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        session = BrainstormSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # Obter contexto das ideias do brainstorming
        cards = Card.query.filter_by(session_id=session_id).all()
        ideas_context = [card.content for card in cards] if cards else []
        
        # Por enquanto, retornar sugestões fixas baseadas no contexto
        # TODO: Implementar integração real com IA
        suggestions = {
            'problem': f"Como podemos criar um jogo educativo eficaz sobre {session.theme}?",
            'justification': "Este problema é relevante porque combina aprendizado com engajamento através de gamificação.",
            'impact': "O impacto esperado é melhorar a retenção de conhecimento e motivação dos estudantes.",
            'motivation': "Os estudantes se sentirão mais engajados através de elementos lúdicos e desafios progressivos."
        }
        
        # Se temos ideias do brainstorming, personalizar as sugestões
        if ideas_context:
            first_idea = ideas_context[0]
            suggestions['problem'] = f"Como implementar '{first_idea}' em um jogo educativo eficaz?"
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'context_ideas': len(ideas_context),
            'message': 'Sugestões geradas com base nas ideias do brainstorming!'
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar sugestões socráticas: {e}")
        return jsonify({
            'success': False, 
            'error': f'Erro ao gerar sugestões: {str(e)}'
        }), 500

@socratic_bp.route('/skip', methods=['POST'])
def skip():
    """Pula a reflexão socrática criando respostas padrão"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        session = BrainstormSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Sessão não encontrada'}), 404
        
        # Verificar se já existem respostas
        answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        if not answers:
            # Criar respostas padrão usando o construtor corrigido
            answers = SocraticSessionAnswers(
                session_id=session_id,
                problem=f"Desenvolver um jogo educativo sobre {session.theme or 'aprendizado'}",
                justification="Reflexão socrática pulada pelo usuário",
                impact="Impacto educacional a ser definido",
                motivation="Motivação através de gamificação"
            )
            db.session.add(answers)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reflexão socrática pulada com sucesso!',
            'redirect_url': url_for('bloom.index', session_id=session_id)
        })
        
    except Exception as e:
        print(f"❌ Erro ao pular reflexão socrática: {e}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': f'Erro ao pular: {str(e)}'
        }), 500

@socratic_bp.route('/finish', methods=['POST'])
def finish():
    """Finaliza a reflexão socrática"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
        
        # Verificar se há respostas salvas
        answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        if not answers:
            return jsonify({
                'success': False, 
                'error': 'Nenhuma resposta socrática encontrada. Salve as respostas primeiro.'
            }), 400
        
        # Verificar se as respostas estão completas
        if not answers.problem or not answers.justification:
            return jsonify({
                'success': False, 
                'error': 'Respostas incompletas. Complete pelo menos o problema e justificação.'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Reflexão socrática finalizada com sucesso!',
            'redirect_url': url_for('bloom.index', session_id=session_id)
        })
        
    except Exception as e:
        print(f"❌ Erro ao finalizar reflexão socrática: {e}")
        return jsonify({
            'success': False, 
            'error': f'Erro ao finalizar: {str(e)}'
        }), 500

@socratic_bp.route('/export', methods=['GET'])
def export_answers():
    """Exporta as respostas socráticas"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'session_id é obrigatório'}), 400
    
    try:
        answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        if not answers:
            return jsonify({'success': False, 'error': 'Nenhuma resposta encontrada'}), 404
        
        export_data = {
            'session_id': session_id,
            'problem': answers.problem,
            'justification': answers.justification,
            'impact': answers.impact,
            'motivation': answers.motivation,
            'created_at': answers.created_at.isoformat() if answers.created_at else None
        }
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        print(f"❌ Erro ao exportar respostas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500