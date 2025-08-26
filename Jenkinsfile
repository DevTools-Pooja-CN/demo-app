pipeline {
    agent any

    environment {
        APP_PORT     = "3001"
        DOCKER_USER  = credentials('docker-hub-credentials')  // Jenkins secret ID
        DOCKER_PASS  = credentials('docker-hub-password')     // Add if you have separate password
        IMAGE_NAME   = "poojadocker404/python-demo"
        TAG          = "${BUILD_NUMBER}"
        SONAR_TOKEN  = credentials('sonarcloud-token')
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
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
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
                    echo "Running OWASP ZAP baseline scan..."
                    zap-baseline.py -t http://4.156.43.92:$APP_PORT -r zap_report.html -x zap_report.xml -J zap_report.json -I
                '''
            }
        }

        stage('Upload ZAP Report to Azure Blob') {
            steps {
                withCredentials([string(credentialsId: 'azure-storage-account', variable: 'AZURE_STORAGE_ACCOUNT'),
                                 string(credentialsId: 'azure-sas-token', variable: 'AZURE_SAS_TOKEN')]) {
                    sh '''
                        echo "Uploading ZAP report to Azure Blob Storage..."
                        azcopy copy "zap_report.html" "https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/zapreports/zap_report-${BUILD_NUMBER}.html${AZURE_SAS_TOKEN}" --overwrite=true
                        azcopy copy "zap_report.xml" "https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/zapreports/zap_report-${BUILD_NUMBER}.xml${AZURE_SAS_TOKEN}" --overwrite=true
                        azcopy copy "zap_report.json" "https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/zapreports/zap_report-${BUILD_NUMBER}.json${AZURE_SAS_TOKEN}" --overwrite=true
                    '''
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
