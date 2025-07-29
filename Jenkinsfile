pipeline {
    agent any

    environment {
        APP_PORT = "3001"
        IMAGE_NAME = "charan30/python-demo-app"
        TAG = "${BUILD_NUMBER}"  // You can also use "latest" or a Git SHA
    }

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$TAG .'
            }
        }

        stage('Deploy and Test') {
            parallel {
                stage('Deploy Container') {
                    steps {
                        sh '''
                            docker rm -f myapp || true
                            docker run -d --name myapp -p $APP_PORT:$APP_PORT $IMAGE_NAME:$TAG

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
                        sh '''
                            pip install --user -r requirements.txt
                            pytest test_app.py
                        '''
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push $IMAGE_NAME:$TAG
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up..."
        }
    }
}
