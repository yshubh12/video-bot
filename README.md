# Video Bot

A Python-based bot that searches, downloads, and uploads videos from platforms like YouTube and automatically deletes local files after upload. The bot monitors a `/videos` directory for new `.mp4` files and handles asynchronous operations for concurrent uploads.

## Features

- Search and download videos from platforms (YouTube, etc.).
- Upload videos via API endpoints.
- Auto-delete local files after upload.
- Monitor the `/videos` directory for new `.mp4` files.
- Async operations for concurrent uploads.

## Installation

### Prerequisites

- Python 3.8+ (or any other compatible version)
- Pip (Python package installer)

### Setting Up the Project

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yshubh12/video-bot.git
    cd video-bot
    ```

2. **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For MacOS/Linux
    venv\Scripts\activate     # For Windows
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure API keys and settings:**
    - Modify the `main.py` file to include your API keys, flic-token, and any platform-specific configuration details.
    - **Important:** Ensure you have the necessary API key/token for uploading videos, e.g., SocialVerse or another platform you intend to use.
   
5. **Configure `yt-dlp`:**
    - **Install `yt-dlp`**:
      ```bash
      pip install yt-dlp
      ```
    - **Optional: Add `yt-dlp` to your System PATH:**
      - Follow the steps for adding `yt-dlp` to your PATH in the previous sections.
    - **Verify installation**:
      ```bash
      yt-dlp --version
      ```
    - **Update `yt-dlp` regularly**:
      ```bash
      yt-dlp -U
      ```

6. **Permissions (if applicable):**
    - Make sure the bot has access to the `/videos` directory and the necessary permissions for downloading, uploading, and deleting files.

7. **Run the bot:**
    ```bash
    python main.py
    ```

## Usage

The bot will continuously monitor the `/videos` directory for new `.mp4` files. Upon detecting a new video, it will:

1. Download the video from the provided platform.
2. Upload it via the API.
3. Automatically delete the original video files after successful upload.

## Directory Structure

- `main.py`: Entry point to the bot, Contains the main logic for downloading, uploading, and file management.
- `requirements.txt`: List of required dependencies.
- `/videos` : IMPORTANT -create this folder inside video-bot
- `/failed_videos` : IMPORTANT -create this folder inside video-bot

## Dependencies

- `yt-dlp`: To download videos from various platforms.
- `requests`: For making HTTP requests (used for uploading videos).
- `asyncio`: To handle asynchronous tasks like concurrent uploads.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## Troubleshooting

- **Logs**: Check the logs in the terminal or add custom logging functionality in `main.py` if needed.
- **Dependencies**: If you encounter issues related to missing dependencies, ensure all packages are correctly installed by running `pip install -r requirements.txt`.
- **Permissions**: Make sure you have sufficient permissions for reading and writing to the `/videos` directory and uploading files to the target API.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
