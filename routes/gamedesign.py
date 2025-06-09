# routes/gamedesign.py - Rotas do Módulo Game Design
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from models import BrainstormSession, GdcTemplate, GdcSection, GdcNote, Card, SocraticSessionAnswers, BloomObjective, db
from services.groq_service import GroqService
from services.multiagent_service import MultiAgentService
import base64
import io
from datetime import datetime

gamedesign_bp = Blueprint('gamedesign', __name__)

# Definição das seções do Endo-GDC
ENDO_GDC_SECTIONS = [
    {
        'name': 'Jogadores',
        'description': 'Quem são os jogadores target? Idade, perfil, experiência com jogos.',
        'color': '#FFB6C1',  # Rosa claro
        'position': {'x': 50, 'y': 50, 'width': 200, 'height': 150}
    },
    {
        'name': 'Objetivos de Aprendizagem',
        'description': 'Objetivos educacionais específicos baseados na Taxonomia de Bloom.',
        'color': '#98FB98',  # Verde claro
        'position': {'x': 270, 'y': 50, 'width': 200, 'height': 150}
    },
    {
        'name': 'Contexto Educacional',
        'description': 'Ambiente educacional, disciplina, recursos disponíveis.',
        'color': '#87CEEB',  # Azul céu
        'position': {'x': 490, 'y': 50, 'width': 200, 'height': 150}
    },
    {
        'name': 'Mecânicas de Jogo',
        'description': 'Regras, sistemas de pontuação, progressão, feedback.',
        'color': '#DDA0DD',  # Ameixa
        'position': {'x': 50, 'y': 220, 'width': 200, 'height': 150}
    },
    {
        'name': 'Narrativa',
        'description': 'História, personagens, mundo do jogo, tema.',
        'color': '#F0E68C',  # Cáqui
        'position': {'x': 270, 'y': 220, 'width': 200, 'height': 150}
    },
    {
        'name': 'Tecnologia',
        'description': 'Plataforma, ferramentas, recursos técnicos necessários.',
        'color': '#FFA07A',  # Salmão claro
        'position': {'x': 490, 'y': 220, 'width': 200, 'height': 150}
    },
    {
        'name': 'Avaliação',
        'description': 'Como o aprendizado será medido e avaliado.',
        'color': '#20B2AA',  # Verde mar claro
        'position': {'x': 50, 'y': 390, 'width': 200, 'height': 150}
    },
    {
        'name': 'Recursos',
        'description': 'Orçamento, tempo, equipe, materiais necessários.',
        'color': '#CD853F',  # Peru
        'position': {'x': 270, 'y': 390, 'width': 200, 'height': 150}
    },
    {
        'name': 'Motivação e Engajamento',
        'description': 'Elementos que mantêm os jogadores motivados e engajados.',
        'color': '#DA70D6',  # Orquídea
        'position': {'x': 490, 'y': 390, 'width': 200, 'height': 150}
    }
]

