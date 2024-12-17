from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash
from models import Product, db

product_bp = Blueprint('product', __name__)

@product_bp.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    products = Product.query.all()
    return render_template('product_list.html', products=products)

@product_bp.route('/cart')
def cart():
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

@product_bp.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))  # Redirect if user is not logged in

    # Fetch cart from session
    cart = session.get('cart', [])
    product = Product.query.get(product_id)

    # Add product to the cart if it exists
    if product and not any(item['id'] == product.id for item in cart):
        cart.append({"id": product.id, "name": product.name, "price": product.price})
        session['cart'] = cart  # Update session with new cart
        flash(f"{product.name} added to cart!", "success")
    else:
        flash("Product not found or already in cart.", "error")

    return redirect(url_for('product.index'))

@product_bp.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('checkout.html', cart=cart, total=total)

@product_bp.route('/api/add_product', methods=['POST'])
def add_product():
    """
    API to add a new product to the database.
    """
    data = request.get_json()  # Get JSON data from the request
    
    # Validate request data
    name = data.get('name')
    price = data.get('price')

    if not name or not price:
        return jsonify({"error": "Name and price are required!"}), 400

    try:
        # Create a new product instance
        new_product = Product(name=name, price=float(price))
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({"message": "Product added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)  # Remove the 'cart' from the session
    flash("Cart has been cleared.", "success")
    return redirect(url_for('product.cart'))
