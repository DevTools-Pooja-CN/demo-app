pipeline {
    agent any

    environment {
        APP_PORT = "3001"
        IMAGE_NAME = "charan30/python-demo-app"
        TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    retry(2) {
                        sh 'docker build -t $IMAGE_NAME:$TAG .'
                    }
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    sh '''
                        pip install --user -r requirements.txt
                        pytest test_app.py
                    '''
                }
            }
        }

        stage('Code Quality - SonarCloud') {
             tools {
                    sonarQube 'SonarScanner'
            }
            steps {
                withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=CGO-22_demo-app \
                          -Dsonar.organization=cgo-22 \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=https://sonarcloud.io \
                          -Dsonar.login=$SONAR_TOKEN
                    '''
                }
            }
        }

        stage('Deploy and Smoke Test') {
            steps {
                timeout(time: 3, unit: 'MINUTES') {
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
        }

        stage('Approval to Push') {
            steps {
                script {
                    def userInput = input message: 'Do you want to push the image to Docker Hub?', ok: 'Continue',
                        parameters: [choice(name: 'Push', choices: ['Yes', 'No'], description: 'Select Yes to proceed')]

                    if (userInput == 'No') {
                        echo "Skipping Docker Hub push as per user input."
                        env.SKIP_PUSH = "true"
                    } else {
                        env.SKIP_PUSH = "false"
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            when {
                allOf {
                    branch 'main'
                    expression { return env.SKIP_PUSH != "true" }
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push $IMAGE_NAME:$TAG
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Build, test, and deployment successful!"
        }
        failure {
            echo "❌ Build or test failed."
        }
    }
}
