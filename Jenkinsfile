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
                sh '''
                    nohup python3 app.py > app.log 2>&1 &
                    echo $! > app.pid
                    disown
                '''
            }
        }

        stage('Test App') {
            steps {
                sh '''
                    sleep 5  # Give app time to start
                    curl http://localhost:3001
                '''
            }
        }
    }

    post {
        always {
            sh '''
                if [ -f app.pid ]; then
                    kill $(cat app.pid) || true
                fi
            '''
        }
    }
}
