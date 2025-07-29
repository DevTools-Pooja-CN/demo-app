pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install --user -r requirements.txt'
            }
        }

        stage('Start App and Test') {
            steps {
                sh '''
                    nohup python3 app.py > app.log 2>&1 &
                    sleep 5  # wait for the app to start
                    curl http://localhost:3001
                '''
            }
        }
        stage('check'){
            sh 'curl http://localhost:3001'
    }
}
