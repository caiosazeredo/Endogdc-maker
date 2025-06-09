# routes/bloom.py - Rotas do Módulo Taxonomia de Bloom
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import BrainstormSession, BloomObjective, BloomTaxonomyLevel, SocraticSessionAnswers, db
from services.groq_service import GroqService
import json

bloom_bp = Blueprint('bloom', __name__)

# Dados dos níveis da Taxonomia de Bloom
BLOOM_LEVELS = [
    {
        'name': 'Criar',
        'description': 'Juntar elementos para formar um todo coerente ou funcional; reorganizar elementos em um novo padrão ou estrutura.',
        'color': '#8B4513',  # Marrom
        'order': 6,
        'verbs': ['criar', 'desenvolver', 'projetar', 'construir', 'inventar', 'formular']
    },
    {
        'name': 'Avaliar', 
        'description': 'Fazer julgamentos baseados em critérios e padrões.',
        'color': '#FF4500',  # Laranja avermelhado
        'order': 5,
        'verbs': ['avaliar', 'julgar', 'criticar', 'verificar', 'testar', 'monitorar']
    },
    {
        'name': 'Analisar',
        'description': 'Quebrar material em partes constituintes e determinar como as partes se relacionam entre si.',
        'color': '#FFD700',  # Dourado
        'order': 4,
        'verbs': ['analisar', 'comparar', 'contrastar', 'organizar', 'desconstruir', 'questionar']
    },
    {
        'name': 'Aplicar',
        'description': 'Executar ou usar um procedimento em uma situação específica.',
        'color': '#32CD32',  # Verde lima
        'order': 3,
        'verbs': ['aplicar', 'executar', 'implementar', 'demonstrar', 'usar', 'ilustrar']
    },
    {
        'name': 'Compreender',
        'description': 'Construir significado a partir de mensagens instrucionais, incluindo comunicação oral, escrita e gráfica.',
        'color': '#4169E1',  # Azul royal
        'order': 2,
        'verbs': ['compreender', 'interpretar', 'exemplificar', 'classificar', 'resumir', 'explicar']
    },
    {
        'name': 'Lembrar',
        'description': 'Recuperar conhecimento relevante da memória de longo prazo.',
        'color': '#8A2BE2',  # Azul violeta
        'order': 1,
        'verbs': ['lembrar', 'reconhecer', 'listar', 'identificar', 'recuperar', 'nomear']
    }
]

@bloom_bp.route('/')
def index():
    """Página principal da Taxonomia de Bloom"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    session = BrainstormSession.query.get_or_404(session_id)
    objectives = BloomObjective.query.filter_by(session_id=session_id).all()
    
    # Organizar objetivos por nível
    objectives_by_level = {}
    for obj in objectives:
        if obj.level not in objectives_by_level:
            objectives_by_level[obj.level] = []
        objectives_by_level[obj.level].append(obj)
    
    return render_template('bloom/index.html', 
                         session=session, 
                         bloom_levels=BLOOM_LEVELS,
                         objectives_by_level=objectives_by_level)

@bloom_bp.route('/initialize-levels', methods=['POST'])
def initialize_levels():
    """Inicializa os níveis da Taxonomia de Bloom no banco"""
    try:
        for level_data in BLOOM_LEVELS:
            existing_level = BloomTaxonomyLevel.query.filter_by(name=level_data['name']).first()
            if not existing_level:
                level = BloomTaxonomyLevel(
                    name=level_data['name'],
                    description=level_data['description'],
                    level_order=level_data['order'],
                    color=level_data['color'],
                    verbs=json.dumps(level_data['verbs'])
                )
                db.session.add(level)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@bloom_bp.route('/generate-objectives', methods=['POST'])
def generate_objectives():
    """Gera objetivos educacionais automaticamente"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        socratic_answers = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        
        if not socratic_answers:
            return jsonify({
                'success': False, 
                'error': 'Respostas socráticas não encontradas. Complete o módulo socrático primeiro.'
            }), 400
        
        groq_service = GroqService()
        result = groq_service.generate_bloom_objectives(socratic_answers, session_id)
        
        if result['success']:
            try:
                # Limpar e fazer parse da resposta JSON
                response_text = result['content'].strip()
                
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                objectives_data = json.loads(response_text)
                new_objectives = []
                
                # Criar objetivos no banco
                for obj_data in objectives_data.get('objectives', []):
                    # Determinar a cor baseada no nível
                    level_color = '#6c757d'  # Cor padrão
                    for level in BLOOM_LEVELS:
                        if level['name'].lower() in obj_data['level'].lower():
                            level_color = level['color']
                            break
                    
                    objective = BloomObjective(
                        session_id=session_id,
                        text=obj_data['text'],
                        level=obj_data['level'],
                        color=level_color,
                        is_ai_generated=True
                    )
                    db.session.add(objective)
                    new_objectives.append(objective)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'objectives': [{
                        'id': obj.id,
                        'text': obj.text,
                        'level': obj.level,
                        'color': obj.color,
                        'is_ai_generated': obj.is_ai_generated
                    } for obj in new_objectives]
                })
                
            except json.JSONDecodeError as e:
                return jsonify({
                    'success': False, 
                    'error': f'Erro ao processar resposta da IA: {str(e)}'
                }), 400
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bloom_bp.route('/add-objective', methods=['POST'])
def add_objective():
    """Adiciona um objetivo manualmente"""
    data = request.get_json()
    
    try:
        # Determinar a cor baseada no nível
        level_color = '#6c757d'  # Cor padrão
        for level in BLOOM_LEVELS:
            if level['name'].lower() == data['level'].lower():
                level_color = level['color']
                break
        
        objective = BloomObjective(
            session_id=data['session_id'],
            text=data['text'].strip(),
            level=data['level'],
            color=level_color,
            is_ai_generated=False
        )
        
        db.session.add(objective)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'objective': {
                'id': objective.id,
                'text': objective.text,
                'level': objective.level,
                'color': objective.color,
                'is_ai_generated': objective.is_ai_generated
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@bloom_bp.route('/delete-objective', methods=['POST'])
def delete_objective():
    """Remove um objetivo"""
    data = request.get_json()
    
    try:
        objective = BloomObjective.query.get_or_404(data['objective_id'])
        db.session.delete(objective)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@bloom_bp.route('/finish', methods=['POST'])
def finish():
    """Finaliza o módulo de Taxonomia de Bloom"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    return jsonify({
        'success': True,
        'redirect_url': url_for('gamedesign.index', session_id=session_id)
    })