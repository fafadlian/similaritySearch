# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python script files
COPY app.py api_client.py similarity_search.py distanceSimilarity.py ageSimilarity.py loc_access.py data_loader.py ./

# Copy the folders with their contents
COPY jsonData/ jsonData/
COPY XMLs/ XMLs/
COPY templates/ templates/
COPY static/ static/
COPY data/ data/

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for the storage path
ENV STORAGE_PATH_JSON=/app/jsonData
ENV STORAGE_PATH_XML=/app/XMLs

# Ensure the jsonData and XMLs folders exist
RUN mkdir -p ${STORAGE_PATH_JSON}
RUN mkdir -p ${STORAGE_PATH_XML}


ENV FLASK_APP=app.py
# ENV FLASK_ENV=production


# Run app.py when the container launches

#Use this for debug
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]

#Use this for Production
# CMD ["gunicorn", "-w", "4", "app:app", "--bind", "0.0.0.0:80"]


