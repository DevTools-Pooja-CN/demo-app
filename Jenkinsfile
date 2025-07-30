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

        stage('Deploy and Test') {
            parallel {
                stage('Deploy Container') {
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

                stage('Run Tests') {
                    steps {
                        timeout(time: 2, unit: 'MINUTES') {
                            sh '''
                                pip install --user -r requirements.txt
                                pytest test_app.py
                            '''
                        }
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            when {
                branch 'main'  // Only push image if on 'main' branch
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
            echo "🎉 Build and deployment successful!"
            mail to: 'charanv@devtools.in',
             subject: "Jenkins Build Sucess: ${env.JOB_NAME} [#${env.BUILD_NUMBER}]",
             body: "The build Sucess. Check details at: ${env.BUILD_URL}"
        }
        failure {
            echo "❌ Build or test failed."
            mail to: 'charanv@devtools.in',
             subject: "Jenkins Build Failed: ${env.JOB_NAME} [#${env.BUILD_NUMBER}]",
             body: "The build failed. Check details at: ${env.BUILD_URL}"
        }
    }
}
