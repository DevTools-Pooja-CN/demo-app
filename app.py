from flask import Flask, render_template_string

app = Flask(__name__)

WELCOME_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Jenkins-Python App</title>
    <style>
        body {
            background: linear-gradient(135deg, #1abc9c, #3498db);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
            text-align: center;
            padding-top: 100px;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 0.2em;
        }
        p {
            font-size: 1.2em;
        }
        .card {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 Hello from Jenkins Pipeline!</h1>
        <p>This Python Flask app was deployed using Jenkins.</p>
    </div>
</body>
</html>
'''

@app.route("/")
def home():
    return render_template_string(WELCOME_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
