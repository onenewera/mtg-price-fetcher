from src.app import app as application
from flask_cors import CORS

CORS(application, resources={r"/*": {"origins": "*"}})

@application.route("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)
