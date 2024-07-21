# #!/bin/bash

# # Change ownership of docker.sock
# chown root:docker /var/run/docker.sock

# # Display permissions of docker.sock
# ls -l /var/run/docker.sock

# # Display Jenkins user ID info
# id jenkins

# # Start Jenkins
# exec /sbin/tini -- /usr/local/bin/jenkins.sh
