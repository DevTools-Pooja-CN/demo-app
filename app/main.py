from flask import Flask, render_template_string
from flask_wtf import CSRFProtect
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")  # Required for CSRF (should be kept safe in production)
metrics = PrometheusMetrics(app)
# Enable CSRF protection
csrf = CSRFProtect(app)

WELCOME_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Jenkins-Python App</title>
    <style>
        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1abc9c, #3498db);
            color: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background-color: rgba(0, 0, 0, 0.2);
            padding: 20px;
            text-align: center;
            font-size: 2em;
            font-weight: bold;
        }

        main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 15px;
            text-align: center;
        }

        footer {
            background-color: rgba(0, 0, 0, 0.2);
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <header>
        🔧 Jenkins Python App
    </header>

    <main>
        <div class="card">
            <h1>🚀 Welcome !</h1>
            <p>This Flask app was deployed using a Jenkins pipeline usinf docker.</p>
        </div>
    </main>

    <footer>
        &copy; 2025 Charan_SV DevOps · Powered by Flask & Jenkins
    </footer>
</body>
</html>
'''

@app.route("/")
def home():
    return render_template_string(WELCOME_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
