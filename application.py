from src.app import app as application
from flask_cors import CORS

if __name__ == '__main__':
    application.run()

CORS(application, resources={r"/*": {"origins": "*"}})

@application.route("/healthz")
def healthz():
    return {"status": "ok"}