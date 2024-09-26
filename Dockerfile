FROM python@sha256:80619a5316afae7045a3c13371b0ee670f39bac46ea1ed35081d2bf91d6c3dbd

# Prevent Python from writing .pyc files and force it to buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the Pipfile and Pipfile.lock into the container and install dependencies
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --deploy

# Create a non-root user to run the application
RUN useradd --create-home appuser

# Set work directory
WORKDIR /home/appuser

# Copy the rest of the application code
COPY . .

# Adjust ownership and permissions for the appuser to read/write files
RUN chown -R appuser:appuser /home/appuser && chmod -R 755 /home/appuser

# Switch to non-root user
USER appuser

# Expose the default FastAPI port
EXPOSE 8000

# Run the FastAPI application
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]