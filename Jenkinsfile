pipeline {
    agent any

    environment {
        // Set environment variables for testing
        // Using ephemeral sqlite DB for testing models
        TESTING = 'true'
        DATABASE_URL = 'sqlite:///test.db'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    dir('DataBase2') {
                        // Check Python availability
                        sh 'python3 --version'
                        sh 'pip3 --version'
                        
                        // Install dependencies
                        sh 'pip3 install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    dir('DataBase2') {
                        // Run the model verification script
                        sh 'python3 verify_models.py'
                        
                        // Run the API verification script
                        sh 'python3 verify_api.py'
                    }
                }
            }
        }
    }

    post {
        always {
            // Clean up
            echo 'Pipeline finished'
        }
        success {
            echo 'Tests Passed!'
        }
        failure {
            echo 'Tests Failed!'
        }
    }
}
