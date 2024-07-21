pipeline {
    agent any

    environment {
        WORKSPACE_DIR = 'workspace'
        FLASK_DIR = "${WORKSPACE_DIR}/flask"
        VENV_PATH = "${FLASK_DIR}/venv"
        FLASK_APP = "${FLASK_DIR}/app.py"
        PATH = "$VENV_PATH/bin:$PATH"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        SONARQUBE_TOKEN = 'sqp_f9d0c566e2b4e306bcac4e8a78f13f5e5bd446a4'
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
                dir(WORKSPACE_DIR) {
                    git branch: 'main', url: 'https://github.com/nickphoon/hello.git'
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                dir(FLASK_DIR) {
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }
        
        stage('Activate Virtual Environment and Install Dependencies') {
            steps {
                dir(FLASK_DIR) {
                    sh '. $VENV_PATH/bin/activate && pip install -r requirements.txt'
                }
            }
        }
        
        stage('OWASP Dependency-Check Vulnerabilities') {
            steps {
                dir(FLASK_DIR) {
                    sh '''
                    $DEPENDENCY_CHECK_HOME/bin/dependency-check.sh \
                    --project "Flask App" \
                    --scan . \
                    --out . \
                    --format ALL \
                    --nvdApiKey '7817ec75-4dd8-41ad-a186-a566708de4f3'
                    '''
                }
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        
        stage('UI Testing') {
            steps {
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
        
        stage('Integration Testing') {
            steps {
                dir(FLASK_DIR) {
                    sh '. $VENV_PATH/bin/activate && pytest --junitxml=integration-test-results.xml'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                dir(FLASK_DIR) {
                    sh 'docker build -t flask-app .'
                }
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    dir(FLASK_DIR) {
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
                    // Stop any running container on port 5000
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop'
                    // Remove the stopped container
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm'
                    // Run the new Flask app container
                    sh 'docker run -d -p 5000:5000 flask-app'
                    
                    sh 'sleep 10'
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
            archiveArtifacts artifacts: "${FLASK_DIR}/dependency-check-report/*.*", allowEmptyArchive: true
            archiveArtifacts artifacts: "${FLASK_DIR}/integration-test-results.xml", allowEmptyArchive: true
        }
    }
}
