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
                    // Change to DataBase2 directory
                    dir('DataBase2') {
                        // Check Python version (try python3 first, common in Docker)
                        sh '''
                            if command -v python3 &> /dev/null; then
                                echo "Using python3"
                                python3 --version
                                python3 -m pip --version || echo "pip not found, attempting install"
                            elif command -v python &> /dev/null; then
                                echo "Using python"
                                python --version
                                python -m pip --version || echo "pip not found"
                            else
                                echo "ERROR: Python not found!"
                                exit 1
                            fi
                        '''
                        
                        // Install dependencies
                        sh '''
                            if command -v python3 &> /dev/null; then
                                python3 -m pip install --user -r requirements.txt || pip3 install --user -r requirements.txt
                            else
                                python -m pip install --user -r requirements.txt || pip install --user -r requirements.txt
                            fi
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    dir('DataBase2') {
                        // Run the model verification script
                        sh '''
                            if command -v python3 &> /dev/null; then
                                python3 verify_models.py
                            else
                                python verify_models.py
                            fi
                        '''
                        
                        // Run the API verification script
                        sh '''
                            if command -v python3 &> /dev/null; then
                                python3 verify_api.py
                            else
                                python verify_api.py
                            fi
                        '''
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
