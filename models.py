# models.py - COMPLETO baseado na estrutura real detectada (raiz do projeto)
from extensions import db
from datetime import datetime
from sqlalchemy.dialects.mysql import TEXT, LONGTEXT

class BrainstormSession(db.Model):
    __tablename__ = 'brainstorm_sessions'
    
    # Estrutura real: id, start_time, end_time, status, theme, description, duration_minutes, created_at
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=True, default='active')
    theme = db.Column(db.String(255), nullable=True)
    description = db.Column(TEXT, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True, default=30)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

class Card(db.Model):
    __tablename__ = 'cards'
    
    # Estrutura real: id, session_id, content, category, color, position_x, position_y, created_at, updated_at
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    content = db.Column(TEXT, nullable=False)  # NO BANCO É 'content', NÃO 'text'
    category = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(7), nullable=True)
    position_x = db.Column(db.Float, nullable=True)
    position_y = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    # Propriedade para compatibilidade com código que usa 'text'
    @property
    def text(self):
        return self.content
    
    @text.setter
    def text(self, value):
        self.content = value

class BloomObjective(db.Model):
    __tablename__ = 'bloom_objectives'
    
    # Estrutura real: id, session_id, level_id, content, verb, created_at
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('bloom_taxonomy_levels.id'), nullable=True)
    content = db.Column(TEXT, nullable=False)  # NO BANCO É 'content', NÃO 'text'
    verb = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    
    # Propriedades para compatibilidade
    @property
    def text(self):
        return self.content
    
    @text.setter
    def text(self, value):
        self.content = value
        
    @property
    def level(self):
        # Retorna o nome do nível baseado no level_id
        if self.level_id and self.taxonomy_level:
            return self.taxonomy_level.name
        return None
    
    @level.setter
    def level(self, value):
        # Encontra o level_id baseado no nome
        if value:
            level_obj = BloomTaxonomyLevel.query.filter_by(name=value).first()
            if level_obj:
                self.level_id = level_obj.id

class BloomTaxonomyLevel(db.Model):
    __tablename__ = 'bloom_taxonomy_levels'
    
    # Estrutura real: id, name, description, color, order_level
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(TEXT, nullable=False)
    color = db.Column(db.String(7), nullable=False)
    order_level = db.Column(db.Integer, nullable=False)  # NO BANCO É 'order_level', NÃO 'level_order'
    
    # Relacionamentos
    objectives = db.relationship('BloomObjective', backref='taxonomy_level', lazy=True)
    
    # Propriedade para compatibilidade
    @property
    def level_order(self):
        return self.order_level
    
    @level_order.setter
    def level_order(self, value):
        self.order_level = value

# Correção para SocraticSessionAnswers - Substitua no seu models.py

class SocraticSessionAnswers(db.Model):
    __tablename__ = 'socratic_session_answers'
    
    # Estrutura real: id, session_id, answers_json, created_at, updated_at
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    answers_json = db.Column(LONGTEXT, nullable=False, default='{}')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        # Extrair campos especiais antes de chamar o construtor pai
        problem = kwargs.pop('problem', '')
        justification = kwargs.pop('justification', '')
        impact = kwargs.pop('impact', '')
        motivation = kwargs.pop('motivation', '')
        
        # Chamar construtor pai com campos restantes
        super().__init__(**kwargs)
        
        # Inicializar JSON
        if not self.answers_json:
            self.answers_json = '{}'
        
        # Definir valores
        if problem:
            self.problem = problem
        if justification:
            self.justification = justification
        if impact:
            self.impact = impact
        if motivation:
            self.motivation = motivation
    
    # Propriedades com getters E setters
    @property
    def problem(self):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
            return data.get('problem', '')
        except:
            return ''
    
    @problem.setter
    def problem(self, value):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
        except:
            data = {}
        data['problem'] = value or ''
        self.answers_json = json.dumps(data)
    
    @property
    def justification(self):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
            return data.get('justification', '')
        except:
            return ''
    
    @justification.setter
    def justification(self, value):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
        except:
            data = {}
        data['justification'] = value or ''
        self.answers_json = json.dumps(data)
    
    @property
    def impact(self):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
            return data.get('impact', '')
        except:
            return ''
    
    @impact.setter
    def impact(self, value):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
        except:
            data = {}
        data['impact'] = value or ''
        self.answers_json = json.dumps(data)
    
    @property
    def motivation(self):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
            return data.get('motivation', '')
        except:
            return ''
    
    @motivation.setter
    def motivation(self, value):
        import json
        try:
            data = json.loads(self.answers_json or '{}')
        except:
            data = {}
        data['motivation'] = value or ''
        self.answers_json = json.dumps(data)

class GameGroup(db.Model):
    __tablename__ = 'game_groups'
    
    # Estrutura real: id, session_id, name, description, color, created_at
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(TEXT, nullable=True)
    color = db.Column(db.String(7), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

class GdcTemplate(db.Model):
    __tablename__ = 'gdc_templates'
    
    # Estrutura real: id, session_id, name, description, canvas_data, created_at, updated_at
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(TEXT, nullable=True)
    canvas_data = db.Column(LONGTEXT, nullable=True)  # DADOS DO CANVAS EM JSON
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)

class GdcSection(db.Model):
    __tablename__ = 'gdc_sections'
    
    # Estrutura real: id, template_id, name, description, color, position_data
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('gdc_templates.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(TEXT, nullable=True)
    color = db.Column(db.String(7), nullable=True)
    position_data = db.Column(TEXT, nullable=True)  # POSIÇÕES EM JSON, NÃO CAMPOS SEPARADOS
    
    # Propriedades para compatibilidade
    @property
    def position_x(self):
        import json
        try:
            data = json.loads(self.position_data or '{}')
            return data.get('x', 0)
        except:
            return 0
    
    @position_x.setter
    def position_x(self, value):
        import json
        try:
            data = json.loads(self.position_data or '{}')
        except:
            data = {}
        data['x'] = value
        self.position_data = json.dumps(data)
    
    @property
    def position_y(self):
        import json
        try:
            data = json.loads(self.position_data or '{}')
            return data.get('y', 0)
        except:
            return 0

class GdcNote(db.Model):
    __tablename__ = 'gdc_notes'
    
    # Estrutura real: id, section_id, content, color, position_x, position_y, created_at, updated_at
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('gdc_sections.id'), nullable=False)
    content = db.Column(TEXT, nullable=False)  # NO BANCO É 'content', NÃO 'text'
    color = db.Column(db.String(7), nullable=True)
    position_x = db.Column(db.Float, nullable=True)
    position_y = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    # Propriedade para compatibilidade
    @property
    def text(self):
        return self.content
    
    @text.setter
    def text(self, value):
        self.content = value

class GroqResponse(db.Model):
    __tablename__ = 'groq_responses'
    
    # Estrutura real: id, session_id, prompt, response, model_used, tokens_used, response_time_ms, module_type, created_at
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=True)
    prompt = db.Column(LONGTEXT, nullable=False)
    response = db.Column(LONGTEXT, nullable=False)
    model_used = db.Column(db.String(100), nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)
    response_time_ms = db.Column(db.Integer, nullable=True)
    module_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)