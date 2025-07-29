pipeline {
    agent any

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install --user -r requirements.txt'
            }
        }

        stage('Run App and Test') {
            steps {
                sh '''
                    nohup python3 app.py > app.log 2>&1 &
                    APP_PID=$!
                    sleep 5
                    curl -f http://localhost:3001/
                    kill $APP_PID
                '''
            }
        }
    }
}
