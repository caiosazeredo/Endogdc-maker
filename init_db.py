# init_db.py - Inicialização do Banco de Dados
from app import create_app
from extensions import db
from models import BloomTaxonomyLevel, GdcTemplate, GdcSection
import json

# Dados dos níveis da Taxonomia de Bloom
BLOOM_LEVELS = [
    {
        'name': 'Criar',
        'description': 'Juntar elementos para formar um todo coerente ou funcional; reorganizar elementos em um novo padrão ou estrutura.',
        'color': '#8B4513',
        'order': 6,
        'verbs': ['criar', 'desenvolver', 'projetar', 'construir', 'inventar', 'formular']
    },
    {
        'name': 'Avaliar', 
        'description': 'Fazer julgamentos baseados em critérios e padrões.',
        'color': '#FF4500',
        'order': 5,
        'verbs': ['avaliar', 'julgar', 'criticar', 'verificar', 'testar', 'monitorar']
    },
    {
        'name': 'Analisar',
        'description': 'Quebrar material em partes constituintes e determinar como as partes se relacionam entre si.',
        'color': '#FFD700',
        'order': 4,
        'verbs': ['analisar', 'comparar', 'contrastar', 'organizar', 'desconstruir', 'questionar']
    },
    {
        'name': 'Aplicar',
        'description': 'Executar ou usar um procedimento em uma situação específica.',
        'color': '#32CD32',
        'order': 3,
        'verbs': ['aplicar', 'executar', 'implementar', 'demonstrar', 'usar', 'ilustrar']
    },
    {
        'name': 'Compreender',
        'description': 'Construir significado a partir de mensagens instrucionais, incluindo comunicação oral, escrita e gráfica.',
        'color': '#4169E1',
        'order': 2,
        'verbs': ['compreender', 'interpretar', 'exemplificar', 'classificar', 'resumir', 'explicar']
    },
    {
        'name': 'Lembrar',
        'description': 'Recuperar conhecimento relevante da memória de longo prazo.',
        'color': '#8A2BE2',
        'order': 1,
        'verbs': ['lembrar', 'reconhecer', 'listar', 'identificar', 'recuperar', 'nomear']
    }
]

# Seções do Endo-GDC
ENDO_GDC_SECTIONS = [
    {
        'name': 'Jogadores',
        'description': 'Quem são os jogadores target? Idade, perfil, experiência com jogos.',
        'color': '#FFB6C1',
        'position': {'x': 50, 'y': 50, 'width': 200, 'height': 150}
    },
    {
        'name': 'Objetivos de Aprendizagem',
        'description': 'Objetivos educacionais específicos baseados na Taxonomia de Bloom.',
        'color': '#98FB98',
        'position': {'x': 270, 'y': 50, 'width': 200, 'height': 150}
    },
    {
        'name': 'Contexto Educacional',
        'description': 'Ambiente educacional, disciplina, recursos disponíveis.',
        'color': '#87CEEB',
        'position': {'x': 490, 'y': 50, 'width': 200, 'height': 150}
    },
    {
        'name': 'Mecânicas de Jogo',
        'description': 'Regras, sistemas de pontuação, progressão, feedback.',
        'color': '#DDA0DD',
        'position': {'x': 50, 'y': 220, 'width': 200, 'height': 150}
    },
    {
        'name': 'Narrativa',
        'description': 'História, personagens, mundo do jogo, tema.',
        'color': '#F0E68C',
        'position': {'x': 270, 'y': 220, 'width': 200, 'height': 150}
    },
    {
        'name': 'Tecnologia',
        'description': 'Plataforma, ferramentas, recursos técnicos necessários.',
        'color': '#FFA07A',
        'position': {'x': 490, 'y': 220, 'width': 200, 'height': 150}
    },
    {
        'name': 'Avaliação',
        'description': 'Como o aprendizado será medido e avaliado.',
        'color': '#20B2AA',
        'position': {'x': 50, 'y': 390, 'width': 200, 'height': 150}
    },
    {
        'name': 'Recursos',
        'description': 'Orçamento, tempo, equipe, materiais necessários.',
        'color': '#CD853F',
        'position': {'x': 270, 'y': 390, 'width': 200, 'height': 150}
    },
    {
        'name': 'Motivação e Engajamento',
        'description': 'Elementos que mantêm os jogadores motivados e engajados.',
        'color': '#DA70D6',
        'position': {'x': 490, 'y': 390, 'width': 200, 'height': 150}
    }
]

def init_database():
    """Inicializa o banco de dados com dados padrão"""
    app = create_app()
    
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        
        print("Inicializando níveis da Taxonomia de Bloom...")
        init_bloom_levels()
        
        print("Inicializando template do Endo-GDC...")
        init_gdc_template()
        
        print("Banco de dados inicializado com sucesso!")

def init_bloom_levels():
    """Inicializa os níveis da Taxonomia de Bloom"""
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
            print(f"  Adicionado nível: {level_data['name']}")
    
    db.session.commit()

def init_gdc_template():
    """Inicializa o template padrão do Endo-GDC"""
    # Verificar se já existe template padrão
    existing_template = GdcTemplate.query.filter_by(is_default=True).first()
    if existing_template:
        print("  Template padrão já existe, pulando...")
        return
    
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
        print(f"  Adicionada seção: {section_data['name']}")
    
    db.session.commit()

if __name__ == '__main__':
    init_database()