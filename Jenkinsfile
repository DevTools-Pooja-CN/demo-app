pipeline {
    agent any

    environment {
        APP_PORT = "3001"
        JFROG_REGISTRY = "130.131.164.192:8082"
        JFROG_REPO = "art-docker-local"
        IMAGE_NAME = "${JFROG_REGISTRY}/${JFROG_REPO}/python-demo"
        TAG = "${BUILD_NUMBER}"
        COVERAGE_FILE = "coverage.xml"
        COVERAGE_ARTIFACT_PATH = "coverage/coverage-${BUILD_NUMBER}.xml"
        SONAR_TOKEN= credentials('sonarcloud-token')
    }

    stages {
        stage('Install Python Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

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
                stage('Run Unit Tests') {
                    steps {
                        timeout(time: 3, unit: 'MINUTES') {
                            sh '''
                                export PATH=$PATH:/var/lib/jenkins/.local/bin
                                pytest test_app.py
                            '''
                        }
                    }
                }
                // Code Quality stage (like SonarCloud) can stay here if you still need it
            }
        }

               stage('SonarCloud Scan') {
                    steps {
                        withCredentials([string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')]) {
                            sh """
                                sonar-scanner \\
                                    -Dsonar.projectKey=game-app_demo-app \\
                                    -Dsonar.organization=game-app \\
                                    -Dsonar.token=$SONAR_TOKEN \\
                                    -Dsonar.sources=. \\
                                    -Dsonar.host.url=https://sonarcloud.io
                            """
                        }
                    }
                }
            }

        stage('Publish Artifacts to JFrog') {
            parallel {
                stage('Push Docker Image') {
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

                stage('Upload Coverage Report') {
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
        }

        stage('Deploy to Kubernetes & Smoke Test') {
            steps {
                timeout(time: 4, unit: 'MINUTES') {
                    sh '''
                        # Replace image in deployment YAML with the new tag
                        sed "s|IMAGE_PLACEHOLDER|$IMAGE_NAME:$TAG|g" k8s/deployment.yaml > k8s/deploy-temp.yaml

                        # Apply deployment (keeps existing service/ingress unchanged)
                        kubectl apply -f k8s/deploy-temp.yaml

                        # Restart deployment if same tag is reused (optional but safe)
                        kubectl rollout restart deployment/python-demo

                        # Wait for rollout to complete
                        kubectl rollout status deployment/python-demo

                        # Smoke test via public URL (Nginx exposed)
                        echo "Testing http://20.109.16.207:32256/"

                        sleep 10
                        curl --fail http://20.109.16.207:32256/
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "🎉 Build, test, and Kubernetes deployment successful!"
        }
        failure {
            echo "❌ Something failed. Check logs."
        }
    }
}
