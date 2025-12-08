pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-u root:root'
        }
    }

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
                        // Python is already available in the Docker image
                        sh 'python --version'
                        sh 'pip --version'
                        
                        // Install dependencies
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    dir('DataBase2') {
                        // Run the model verification script
                        sh 'python verify_models.py'
                        
                        // Run the API verification script
                        sh 'python verify_api.py'
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
