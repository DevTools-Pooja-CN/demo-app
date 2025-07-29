pipeline {
    agent any

    environment {
        APP_PORT = "3001"
        APP_LOG = "app.log"
        APP_PID_FILE = "app.pid"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install --user -r requirements.txt'
            }
        }

        stage('Stop Old App If Running') {
            steps {
                sh '''
                    if [ -f $APP_PID_FILE ]; then
                        PID=$(cat $APP_PID_FILE)
                        if ps -p $PID > /dev/null 2>&1; then
                            echo "Stopping previous app running with PID $PID"
                            kill $PID
                        else
                            echo "No running app found with PID $PID"
                        fi
                        rm -f $APP_PID_FILE
                    else
                        echo "No existing PID file found"
                    fi
                '''
            }
        }

        stage('Start App in Background') {
            steps {
                sh '''
                    nohup python3 app.py > $APP_LOG 2>&1 &
                    echo $! > $APP_PID_FILE
                    echo "App started in background with PID $(cat $APP_PID_FILE)"
                '''
            }
        }

        stage('Verify App is Running') {
            steps {
                sh '''
                    curl --fail http://localhost:$APP_PORT/ || {
                        echo "App is not responding on port $APP_PORT"
                        exit 1
                    }
                '''
            }
        }
    }
}
