from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    # creiamo un oggetto flask con __name__ che arriva daa main.py
    # il web server passerà le richieste inviate dal client a questo oggetto della classe flask
    # utilizzando il protocollo WSGI (web server gateway interface)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sdhfjdshgreghuewrg'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app) # inizializzazione del database dando l'app di flask

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()
        
        login_manager = LoginManager()
        login_manager.login_view = 'auth.login'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

    return app
