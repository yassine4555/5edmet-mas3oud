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
                // Ensure Python and pip are installed
                sh 'python --version'
                sh 'pip --version'
                
                // Create virtual environment (optional but recommended)
                // sh 'python -m venv venv'
                // sh '. venv/bin/activate'
                
                // Install dependencies
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                // Run the model verification script
                sh 'python verify_models.py'
                
                // You could also run verify_db.py if you have a local postgres
                // but usually pipelines use ephemeral DBs or docker services
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
