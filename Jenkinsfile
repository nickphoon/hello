pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        FLASK_APP = 'app.py'  // Correct path to the Flask app
        PATH = "$VENV_PATH/bin:$PATH"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        SONARQUBE_TOKEN = 'sqp_f9d0c566e2b4e306bcac4e8a78f13f5e5bd446a4'  // Set your new SonarQube token here
        DEPENDENCY_CHECK_HOME = '/var/jenkins_home/tools/org.jenkinsci.plugins.DependencyCheck.tools.DependencyCheckInstallation/OWASP_Dependency-Check/dependency-check'
    }
    
    stages {
        stage('Check Docker') {
            steps {
                sh 'docker --version'
            }
        }
        
        stage('Clone Repository') {
            steps {
                
                    git branch: 'main', url: 'https://github.com/nickphoon/hello.git'
                
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                dir('flask') {
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }
        
        stage('Activate Virtual Environment and Install Dependencies') {
            steps {
                dir('flask') {
                    sh '. $VENV_PATH/bin/activate && pip install -r requirements.txt'
                }
            }
        }
        
        stage('OWASP Dependency-Check Vulnerabilities') {
    steps {
        dependencyCheck additionalArguments: ''' 
                    -o './'
                    -s './'
                    -f 'ALL' 
                    --prettyPrint
                    --nvdApiKey '7817ec75-4dd8-41ad-a186-a566708de4f3' ''', odcInstallation: 'OWASP Dependency-Check Vulnerabilities'
        
        dependencyCheckPublisher pattern: 'dependency-check-report.xml'
    }
}
    stage('Build Flask Image') {
            steps {
                dir('flask') {
                    // Stop and remove the existing flask-app container if it exists
                    sh '''
                    CONTAINER_ID=$(docker ps -aq --filter name=flask-app-test)
                    if [ -n "$CONTAINER_ID" ]; then
                        echo "Stopping existing container: $CONTAINER_ID"
                        docker stop $CONTAINER_ID || true
                        echo "Removing existing container: $CONTAINER_ID"
                        docker rm $CONTAINER_ID || true
                    else
                        echo "No existing container found"
                    fi
                    '''
                    // Build the new flask-app image
                    sh 'docker build -t flask-app .'
                }
            }
        }

        stage('Build Flask App') {
            steps {
                script {
                    // Run the Flask app container
                    sh 'docker run -d -p 5000:5000 --name flask-app-test flask-app'
                    // Give the server a moment to start
                    sh 'sleep 10'
                }
            }
        }

        
        stage('UI Testing') {
            steps {
                dir('flask') {
                script {
                    // Start the Flask app in the background
                    sh '. $VENV_PATH/bin/activate && FLASK_APP=$FLASK_APP flask run &'
                    // Give the server a moment to start
                    sh 'sleep 5'
                    // Debugging: Check if the Flask app is running
                    sh 'curl -s http://127.0.0.1:5000 || echo "Flask app did not start"'
                    
                    // Test a strong password
                    sh '''
                    curl -s -X POST -F "password=StrongPass123" http://127.0.0.1:5000 | grep "Welcome"
                    '''
                    
                    // Test a weak password
                    sh '''
                    curl -s -X POST -F "password=password" http://127.0.0.1:5000 | grep "Password does not meet the requirements"
                    '''
                    // Stop the Flask app
                    sh 'pkill -f "flask run"'
                }
                }
            }
        }
        
        stage('Integration Testing') {
            steps {
                dir('flask') {
                    sh '. $VENV_PATH/bin/activate && pytest --junitxml=integration-test-results.xml'
                }
            }
        }
        
        
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    dir('flask') {
                        sh '''
                        ${SONARQUBE_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=Quiz \
                        -Dsonar.sources=. \
                        -Dsonar.inclusions=app.py \
                        -Dsonar.host.url=http://sonarqube:9000 \
                        -Dsonar.login=${SONARQUBE_TOKEN}
                        '''
                    }
                }
            }
        }
        
        stage('Deploy Flask App') {
            steps {
                script {
                    echo 'Deploying Flask App...'
                    // Stop and remove the flask-app container if it exists
                    sh '''
                    CONTAINER_ID=$(docker ps -aq --filter name=flask-app)
                    if [ -n "$CONTAINER_ID" ]; then
                        echo "Stopping existing container: $CONTAINER_ID"
                        docker stop $CONTAINER_ID || true
                        echo "Removing existing container: $CONTAINER_ID"
                        docker rm $CONTAINER_ID || true
                    else
                        echo "No existing container found"
                    fi
                    '''
                    
                    sh 'docker run -d -p 5000:5000 --name flask-app flask-app'
                }
            }
        }
    }
    }
    
    post {
        failure {
            script {
                echo 'Build failed, not deploying Flask app.'
            }
        }
        always {
            archiveArtifacts artifacts: 'workspace/dependency-check-report/*.*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'workspace/integration-test-results.xml', allowEmptyArchive: true
        }
    }
}
