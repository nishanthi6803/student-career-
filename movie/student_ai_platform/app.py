from flask import Flask, render_template
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from config import Config
from models.database import db, User
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    jwt = JWTManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.admin_routes import admin_bp
    from routes.api_routes import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('landing.html')

    # Create Database tables
    with app.app_context():
        db.create_all()
        # Seed admin if needed
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin', 
                email='admin@careerai.com', 
                password=generate_password_hash('adminpassword'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
