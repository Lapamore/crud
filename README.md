# Blog Platform API

This is a simple RESTful API for a blog platform, built with Python, FastAPI, and PostgreSQL. It's fully containerized with Docker and set up for CI/CD with GitHub Actions.

## Features

- **User Management**: Register, login, and manage user profiles.
- **JWT Authentication**: Secure endpoints using JSON Web Tokens.
- **Article Management**: Full CRUD operations for articles.
- **Comments**: Add, view, and delete comments on articles.
- **Dockerized**: Easy setup and deployment using Docker and Docker Compose.
- **CI/CD**: Automated Docker image builds and publishing to GHCR.

## API Documentation

Once the application is running, the interactive API documentation (Swagger UI) is available at [http://localhost:8000/docs](http://localhost:8000/docs).

A live version of the deployed application and its Swagger UI will be available at: [YOUR_RENDER_URL_HERE]

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)
- A GitHub account

### Installation & Running Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<your_username>/<your_repo_name>.git
    cd <your_repo_name>
    ```

2.  **Create an environment file:**
    Copy the example environment file and update the variables if needed.
    ```bash
    cp .env.example .env
    ```

3.  **Build and run the application with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    This command will build the Docker images and start the application and database containers.

4.  **Run database migrations:**
    The first time you start the application, you need to apply the database migrations.
    ```bash
    # Create the migration file (only if you change models)
    docker-compose run --rm app alembic revision --autogenerate -m "Your migration message"

    # Apply the migrations
    docker-compose run --rm app alembic upgrade head
    ```

The application will be running at `http://localhost:8000`.

## Project Structure
```
├── src/                  # Source code
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # API routers (controllers)
│   ├── services/         # Business logic
│   └── schemas/          # Pydantic schemas (data validation)
├── migrations/           # Alembic database migration files
├── .github/
│   └── workflows/        # GitHub Actions configuration
│       └── docker-publish.yaml
├── Dockerfile            # Dockerfile for the application
├── docker-compose.yaml   # Docker Compose file
├── .env.example          # Example environment variables
└── README.md             # Project documentation
```

## Deployment (CI/CD)

This project is configured for continuous integration and deployment using GitHub Actions.

1.  **Build and Publish**: On every push to the `main` branch, a GitHub Action workflow automatically builds a Docker image and pushes it to the GitHub Container Registry (GHCR).

2.  **Deploy to Render**:
    - Create a new "Web Service" on Render and connect your GitHub repository.
    - Choose "Deploy from Docker Registry".
    - Use the image path: `ghcr.io/<your_github_username>/<your_repo_name>:latest`.
    - Add the required environment variables from your `.env` file (e.g., `DATABASE_URL`, `JWT_SECRET`).
    - Render will automatically re-deploy your application whenever a new image is pushed to GHCR.

