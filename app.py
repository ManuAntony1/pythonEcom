from flask import Flask, redirect, url_for
from models import db, bcrypt
from config import Config
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(product_bp, url_prefix='/product')

@app.route('/')
def home():
    return redirect(url_for('product.index'))

# Debugging: Print all registered routes
with app.app_context():
    print(app.url_map)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
