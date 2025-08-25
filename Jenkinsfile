pipeline {
    agent any
    environment {
        APP_PORT = "3001"
        DOCKERHUB_REPO = "poojadocker404/python-demo"
        TAG = "${BUILD_NUMBER}"
        SONAR_TOKEN = credentials('sonarcloud-token')
        AZURE_WEBAPP_NAME = 'python-app1'         // Your Azure Web App name
        AZURE_RESOURCE_GROUP = 'RG'              // Azure Resource Group
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
                        sh "docker build -t ${DOCKERHUB_REPO}:${TAG} ."
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

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-pat', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push ${DOCKERHUB_REPO}:${TAG}
                        '''
                    }
                }
            }
        }

        stage('Deploy to Azure Web App for Containers') {
            steps {
                withCredentials([
                  file(credentialsId: 'azure-publish-profile', variable: 'PUBLISH_PROFILE'),
                  usernamePassword(credentialsId: 'docker-hub-pat', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')
                ]) {
                    sh '''
                        # Configure the Web App to use the Docker image from Docker Hub
                        az webapp config container set \
                          --name $AZURE_WEBAPP_NAME \
                          --resource-group $AZURE_RESOURCE_GROUP \
                          --docker-custom-image-name ${DOCKERHUB_REPO}:${TAG} \
                          --docker-registry-server-url https://index.docker.io \
                          --docker-registry-server-user $DOCKER_USER \
                          --docker-registry-server-password $DOCKER_PASS

                        # Optionally enable CI/CD so App Service redeploys on new pushes
                        az webapp deployment container config \
                          --name $AZURE_WEBAPP_NAME \
                          --resource-group $AZURE_RESOURCE_GROUP \
                          --enable-cd true

                        # Restart the app to pull the new image
                        az webapp restart \
                          --name $AZURE_WEBAPP_NAME \
                          --resource-group $AZURE_RESOURCE_GROUP
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up local Docker image"
            sh "docker rmi ${DOCKERHUB_REPO}:${TAG} || true"
        }
    }
}
