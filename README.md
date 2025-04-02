# OpenHexa

## Description

OpenHexa Backend and Frontend.

## Changelog

### Backend

For details please refer to the [Backend README](backend/README.md).

### Frontend

For details please refer to the [Frontend README](frontend/README.md).

## How to Run

### Backend

1. Navigate to the backend directory:
    ```sh
    cd backend
    ```
2. Install the required Python dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Run the backend server:
   ```sh
   cp .env.dist .env  # adapt the .env file with the required configuration values
   # Set WORKSPACE_STORAGE_LOCATION to a local directory to use a local storage backend for workspaces
   docker network create openhexa
   docker compose build
   docker compose run app fixtures
   docker compose up
   ```

### Frontend

1. Navigate to the frontend directory:
    ```sh
    cd frontend
    ```
2. Install the required Node.js dependencies:
    ```sh
    npm install
    ```
3. Copy `.env.local.dist` and adapt it to your needs:
    ```sh
    cp .env.local.dist .env.local  # adapt the .env file with the required configuration values
    ```
4. Run the frontend development server:
    ```sh
    npm run dev
    ```

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.