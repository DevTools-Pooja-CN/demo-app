pipeline {
    agent any
    environment {
        APP_PORT = "3001"
        JFROG_REGISTRY = "130.131.164.192:8082"
        JFROG_REPO = "art-docker-local"
        IMAGE_NAME = "${JFROG_REGISTRY}/${JFROG_REPO}/python-demo"
        TAG = "${BUILD_NUMBER}"
        SONAR_TOKEN = credentials('sonarcloud-token')
        AZURE_WEBAPP_NAME = 'python-app1'   // Your Azure Web App name
        AZURE_RESOURCE_GROUP = 'RG'   // Your Azure Resource Group (not mandatory with publish profile but good to have)
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
                        sh "docker build -t ${IMAGE_NAME}:${TAG} ."
                    }
                }
            }
        }
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
        stage('Push Docker Image to JFrog') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'jfrog-cred', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')]) {
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            echo "$JFROG_PASS" | docker login $JFROG_REGISTRY -u "$JFROG_USER" --password-stdin
                            docker push ${IMAGE_NAME}:${TAG}
                        '''
                    }
                }
            }
        }
        stage('Deploy to Azure Web App') {
            steps {
                withCredentials([file(credentialsId: 'azure-publish-profile', variable: 'PUBLISH_PROFILE')]) {
                    sh '''
                        # Install Azure CLI if not already installed, or ensure it's available

                        echo "Logging into Azure Web App using publish profile..."
                        az webapp deployment container config --name ${AZURE_WEBAPP_NAME} --resource-group ${AZURE_RESOURCE_GROUP} --enable-cd true

                        echo "Setting container image from private registry..."
                        az webapp config container set --name ${AZURE_WEBAPP_NAME} --resource-group ${AZURE_RESOURCE_GROUP} \\
                            --docker-custom-image-name ${IMAGE_NAME}:${TAG} \\
                            --docker-registry-server-url https://${JFROG_REGISTRY} \\
                            --docker-registry-server-user $JFROG_USER \\
                            --docker-registry-server-password $JFROG_PASS

                        echo "Restarting Azure Web App..."
                        az webapp restart --name ${AZURE_WEBAPP_NAME} --resource-group ${AZURE_RESOURCE_GROUP}
                    '''
                }
            }
        }
    }
    post {
        always {
            echo "Cleaning up Docker images"
            sh "docker rmi ${IMAGE_NAME}:${TAG} || true"
        }
    }
}
