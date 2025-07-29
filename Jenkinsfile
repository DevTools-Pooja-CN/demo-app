pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install --user -r requirements.txt'
            }
        }

        stage('VApp is Running') {
            steps {
               sh 'python3 app.py &'
               curl 'http://localhost:3001'
            }
        }
    }
}
