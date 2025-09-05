from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from flask import jsonify   


db = SQLAlchemy()
migrate = Migrate()
 
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'una_clave_muy_secreta'  # cambia esto por algo seguro

    #CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://192.168.1.170:8080"}})
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://172.168.0.93:8080"}})

    jwt = JWTManager(app) #Inicializar gestor de JWT

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print(f"Token inválido: {error_string}")
        return jsonify({"msg": "Token inválido o mal formado"}), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        print(f"Falta token o autorización: {error_string}")
        return jsonify({"msg": "Falta token o autorización"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print("Token expirado")
        return jsonify({"msg": "Token expirado"}), 401

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import citas
    app.register_blueprint(citas.bp)
    
    from app.routes import usuarios
    app.register_blueprint(usuarios.bp)

    from app.routes import tecnicos
    app.register_blueprint(tecnicos.bp)

    from app.routes import bicis
    app.register_blueprint(bicis.bp)

   


    return app
