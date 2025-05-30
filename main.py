import sys
import os
import secrets
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import datetime

# Configuração do caminho do sistema
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importação dos modelos e blueprints
from src.models.models import db, User, Category, Product
from src.routes.public import public_bp
from src.routes.admin import admin_bp
from src.routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    
    # Configuração do aplicativo
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Inicialização do banco de dados
    db.init_app(app)
    
    # Configuração do Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registro dos blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Contexto global para templates
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.datetime.now().year,
            'site_name': 'Delícias da Fa',
            'categories': Category.query.all()
        }
    
    # Criação das tabelas e dados iniciais
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            
            # Criar categorias iniciais
            categories = [ 
                {'name': 'Bolos Simples', 'slug': 'bolos-simples', 'description': 'Bolos tradicionais com sabores clássicos e irresistíveis.'},
                {'name': 'Bolos com Cobertura', 'slug': 'bolos-com-cobertura', 'description': 'Bolos especiais com coberturas deliciosas e decorações caprichadas.'},
                {'name': 'Bolos Piscininha', 'slug': 'bolos-piscininha', 'description': 'Nossos famosos bolos piscininha com recheio cremoso e cobertura especial.'},
                {'name': 'Bolos Vulcão', 'slug': 'bolos-vulcao', 'description': 'Surpreendente bolo vulcão com recheio que derrete na boca.'},
                {'name': 'Bolos Recheados', 'slug': 'bolos-recheados', 'description': 'Bolos com camadas de recheios especiais para momentos inesquecíveis.'},
              ]
            
            for cat_data in categories:
                if not Category.query.filter_by(slug=cat_data['slug']).first():
                    category = Category(**cat_data)
                    db.session.add(category)
            
            db.session.commit()
            
            # Adicionar alguns produtos de exemplo
            sample_products = [
                {
                    'name': 'Bolo de Chocolate', 
                    'description': 'Bolo macio de chocolate, feito com cacau de qualidade e muito amor.',
                    'price': 35.00,
                    'category_id': 1,
                    'image_filename': 'placeholder-bolo-simples1.jpg'
                },
                {
                    'name': 'Bolo de Cenoura com Chocolate', 
                    'description': 'Tradicional bolo de cenoura com cobertura de chocolate cremoso.',
                    'price': 45.00,
                    'category_id': 2,
                    'image_filename': 'placeholder-bolo-cobertura2.jpg'
                },
                {
                    'name': 'Piscininha de Leite Ninho', 
                    'description': 'Bolo com recheio cremoso de leite ninho e cobertura especial.',
                    'price': 60.00,
                    'category_id': 3,
                    'image_filename': 'placeholder-bolo-piscininha1.jpg'
                }
            ]
            
            for prod_data in sample_products:
                if not Product.query.filter_by(name=prod_data['name']).first():
                    product = Product(**prod_data)
                    db.session.add(product)
            
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
