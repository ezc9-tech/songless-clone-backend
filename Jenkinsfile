pipeline {
    agent any

    stages {
        stage('Environment Check') {
            steps {
                echo 'Jenkins pipeline is running successfully.'

                sh '''
                    echo "===== SYSTEM INFO ====="
                    whoami
                    pwd
                    uname -a
                '''
            }
        }

        stage('Docker Check') {
            steps {
                sh '''
                    echo "===== DOCKER VERSION ====="
                    docker --version

                    echo "===== RUNNING TEST CONTAINER ====="
                    docker run --rm hello-world
                '''
            }
        }
    }
}
