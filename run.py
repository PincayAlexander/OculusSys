import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

config=os.getenv('FLASK_ENV') or 'development'

app = create_app(config)

if __name__ == "__main__":
    if config == 'development':
        app.run(port = 5000, debug=True)
    else:
        from werkzeug.serving import run_simple
        run_simple('0.0.0.0', 3600, app)