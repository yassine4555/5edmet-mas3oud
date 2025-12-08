pipeline {
    agent none

    environment {
        // Set environment variables for testing
        // Using ephemeral sqlite DB for testing models
        TESTING = 'true'
        DATABASE_URL = 'sqlite:///test.db'
    }

    stages {
        stage('Checkout') {
            agent any
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                script {
                    dir('DataBase2') {
                        // Check Python availability
                        sh 'python --version'
                        sh 'pip --version'
                        
                        // Install dependencies
                        sh 'pip install -r requirements.txt'
                    }
                }
            }
        }

        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                script {
                    dir('DataBase2') {
                        // First install dependencies again in this stage
                        sh 'pip install -r requirements.txt'
                        
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
