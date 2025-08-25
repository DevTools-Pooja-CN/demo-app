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

        stage('Configure Azure Web App to use Docker Image') {
          steps {
            withCredentials([
              file(credentialsId: 'azure-publish-profile', variable: 'PUBLISH_PROFILE'),
              usernamePassword(credentialsId: 'jfrog-cred', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')
            ]) {
              sh '''
                echo "Using Azure publish profile from file: $PUBLISH_PROFILE"
                
                # Enable continuous deployment (optional)
                az webapp deployment container config --name python-app1 --resource-group RG --enable-cd true
        
                # Configure Azure Web App to pull your custom image from JFrog
                az webapp config container set \
                  --name python-app1 \
                  --resource-group RG \
                  --docker-custom-image-name 130.131.164.192:8082/art-docker-local/python-demo:${BUILD_NUMBER} \
                  --docker-registry-server-url https://130.131.164.192:8082 \
                  --docker-registry-server-user $JFROG_USER \
                  --docker-registry-server-password $JFROG_PASS
        
                # Restart the app to apply changes
                az webapp restart --name python-app1 --resource-group RG
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
