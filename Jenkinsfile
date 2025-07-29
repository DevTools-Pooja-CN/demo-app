pipeline {
    agent any

    environment {
        APP_PORT = "3001"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }

        stage('Deploy and Test') {
            parallel {
                stage('Deploy Container') {
                    steps {
                        sh '''
                            docker rm -f myapp || true
                            docker run -d --name myapp -p 3001:3001 myapp:latest

                            echo "Waiting for app to start..."
                            for i in {1..10}; do
                                if curl --silent http://localhost:$APP_PORT; then
                                    echo "App is up"
                                    break
                                fi
                                echo "Waiting... ($i)"
                                sleep 1
                            done

                            curl --fail http://localhost:$APP_PORT
                        '''
                    }
                }

                stage('Run Tests') {
                    steps {
                        // Ensure dependencies are available in Jenkins environment
                        sh '''
                            pip install --user -r requirements.txt
                            pytest test_app.py
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up..."
            sh 'docker rm -f myapp || true'
        }
    }
}
