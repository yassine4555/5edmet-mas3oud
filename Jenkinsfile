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
        
        stage('Verify Project Structure') {
            steps {
                script {
                    dir('DataBase2') {
                        // Check if required files exist
                        sh '''
                            echo "Checking project structure..."
                            test -f requirements.txt && echo "✓ requirements.txt found" || exit 1
                            test -f app.py && echo "✓ app.py found" || exit 1
                            test -f verify_models.py && echo "✓ verify_models.py found" || exit 1
                            test -f verify_api.py && echo "✓ verify_api.py found" || exit 1
                            test -d models && echo "✓ models/ directory found" || exit 1
                            test -d routes && echo "✓ routes/ directory found" || exit 1
                            test -d config && echo "✓ config/ directory found" || exit 1
                            echo "All required files and directories are present!"
                        '''
                    }
                }
            }
        }

        stage('List Python Files') {
            steps {
                script {
                    dir('DataBase2') {
                        sh '''
                            echo "Python files in the project:"
                            find . -name "*.py" -not -path "./__pycache__/*" -not -path "./.venv/*" | sort
                        '''
                    }
                }
            }
        }

        stage('Check Requirements') {
            steps {
                script {
                    dir('DataBase2') {
                        sh '''
                            echo "Dependencies listed in requirements.txt:"
                            cat requirements.txt
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
            echo 'Project structure verification passed!'
        }
        failure {
            echo 'Project structure verification failed!'
        }
    }
}
