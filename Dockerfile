# Stage 1: Builder
# This stage builds the Python wheel for the application.
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
# Using pip directly as poetry/pdm are not specified for this stage's core build tools
RUN pip install --no-cache-dir --upgrade pip build

# Copy project configuration and source code
# Only copy what's necessary for building the wheel
COPY pyproject.toml README.md ./
COPY src/ src/

# Build the wheel
# This installs dependencies specified in pyproject.toml's [project].dependencies
# The output wheel will be in the /app/dist/ directory
RUN python -m build --wheel --outdir dist .

# Stage 2: Final image
# This stage creates the final, lean image with the application and its runtime dependencies.
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user for security
ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd -r -g ${APP_USER} ${APP_USER}

# Copy the built wheel from the builder stage
COPY --from=builder /app/dist/*.whl .

# Install the application wheel.
# This also installs runtime dependencies declared in pyproject.toml.
# Use a wildcard for the wheel name as it includes version and build tags.
RUN pip install --no-cache-dir *.whl && \
    # Clean up the wheel file after installation to keep the image small
    rm -f *.whl

# The application code is now installed in the Python site-packages directory.
# The CV PDF is expected to be in the project root, which is /app in the container.
# It's recommended to mount the CV PDF as a volume during runtime for flexibility,
# or uncomment the COPY line below if you prefer to bake it into the image.
# Ensure '2025_FranciscoPerezSorrosal_CV_English.pdf' is in the Docker build context if uncommenting.
# COPY 2025_FranciscoPerezSorrosal_CV_English.pdf ./2025_FranciscoPerezSorrosal_CV_English.pdf

# Switch to the non-root user
USER ${APP_USER}

# Expose the port the app runs on
EXPOSE 8000

# Environment variable for ANTHROPIC_API_KEY should be passed during `docker run`
# ENV ANTHROPIC_API_KEY="your_api_key_here" # Do NOT hardcode API keys

# Command to run the application
# The entrypoint 'cv-mcp-server' is defined in pyproject.toml [project.scripts]
# Uvicorn is installed as a dependency of the project.
CMD ["uvicorn", "cv_mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
