
# Use the Jupyter all-spark-notebook as the base image
FROM jupyter/all-spark-notebook:x86_64-spark-3.5.0
# Use root to change write read permission, so spark can create output files
USER root

# Set the working directory in the container
WORKDIR /etl_app

# Copy the files from the current directory on the host to the container
COPY ./scripts/requirements.txt /etl_app/requirements.txt

#RUN chmod -R 777 /etl_app/
# Set environment variables
ENV JUPYTER_ENABLE_LAB=yes

# Install dependencies
RUN pip install -r ./requirements.txt

# Specify the command to run Jupyter Notebook within spark environment
CMD ["start-notebook.sh", "--NotebookApp.token=token"]

# Set the entrypoint script
ENTRYPOINT ["/etl_app/scripts/execute_etl.sh"]