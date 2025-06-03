# Zen

## Project Description
Zen is a backend application that provides a chatbot API to help users find their zen. The application is built using Flask and integrates with Perplexity AI for chat responses. It supports AWS S3 for conversation storage in production environments and uses AWS Parameter Store or local configuration for settings management.

## Features
- Chatbot API endpoint
- Conversation storage in AWS S3 (production)
- Flexible configuration via AWS Parameter Store or local file
- Logging and error handling

## Technologies Used
- Python
- Flask
- Perplexity AI
- AWS S3
- AWS Parameter Store

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- AWS credentials (for production or test environments)

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/pushanbishi/zen.git
    ```
2. Navigate to the backend directory:
    ```bash
    cd zen/src/backend
    ```
3. (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration
- For local development, edit `../../config/zen.properties` with your settings.
- For production or test, ensure AWS Parameter Store is set up with the required parameters.
- Set the environment variable `APP_ENV` to `local`, `test`, or `production` as needed.
- For S3 conversation storage, set the `CONVERSATION_BUCKET` environment variable (production only).

### Running the Application
To run the main Flask application:
```bash
python crisis_line_assistant.py
```
The app will run on port 5001 by default.

### Running the Client
The client is located in the `src/client/` directory. To run the client:
1. Navigate to the client directory:
    ```bash
    cd zen/src/client
    ```
2. Install the client dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the client script:
    ```bash
    python client.py
    ```
   This will start the client, which can interact with the backend API.

## API Endpoints
- `POST /chat`: Send chat messages and receive responses.
- `GET /config?key=...`: Fetch configuration values.

## Project Structure
- `src/backend/crisis_line_assistant.py`: Main Flask application.
- `src/backend/config/`: Configuration helpers and policies.
- `src/client/`: Client code for interacting with the backend.
- `config/zen.properties`: Local configuration file.
- `src/backend/test/`: Backend tests.



## .gitignore
The `.gitignore` file is used to specify which files and directories should be ignored by Git, such as virtual environments and credentials.

## License
This project is licensed under the MIT License.