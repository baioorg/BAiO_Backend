# Use an official Python runtime as a parent image
FROM python:3.12

# Copy and install dependencies
COPY requirements.txt /BAiO_Backend/

# Set working directory
WORKDIR /BAiO_Backend

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project
COPY . /BAiO_Backend

# Expose the Gunicorn port
EXPOSE 8000

# collect all static files to the root directory - mainly for admin panel
RUN python manage.py collectstatic --no-input

# migrate db
RUN python manage.py migrate

# Run Gunicorn
CMD ["gunicorn", "BAiO_Backend.wsgi:application", "--bind", "0.0.0.0:8000"]

############### gunicorn serves the django application on port 8000