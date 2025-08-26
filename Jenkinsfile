pipeline {
    agent any

    environment {
        APP_PORT             = "3001"
        DOCKER_CREDENTIALS   = 'docker-hub-credentials'  // Jenkins credential ID for Docker Hub (username/password)
        IMAGE_NAME           = "poojadocker404/python-demo"
        TAG                  = "${BUILD_NUMBER}"
        SONAR_TOKEN          = credentials('sonarcloud-token')
        AZURE_STORAGE_ACCOUNT = credentials('azure-storage-account')    // Jenkins secret ID for storage account name
        AZURE_SAS_TOKEN      = credentials('azure-sas-token')           // Jenkins secret ID for SAS token
    }

    stages {
        stage('Install Python Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
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

        stage('Build Docker Image') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    retry(2) {
                        sh 'docker build -t $IMAGE_NAME:$TAG .'
                    }
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    timeout(time: 2, unit: 'MINUTES') {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push $IMAGE_NAME:$TAG
                        '''
                    }
                }
            }
        }

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
                    curl --fail http://4.156.43.92:$APP_PORT || exit 1
                '''
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                sh '''
                    echo "Running OWASP ZAP baseline scan using Docker..."

                    docker run --rm --user root -v $PWD:/zap/wrk/:rw -t zaproxy/zap-stable zap-baseline.py \
                        -t http://4.156.43.92:$APP_PORT \
                        -r zap_report.html -x zap_report.xml -J zap_report.json -I
                '''
            }
        }

        stage('Upload ZAP Report to JFrog Artifactory') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'jfrog-cred', usernameVariable: 'JFROG_USER', passwordVariable: 'JFROG_PASS')]) {
                    sh """
                        jf c add my-jfrog-server --url http://130.131.164.192:8082 --user $JFROG_USER --password $JFROG_PASS --interactive=false
                        jf rt upload "zap_report.*" "art-docker-local/zap-reports/${BUILD_NUMBER}/" --server-id=my-jfrog-server
                    """
                }
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
