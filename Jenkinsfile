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
        
        stage('Install Dependencies') {
            steps {
                script {
                    dir('DataBase2') {
                        // Try to use python3, fall back to python
                        sh '''
                            if command -v python3 &> /dev/null; then
                                PYTHON_CMD=python3
                                PIP_CMD=pip3
                            elif command -v python &> /dev/null; then
                                PYTHON_CMD=python
                                PIP_CMD=pip
                            else
                                echo "Error: Python is not installed"
                                exit 1
                            fi
                            
                            echo "Using Python: $PYTHON_CMD"
                            $PYTHON_CMD --version
                            
                            echo "Installing dependencies..."
                            $PIP_CMD install -r requirements.txt --user
                        '''
                    }
                }
            }
        }

        stage('Verify Models') {
            steps {
                script {
                    dir('DataBase2') {
                        sh '''
                            if command -v python3 &> /dev/null; then
                                PYTHON_CMD=python3
                            else
                                PYTHON_CMD=python
                            fi
                            
                            echo "Running verify_models.py..."
                            $PYTHON_CMD verify_models.py
                        '''
                    }
                }
            }
        }

        stage('Verify API') {
            steps {
                script {
                    dir('DataBase2') {
                        sh '''
                            if command -v python3 &> /dev/null; then
                                PYTHON_CMD=python3
                            else
                                PYTHON_CMD=python
                            fi
                            
                            echo "Running verify_api.py..."
                            $PYTHON_CMD verify_api.py
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
        success {
            echo 'All tests passed! ✓'
        }
        failure {
            echo 'Tests failed! ✗'
        }
    }
}