@gamedesign_bp.route('/')
def index():
    """Página principal do Game Design Canvas"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    session = BrainstormSession.query.get_or_404(session_id)
    
    # Inicializar template se não existir
    template = _get_or_create_template()
    
    # Buscar notas existentes
    notes = GdcNote.query.filter_by(session_id=session_id).all()
    notes_by_section = {}
    for note in notes:
        section_name = note.section.name
        if section_name not in notes_by_section:
            notes_by_section[section_name] = []
        notes_by_section[section_name].append(note)
    
    return render_template('gamedesign/index.html', 
                         session=session, 
                         sections=ENDO_GDC_SECTIONS,
                         notes_by_section=notes_by_section)

def _get_or_create_template():
    """Obtém ou cria o template do Endo-GDC"""
    template = GdcTemplate.query.filter_by(is_default=True).first()
    
    if not template:
        # Criar template padrão
        template = GdcTemplate(
            name='Endo-GDC Padrão',
            description='Template padrão do Game Design Canvas para Jogos Educativos Endógenos',
            is_default=True
        )
        db.session.add(template)
        db.session.flush()  # Para obter o ID
        
        # Criar seções
        for i, section_data in enumerate(ENDO_GDC_SECTIONS):
            section = GdcSection(
                template_id=template.id,
                name=section_data['name'],
                description=section_data['description'],
                background_color=section_data['color'],
                position_x=section_data['position']['x'],
                position_y=section_data['position']['y'],
                width=section_data['position']['width'],
                height=section_data['position']['height'],
                order_index=i
            )
            db.session.add(section)
        
        db.session.commit()
    
    return template

@gamedesign_bp.route('/add-note', methods=['POST'])
def add_note():
    """Adiciona uma nota a uma seção"""
    data = request.get_json()
    
    try:
        # Encontrar a seção pelo nome
        template = _get_or_create_template()
        section = GdcSection.query.filter_by(
            template_id=template.id, 
            name=data['section_name']
        ).first()
        
        if not section:
            return jsonify({'success': False, 'error': 'Seção não encontrada'}), 400
        
        note = GdcNote(
            session_id=data['session_id'],
            section_id=section.id,
            text=data['text'].strip(),
            color=data.get('color', '#ffff99'),
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0),
            is_ai_generated=data.get('is_ai_generated', False)
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'note': {
                'id': note.id,
                'text': note.text,
                'color': note.color,
                'position_x': note.position_x,
                'position_y': note.position_y,
                'is_ai_generated': note.is_ai_generated
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@gamedesign_bp.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    """Obtém sugestões da IA para uma seção específica"""
    data = request.get_json()
    session_id = data.get('session_id')
    section_name = data.get('section_name')
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        
        # Construir contexto baseado nos dados da sessão
        context_parts = []
        
        # Adicionar cards do brainstorming
        cards = Card.query.filter_by(session_id=session_id).all()
        if cards:
            context_parts.append("Ideias do Brainstorming:")
            for card in cards[:5]:  # Limitar a 5 cards
                context_parts.append(f"- {card.text}")
        
        # Adicionar respostas socráticas
        socratic = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        if socratic:
            context_parts.append(f"\nProblema Educacional: {socratic.problem}")
            context_parts.append(f"Motivação: {socratic.motivation}")
        
        # Adicionar objetivos de aprendizagem
        objectives = BloomObjective.query.filter_by(session_id=session_id).all()
        if objectives:
            context_parts.append("\nObjetivos de Aprendizagem:")
            for obj in objectives[:3]:  # Limitar a 3 objetivos
                context_parts.append(f"- {obj.text} ({obj.level})")
        
        context = '\n'.join(context_parts) if context_parts else "Projeto de jogo educativo em desenvolvimento."
        
        groq_service = GroqService()
        result = groq_service.generate_gamedesign_suggestions(context, section_name, session_id)
        
        if result['success']:
            # Dividir as sugestões em linhas
            suggestions = [s.strip() for s in result['content'].split('\n') if s.strip() and not s.strip().startswith('-')]
            
            return jsonify({
                'success': True,
                'suggestions': suggestions[:5]  # Limitar a 5 sugestões
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gamedesign_bp.route('/delete-note', methods=['POST'])
def delete_note():
    """Remove uma nota"""
    data = request.get_json()
    
    try:
        note = GdcNote.query.get_or_404(data['note_id'])
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@gamedesign_bp.route('/multiagent-chat', methods=['POST'])
def multiagent_chat():
    """Chat multiagentes para discussão sobre o design"""
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message')
    focus_section = data.get('focus_section')
    
    try:
        multiagent_service = MultiAgentService()
        result = multiagent_service.start_multiagent_discussion(
            session_id, user_message, focus_section
        )
        
        return jsonify({
            'success': True,
            'agents_responses': result['agents_responses'],
            'synthesis': result['synthesis'],
            'suggestions': result['suggestions'],
            'context': result['context']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gamedesign_bp.route('/apply-suggestion', methods=['POST'])
def apply_suggestion():
    """Aplica uma sugestão específica do chat multiagentes"""
    data = request.get_json()
    session_id = data.get('session_id')
    suggestion = data.get('suggestion')
    
    try:
        # Encontrar a seção pelo nome
        template = _get_or_create_template()
        section = GdcSection.query.filter_by(
            template_id=template.id, 
            name=suggestion['section']
        ).first()
        
        if not section:
            return jsonify({'success': False, 'error': 'Seção não encontrada'}), 400
        
        if suggestion['action'] == 'add':
            note = GdcNote(
                session_id=session_id,
                section_id=section.id,
                text=suggestion['content'],
                color='#E6F3FF',  # Azul claro para sugestões de agentes
                position_x=10,
                position_y=80,
                is_ai_generated=True
            )
            db.session.add(note)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'note': {
                    'id': note.id,
                    'text': note.text,
                    'color': note.color,
                    'position_x': note.position_x,
                    'position_y': note.position_y,
                    'is_ai_generated': note.is_ai_generated,
                    'section_name': suggestion['section']
                }
            })
        
        # Implementar outras ações conforme necessário
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@gamedesign_bp.route('/export-canvas', methods=['POST'])
def export_canvas():
    """Exporta o canvas como HTML formatado para exportação"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        session = BrainstormSession.query.get_or_404(session_id)
        
        # Coletar todos os dados do projeto
        cards = Card.query.filter_by(session_id=session_id).all()
        socratic = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        objectives = BloomObjective.query.filter_by(session_id=session_id).all()
        notes = GdcNote.query.filter_by(session_id=session_id).all()
        
        # Organizar notas por seção
        notes_by_section = {}
        for note in notes:
            section_name = note.section.name
            if section_name not in notes_by_section:
                notes_by_section[section_name] = []
            notes_by_section[section_name].append(note)
        
        # Gerar nome do jogo baseado nas ideias
        game_name = _generate_game_name(cards, socratic)
        
        # Gerar HTML do canvas no formato dos exemplos
        canvas_html = _generate_endo_gdc_html(
            game_name, session, cards, socratic, objectives, notes_by_section
        )
        
        return jsonify({
            'success': True,
            'html': canvas_html,
            'game_name': game_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _generate_game_name(cards, socratic):
    """Gera nome do jogo baseado no contexto"""
    if socratic and socratic.problem:
        # Usar Groq para gerar nome baseado no problema
        groq_service = GroqService()
        prompt = f"""Com base no seguinte problema educacional, sugira um nome criativo para um jogo educativo:

Problema: {socratic.problem}

O nome deve ser:
- Criativo e memorável
- Relacionado ao tema educacional
- Em português
- Máximo 2-3 palavras

Responda apenas com o nome do jogo, nada mais."""

        result = groq_service.generate_response(prompt, 'game_naming')
        if result['success']:
            return result['content'].strip().replace('"', '')
    
    # Nome padrão se não conseguir gerar
    return f"JogoEducativo#{session_id}" if 'session_id' in locals() else "NovoJogoEducativo"

def _generate_endo_gdc_html(game_name, session, cards, socratic, objectives, notes_by_section):
    """Gera HTML do Endo-GDC no formato dos exemplos"""
    
    # Mapear seções para o formato do template
    section_mapping = {
        'Jogadores': 'player',
        'Contexto Educacional': 'situation', 
        'Objetivos de Aprendizagem': 'learning-objectives',
        'Narrativa': 'narrative',
        'Processo Lúdico de Aprendizado': 'learning-process',
        'Mecânicas de Jogo': 'game',
        'Objetivos do Jogo': 'game-objectives',
        'Motivação e Engajamento': 'inspirations',
        'Tecnologia': 'restrictions',
        'Recursos': 'restrictions',
        'Avaliação': 'restrictions'
    }
    
    # Preparar conteúdo para cada seção
    sections_content = {}
    
    # Preencher com notas existentes
    for original_name, notes in notes_by_section.items():
        mapped_name = section_mapping.get(original_name, 'restrictions')
        if mapped_name not in sections_content:
            sections_content[mapped_name] = []
        sections_content[mapped_name].extend([note.text for note in notes])
    
    # Adicionar objetivos educacionais se existirem
    if objectives:
        bloom_levels = ['Lembrar', 'Compreender', 'Aplicar', 'Analisar', 'Avaliar', 'Criar']
        objectives_text = []
        for level in bloom_levels:
            level_objectives = [obj for obj in objectives if obj.level == level]
            if level_objectives:
                for obj in level_objectives:
                    verb = obj.text.split()[0].upper() if obj.text else level.upper()
                    objectives_text.append(f"• {verb} {obj.text}")
        
        if 'learning-objectives' not in sections_content:
            sections_content['learning-objectives'] = []
        sections_content['learning-objectives'].extend(objectives_text)
    
    # Se não tiver conteúdo suficiente, gerar com IA
    if len(sections_content) < 6:
        sections_content = _enhance_sections_with_ai(game_name, socratic, cards, sections_content)
    
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ENDO-GDC: {game_name}</title>
    <style>
        body {{
            font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: white;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-template-rows: auto auto auto auto auto;
            gap: 10px;
        }}
        
        .header-cell {{
            border: 1px solid #000;
            padding: 10px;
            background-color: white;
        }}
        
        .header-row {{
            display: contents;
        }}
        
        .situation {{
            grid-column: 1 / span 2;
            grid-row: 2;
            background-color: #FBD7B4;
            border: 2px solid #E67E22;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .player {{
            grid-column: 3 / span 2;
            grid-row: 2;
            background-color: #FBD7B4;
            border: 2px solid #E67E22;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .learning-objectives {{
            grid-column: 1 / span 2;
            grid-row: 3;
            background-color: #D5F5E3;
            border: 2px solid #27AE60;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .narrative {{
            grid-column: 3 / span 2;
            grid-row: 3;
            background-color: #D6EAF8;
            border: 2px solid #3498DB;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .learning-process {{
            grid-column: 1;
            grid-row: 4;
            background-color: #D5F5E3;
            border: 2px solid #27AE60;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .game {{
            grid-column: 2 / span 2;
            grid-row: 4;
            background-color: #FCF3CF;
            border: 2px solid #F1C40F;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .game-objectives {{
            grid-column: 4;
            grid-row: 4;
            background-color: #D6EAF8;
            border: 2px solid #3498DB;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .inspirations {{
            grid-column: 1 / span 2;
            grid-row: 5;
            background-color: #FCF3CF;
            border: 2px solid #F1C40F;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .restrictions {{
            grid-column: 3 / span 2;
            grid-row: 5;
            background-color: #FADBD8;
            border: 2px solid #E74C3C;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .section-title {{
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        
        .section-content {{
            padding-left: 5px;
        }}
        
        .section-content p {{
            margin: 5px 0;
        }}
        
        .icon {{
            margin-right: 5px;
            font-size: 1.2em;
        }}
        
        .amd-section {{
            margin-top: 10px;
            padding-top: 5px;
            border-top: 1px dashed #bbb;
        }}
        
        .amd-title {{
            font-weight: bold;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Row -->
        <div class="header-row">
            <div class="header-cell" style="grid-column: 1 / span 2;">
                <strong>Jogo:</strong> {game_name}
            </div>
            <div class="header-cell">
                <strong>Versão:</strong> 1.0
            </div>
        </div>
        
        <!-- Situation -->
        <div class="situation">
            <div class="section-title">
                <span class="icon">🏠</span> Situação
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('situation', ['• Situação educacional a ser definida']))}
            </div>
        </div>
        
        <!-- Player/Student -->
        <div class="player">
            <div class="section-title">
                <span class="icon">😊</span> Jogador/Aluno
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('player', ['• Perfil do jogador a ser definido']))}
            </div>
        </div>
        
        <!-- Learning Objectives -->
        <div class="learning-objectives">
            <div class="section-title">
                <span class="icon">📚</span> Objetivos de Aprendizado
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('learning-objectives', ['• Objetivos educacionais a serem definidos']))}
            </div>
        </div>
        
        <!-- Narrative -->
        <div class="narrative">
            <div class="section-title">
                <span class="icon">📖</span> Narrativa
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('narrative', ['• Narrativa do jogo a ser definida']))}
            </div>
        </div>
        
        <!-- Learning Process -->
        <div class="learning-process">
            <div class="section-title">
                <span class="icon">📝</span> Processo Lúdico<br>de Aprendizado
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('learning-process', ['• Processo de aprendizagem a ser definido']))}
            </div>
        </div>
        
        <!-- Game (MDA, Interface, examples) -->
        <div class="game">
            <div class="section-title">
                <span class="icon">🎮</span> Jogo<br>(MDA, Interface, exemplos)
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('game', ['• Mecânicas e sistemas de jogo a serem definidos']))}
            </div>
        </div>
        
        <!-- Game Objectives -->
        <div class="game-objectives">
            <div class="section-title">
                <span class="icon">🎯</span> Objetivos do<br>Jogo
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('game-objectives', ['• Objetivos do jogo a serem definidos']))}
            </div>
        </div>
        
        <!-- Inspirations -->
        <div class="inspirations">
            <div class="section-title">
                <span class="icon">💡</span> Inspirações
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('inspirations', ['• Inspirações para o design a serem definidas']))}
            </div>
        </div>
        
        <!-- Restrictions -->
        <div class="restrictions">
            <div class="section-title">
                <span class="icon">⚠️</span> Restrições
            </div>
            <div class="section-content">
                {_format_section_content(sections_content.get('restrictions', ['• Restrições e limitações a serem consideradas']))}
            </div>
        </div>
    </div>
    
    <!-- Generated info -->
    <div style="margin-top: 30px; padding: 20px; border-top: 1px solid #ccc; color: #666; font-size: 0.9em;">
        <p><strong>Gerado pelo Sistema de Design de Jogos Educativos</strong></p>
        <p>Sessão #{session.id} - {session.start_time.strftime('%d/%m/%Y %H:%M')}</p>
        <p>Dissertação de Mestrado - Caio Silva Azeredo - COPPE/UFRJ</p>
    </div>
