# models.py - Modelos de Dados SQLAlchemy
from extensions import db
from datetime import datetime
from sqlalchemy.dialects.mysql import TEXT, LONGTEXT

class BrainstormSession(db.Model):
    __tablename__ = 'brainstorm_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, default=30)
    theme = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='active')  # active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cards = db.relationship('Card', backref='session', lazy=True)
    game_groups = db.relationship('GameGroup', backref='session', lazy=True)
    socratic_answers = db.relationship('SocraticSessionAnswers', backref='session', lazy=True)
    bloom_objectives = db.relationship('BloomObjective', backref='session', lazy=True)

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    text = db.Column(TEXT, nullable=False)
    color = db.Column(db.String(7), default='#ffd700')  # hex color
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)
    is_ai_generated = db.Column(db.Boolean, default=False)
    group_id = db.Column(db.Integer, db.ForeignKey('game_groups.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameGroup(db.Model):
    __tablename__ = 'game_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(TEXT, nullable=True)
    color = db.Column(db.String(7), default='#87ceeb')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cards = db.relationship('Card', backref='group', lazy=True)

class SocraticSessionAnswers(db.Model):
    __tablename__ = 'socratic_session_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    problem = db.Column(TEXT, nullable=False)
    justification = db.Column(TEXT, nullable=True)
    impact = db.Column(TEXT, nullable=True)
    motivation = db.Column(TEXT, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BloomTaxonomyLevel(db.Model):
    __tablename__ = 'bloom_taxonomy_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(TEXT, nullable=False)
    level_order = db.Column(db.Integer, nullable=False)  # 1-6
    color = db.Column(db.String(7), nullable=False)
    verbs = db.Column(TEXT, nullable=True)  # JSON array of verbs
    
    # Relacionamentos
    objectives = db.relationship('BloomObjective', backref='taxonomy_level', lazy=True)

class BloomObjective(db.Model):
    __tablename__ = 'bloom_objectives'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    text = db.Column(TEXT, nullable=False)
    level = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False)
    is_ai_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GdcTemplate(db.Model):
    __tablename__ = 'gdc_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(TEXT, nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    sections = db.relationship('GdcSection', backref='template', lazy=True)

class GdcSection(db.Model):
    __tablename__ = 'gdc_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('gdc_templates.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(TEXT, nullable=True)
    background_color = db.Column(db.String(7), default='#ffffff')
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)
    width = db.Column(db.Float, default=200)
    height = db.Column(db.Float, default=150)
    order_index = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    notes = db.relationship('GdcNote', backref='section', lazy=True)

class GdcNote(db.Model):
    __tablename__ = 'gdc_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('gdc_sections.id'), nullable=False)
    text = db.Column(TEXT, nullable=False)
    color = db.Column(db.String(7), default='#ffff99')
    position_x = db.Column(db.Float, default=0)
    position_y = db.Column(db.Float, default=0)
    is_ai_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroqResponse(db.Model):
    __tablename__ = 'groq_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('brainstorm_sessions.id'), nullable=True)
    prompt = db.Column(LONGTEXT, nullable=False)
    response = db.Column(LONGTEXT, nullable=False)
    model_used = db.Column(db.String(100), nullable=False)
    tokens_used = db.Column(db.Integer, nullable=True)
    response_time_ms = db.Column(db.Integer, nullable=True)
    module_type = db.Column(db.String(50), nullable=False)  # brainstorm, socratic, bloom, gamedesign
    created_at = db.Column(db.DateTime, default=datetime.utcnow)