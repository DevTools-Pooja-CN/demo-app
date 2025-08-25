pipeline {
    agent any

    environment {
        APP_PORT        = "3001"
        JFROG_REGISTRY  = "130.131.164.192:8082"
        JFROG_REPO      = "art-docker-local"
        IMAGE_NAME      = "${JFROG_REGISTRY}/${JFROG_REPO}/python-demo"
        TAG             = "${BUILD_NUMBER}"
        SONAR_TOKEN     = credentials('sonarcloud-token')
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
                withCredentials([
                    string(credentialsId: 'sonarcloud-token', variable: 'SONAR_TOKEN')
                ]) {
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
                withCredentials([
                    usernamePassword(credentialsId: 'jfrog-cred', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')
                ]) {
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            echo "$JFROG_PASS" | docker login $JFROG_REGISTRY -u "$JFROG_USER" --password-stdin
                            docker push $IMAGE_NAME:$TAG
                        '''
                    }
                }
            }
        }
/*
        stage('Deploy') {
            steps {
                sh '''
                    echo "Stopping and removing existing container (if any)..."
                    docker rm -f python-demo-container || true

                    echo "Pulling the latest image..."
                    docker pull $IMAGE_NAME:$TAG

                    echo "Starting new container..."
                    docker run -d -p 3001:3001 --name python-demo-container $IMAGE_NAME:$TAG
                '''
            }
        }
*/
    stage('Deploy to AKS') {
            steps {
                sh '''
                    sed "s|IMAGE_PLACEHOLDER|$IMAGE_NAME:$TAG|g" k8s/deployment.yaml > k8s/deploy-temp.yaml
                    kubectl apply -f k8s/deploy-temp.yaml
                    kubectl apply -f k8s/service.yaml || true

                    echo "Waiting for rollout to finish..."
                    kubectl rollout status deployment/python-demo
                '''
            }
        }


        
        stage('Smoke Test') {
            steps {
                sh '''
                    echo "Running smoke test..."
                    sleep 10
                    curl --fail http://20.55.91.91/ || exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Deployed successfully to Azure AKS"
        }
        failure {
            echo "❌ Deployment failed"
        }
    }
}
