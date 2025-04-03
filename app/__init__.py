from flask import Flask
from flask.logging import default_handler
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize logging
    app.logger.removeHandler(default_handler)
    
    # Register blueprints
    from app.rates import bp as rates_bp
    app.register_blueprint(rates_bp, url_prefix='/rates')
    
    from app.labels import bp as labels_bp
    app.register_blueprint(labels_bp, url_prefix='/labels')
    
    from app.pickup import bp as pickup_bp
    app.register_blueprint(pickup_bp, url_prefix='/pickup')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    return app
