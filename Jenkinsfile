pipeline {
    agent any

    environment {
        APP_PORT = "3001"
        JFROG_REGISTRY = "trialsnmz2e.jfrog.io"
        JFROG_REPO = "python-demo-app"
        IMAGE_NAME = "${JFROG_REGISTRY}/${JFROG_REPO}/python-demo"
        TAG = "${BUILD_NUMBER}"
        COVERAGE_FILE = "coverage.xml"
        COVERAGE_ARTIFACT_PATH = "coverage/coverage-${BUILD_NUMBER}.xml"
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

        stage('Parallel: Unit Tests & Code Quality') {
            parallel {
                stage('Run Unit Tests + Coverage') {
                    steps {
                        timeout(time: 3, unit: 'MINUTES') {
                            sh '''
                                pip install --user -r requirements.txt
                                pip install --user coverage
                                export PATH=$PATH:/var/lib/jenkins/.local/bin
                                coverage run -m pytest test_app.py
                                coverage xml -o coverage.xml
                            '''
                        }
                    }
                }

                stage('Code Quality - SonarCloud') {
                    steps {
                        withSonarQubeEnv('SonarCloud') {
                            withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
                                sh '''
                                    /opt/sonar-scanner/bin/sonar-scanner \
                                      -Dsonar.projectKey=CGO-22_demo-app \
                                      -Dsonar.organization=cgo-22 \
                                      -Dsonar.sources=. \
                                      -Dsonar.host.url=https://sonarcloud.io \
                                      -Dsonar.login=$SONAR_TOKEN \
                                      -Dsonar.python.coverage.reportPaths=coverage.xml
                                '''
                            }
                        }
                    }
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

        stage('Push to JFrog Artifactory') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'jfrog-cred', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')]) {
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            echo "$JFROG_PASS" | docker login $JFROG_REGISTRY -u "$JFROG_USER" --password-stdin
                            docker push $IMAGE_NAME:$TAG
                        '''
                    }
                }
            }
        }

        stage('Publish Coverage Report to JFrog') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'jfrog-cred', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')]) {
                    sh '''
                        curl -u "$JFROG_USER:$JFROG_PASS" \
                          -T coverage.xml \
                          "https://$JFROG_REGISTRY/artifactory/$JFROG_REPO/$COVERAGE_ARTIFACT_PATH"
                    '''
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