</body>
</html>"""
    
    return html_template

def _format_section_content(content_list):
    """Formata o conteúdo de uma seção como HTML"""
    if not content_list:
        return '<p>• Conteúdo a ser definido</p>'
    
    formatted_items = []
    for item in content_list:
        if not item.startswith('•'):
            item = f"• {item}"
        formatted_items.append(f"<p>{item}</p>")
    
    return '\n'.join(formatted_items)

def _enhance_sections_with_ai(game_name, socratic, cards, existing_content):
    """Melhora seções com conteúdo gerado por IA"""
    try:
        groq_service = GroqService()
        
        # Construir contexto
        context = f"Jogo: {game_name}\n"
        if socratic:
            context += f"Problema educacional: {socratic.problem}\n"
        if cards:
            context += f"Ideias principais: {', '.join([card.text for card in cards[:3]])}\n"
        
        # Prompt para completar seções
        prompt = f"""Com base no seguinte contexto de um jogo educativo, complete as seções em falta do Endo-GDC:

{context}

Gere conteúdo para as seguintes seções (formato de lista com •):

1. SITUAÇÃO (problemas educacionais que o jogo resolve)
2. JOGADOR/ALUNO (perfil do público-alvo)
3. NARRATIVA (história e ambientação do jogo)
4. PROCESSO LÚDICO DE APRENDIZADO (como o jogo ensina)
5. JOGO/MECÂNICAS (sistemas de jogo e MDA)
6. OBJETIVOS DO JOGO (metas que o jogador deve alcançar)
7. INSPIRAÇÕES (referências e influências)
8. RESTRIÇÕES (limitações e desafios)

