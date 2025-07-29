pipeline {
    agent any
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install --user -r requirements.txt'
            }
        }
        stage('Run App') {
            steps {
                sh 'python3 app.py'
            }
        }
    }
}
