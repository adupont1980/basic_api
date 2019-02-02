from flask import Flask

def create_app(config_filename):
    app = Flask(__name__)
    
    from app import api_bp
    app.register_blueprint(api_bp, url_prefix='')

    return app

if __name__ == "__main__":
    app = create_app("config")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)