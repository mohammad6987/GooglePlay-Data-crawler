FROM apache/kafka:latest

# Copy the script into the container
COPY create-topics.sh /create-topics.sh

# Make the script executable
RUN chmod +x /create-topics.sh

# Set the entrypoint
ENTRYPOINT ["/create-topics.sh"]