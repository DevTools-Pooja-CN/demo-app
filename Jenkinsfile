pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    docker rm -f myapp || true
                    docker run -d --name myapp -p 3001:3001 myapp:latest
                    sleep 5
                    curl http://localhost:3001
                '''
            }
        }
    }
}