Seja específico e use listas com • para cada item."""
        
        result = groq_service.generate_response(prompt, 'section_enhancement')
        
        if result['success']:
            # Parse da resposta (implementação simplificada)
            enhanced_content = existing_content.copy()
            
            # Adicionar conteúdo padrão se ainda vazio
            default_sections = {
                'situation': [f"• Desafio educacional relacionado ao tema de {game_name}"],
                'player': [f"• Estudantes interessados no tema do jogo"],
                'narrative': [f"• Narrativa envolvente relacionada ao contexto educacional"],
                'learning-process': [f"• Aprendizagem através de mecânicas lúdicas"],
                'game': [f"• Mecânicas que reforçam os objetivos educacionais"],
                'game-objectives': [f"• Completar desafios educacionais do jogo"],
                'inspirations': [f"• Jogos educativos de referência na área"],
                'restrictions': [f"• Equilibrar diversão e eficácia educacional"]
            }
            
            for section, default_content in default_sections.items():
                if section not in enhanced_content or not enhanced_content[section]:
                    enhanced_content[section] = default_content
            
            return enhanced_content
        except:
            pass


@gamedesign_bp.route('/export-summary')
def export_summary():
    """Exporta um resumo do projeto (mantido para compatibilidade)"""
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect(url_for('home.index'))
    
    session = BrainstormSession.query.get_or_404(session_id)
    
    # Coletar todos os dados do projeto
    cards = Card.query.filter_by(session_id=session_id).all()
    socratic = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
    objectives = BloomObjective.query.filter_by(session_id=session_id).all()
    notes = GdcNote.query.filter_by(session_id=session_id).all()
    
    # Organizar notas por seção
    notes_by_section = {}
    for note in notes:
        section_name = note.section.name
        if section_name not in notes_by_section:
            notes_by_section[section_name] = []
        notes_by_section[section_name].append(note)
    
    return render_template('gamedesign/summary.html',
                         session=session,
                         cards=cards,
                         socratic=socratic,
                         objectives=objectives,
                         notes_by_section=notes_by_section,
                         sections=ENDO_GDC_SECTIONS)
    except:
        pass
    
    return existing_content