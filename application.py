from src.app import app as application
from flask_cors import CORS

# enable CORS on the exported Flask app
CORS(application, resources={r"/*": {"origins": "*"}})

@application.route("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    # local dev only; Railway will use gunicorn via Procfile
    application.run(host="0.0.0.0", port=5000, debug=True)
