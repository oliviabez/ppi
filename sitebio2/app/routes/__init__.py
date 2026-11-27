"""Rotas do SiteBio, organizadas em Blueprints (um por área do site)."""
from .acesso import bp as acesso_bp
from .conteudo import bp as conteudo_bp
from .quiz import bp as quiz_bp
from .perfil import bp as perfil_bp
from .feedback import bp as feedback_bp
from .admin import bp as admin_bp
from .admin_quiz import bp as admin_quiz_bp
from .admin_pagina import bp as admin_pagina_bp

BLUEPRINTS = [acesso_bp, conteudo_bp, quiz_bp, perfil_bp, feedback_bp,
              admin_bp, admin_quiz_bp, admin_pagina_bp]
