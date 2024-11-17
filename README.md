# Zen

## Project Description
Zen is a web application that provides a chatbot interface to help users find their zen. The application is built using React for the frontend and communicates with a backend server to handle chat messages.

## Features
- Chatbot interface
- Popup chat window
- User-friendly design

## Technologies Used
- React
- JavaScript
- Axios
- CSS

## Getting Started

### Prerequisites
- Node.js
- npm or yarn

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/pushanbishi/zen.git
    ```
2. Navigate to the project directory:
    ```bash
    cd zen/src/frontend
    ```
3. Install the dependencies:
    ```bash
    npm install
    ```
    or
    ```bash
    yarn install
    ```

### Running the Application
1. Start the development server:
    ```bash
    npm start
    ```
    or
    ```bash
    yarn start
    ```
2. Open your browser and navigate to `http://localhost:3000`.

## Project Structure
- `src/frontend/src/index.js`: Entry point of the React application.
- `src/frontend/src/App.js`: Main component that includes the "Find Your Zen" button and popup logic.
- `src/frontend/src/ChatComponent.js`: Chatbot component that handles user messages and responses.
- `src/frontend/src/css/`: Directory containing CSS files for styling.

## .gitignore
The `.gitignore` file is used to specify which files and directories should be ignored by Git. The `node_modules` directory is included in this file to prevent it from being committed to the repository.

## License
This project is licensed under the MIT License.