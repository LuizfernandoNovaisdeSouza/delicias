from flask import Blueprint, render_template
from src.models.models import Product, Category

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    featured_products = Product.query.limit(3).all()
    categories = Category.query.all()
    return render_template('home.html', featured_products=featured_products, categories=categories)

@public_bp.route('/menu')
def menu():
    categories = Category.query.all()
    return render_template('menu.html', categories=categories)

@public_bp.route('/categoria/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, products=products)

@public_bp.route('/contato')
def contact():
    return render_template('contato.html')
