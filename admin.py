from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from src.models.models import db, Product, Category
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def dashboard():
    product_count = Product.query.count()
    category_count = Category.query.count()
    return render_template('admin/dashboard.html', 
                          product_count=product_count,
                          category_count=category_count)

@admin_bp.route('/products')
@login_required
def products():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        image_filename = request.form.get('image_filename')
        
        if not name or not price or not category_id:
            flash('Por favor, preencha todos os campos obrigatórios', 'danger')
            return redirect(url_for('admin.add_product'))
        
        product = Product(
            name=name,
            description=description,
            price=float(price),
            category_id=int(category_id),
            image_filename=image_filename
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Category.query.all()
    return render_template('admin/product_form.html', categories=categories)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.category_id = int(request.form.get('category_id'))
        
        if request.form.get('image_filename'):
            product.image_filename = request.form.get('image_filename')
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Category.query.all()
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/uploads')
    files = [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f)) and f != '.gitkeep']
    return render_template('admin/product_form.html', product=product, categories=categories, files=files)

@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')
        
        if not name or not slug:
            flash('Por favor, preencha todos os campos obrigatórios', 'danger')
            return redirect(url_for('admin.add_category'))
        
        category = Category(
            name=name,
            slug=slug,
            description=description
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Categoria adicionada com sucesso!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html')

@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug')
        category.description = request.form.get('description')
        
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', category=category)

@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Verificar se existem produtos nesta categoria
    if Product.query.filter_by(category_id=id).first():
        flash('Não é possível excluir esta categoria pois existem produtos associados a ela.', 'danger')
        return redirect(url_for('admin.categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Categoria excluída com sucesso!', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            flash('Arquivo enviado com sucesso', 'success')
            return redirect(url_for('admin.upload'))
        else:
            flash('Tipo de arquivo não permitido', 'danger')
            return redirect(request.url)
    
    # Listar arquivos existentes
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    files = os.listdir(upload_folder)
    return render_template('admin/upload.html', files=files)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
