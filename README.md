# BOT-private-rooms

## Overview
This bot provides a system for managing private voice channels on a Discord server. Users can create, configure, and delete their own private voice channels, while an automated cleanup task removes inactive channels that haven't been used for a specified period.

## Features
- **Create Private Voice Channels**: Users can generate their own private voice channels with a simple command.
- **Channel Configuration**: Adjust settings such as visibility, user limit, and privacy.
- **Automatic Cleanup**: Channels that remain unused for 7 days are automatically deleted.
- **Admin Controls**: Administrators can manage and remove channels manually.
- **Persistent Database**: All channels are stored in an SQLite database for tracking and management.

## Installation
### Requirements
- Python 3.8+
- `disnake` library
- SQLite3
- `python-dotenv`

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/RarchikCreation/BOT-private-rooms.git
   cd BOT-private-rooms
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your bot token:
   ```sh
   TOKEN=your-bot-token
   ```
4. Configure your bot settings in `config.py`:
   ```python
   control_role_id = [1234567890]  # List of role IDs allowed to create rooms
   category_id = 1234567890        # Category ID where voice channels will be created
   ```
5. Run the bot:
   ```sh
   python3 main.py
   ```

## Commands
| Command | Description |
|---------|-------------|
| `/create_room` | Creates a new private voice channel |
| `/delete_room` | Deletes a specified voice channel |
| `/transfer_room` | Transfers a specified voice channel |
| `/edit_room` | Edites a specified voice channel |


