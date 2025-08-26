from flask import Flask, render_template_string
from flask_wtf import CSRFProtect
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")
metrics = PrometheusMetrics(app)
csrf = CSRFProtect(app)

WELCOME_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🚀 Welcome to DevTools</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: #fff;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px 0;
            text-align: center;
            font-size: 2.5em;
            font-weight: 600;
            letter-spacing: 1px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 2s ease-in-out;
        }

        .card {
            background-color: #7A67EE; /* lavender4 */
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            text-align: center;
            max-width: 650px;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        h1 {
            font-size: 3em;
            margin-bottom: 20px;
        }

        p {
            font-size: 1.2em;
            line-height: 1.6;
        }

        footer {
            background: rgba(0, 0, 0, 0.2);
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <header>
        🛠️ Welcome to DevTools
    </header>

    <main>
        <div class="card">
            <h1>Hello DevOps Enthusiast! 👋</h1>
            <p>DevTools is a leading consulting, licensing and managed services organization dedicated to <strong>DevSecOps</strong> with focus on <strong>Automation</strong> across all platforms.</p>
        </div>
    </main>

    <footer>
        &copy; 2025 DevTools • Built with Flask, Jenkins, Docker & AKS
    </footer>
</body>
</html>
'''

@app.route("/")
def home():
    return render_template_string(WELCOME_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
