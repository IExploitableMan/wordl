# Wordl

Wordl is a Russian word-guessing game inspired by Wordle. Players attempt to guess a 5-letter Russian word within 6 attempts, with feedback provided for each guess.

## Features

- Fully localized for Russian words.
- Simple and intuitive gameplay.
- Feedback on each guess to guide players.
- Responsive design for desktop and mobile.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/IExploitableMan/Wordl.git
    cd wordl
    ```

2. Install dependencies:

    ```sh
    cd backend
    pip install -r requirements.txt
    ```

3. Run the backend:

    ```sh
    python3 main.py
    ```

4. Run http server for the frontend:

    ```sh
    cd ../frontend
    python3 -m http.server 5000
    ```

5. Open your web browser and navigate to `http://localhost:5000`.

6. Enjoy the game!
