# Peer-to-Peer Hybrid Online Game App

## Project Description
This repository contains the code for a peer-to-peer hybrid online game application. The application simulates an online gaming network consisting of a server and multiple players (users). The interaction between the server and users follows a client-server model, while the interaction between players is peer-to-peer (P2P). The application enforces the following rules:

- Users must connect to the Authentication and Information Server (SAI).
- If not registered, users must create an account with their name, username, and password. User data is stored in a file.
- If already registered, users must authenticate with their username and password.
- Authenticated users have two possible statuses: ACTIVE (online and playing) or INACTIVE (online and waiting for game invites). They can request two types of user lists from the server:
  - LIST-USER-ONLINE: The requesting user receives a list of online users, including their USERNAME, STATUS, IP, and PORT.
  - LIST-USER-PLAYING: The requesting user receives a list of users currently in a game, represented as USERNAME(IP:PORT) X USERNAME(IP:PORT).

- User A can request to start a game (send a GAME_INI message) with any other online user B. The response can be GAME_NEG for declined or GAME_ACK for accepted.
- If accepted, users A and B become players and interact without interference from the SAI until the game ends or someone sends a GAME_OVER message.
- The SAI is only informed about users who are currently playing with each other.
- Players must close their connection when the game ends or if either party requests closure. An ACTIVE (playing) user can receive game requests from other users and can choose to accept (in which case they request closure of the current game) or decline.
- The server keeps track of which users are online and playing at any given moment. Additionally, it logs the following events to the standard output and a log file named "game.log":
  - Date and Time: User X registered.
  - Date and Time: User X connected.
  - Date and Time: User X became unresponsive ("died").
  - Date and Time: User X became INACTIVE (indicating they are available to play with others).
  - Date and Time: User X became ACTIVE (indicating they are playing with another user).
  - Date and Time: Users X and Y are PLAYING.
  - Date and Time: User X disconnected from the network.

## The Game
The application includes an interactive game that can be played between two or more participants. The game's specifics, as well as the protocol for interaction between players (control and data messages exchanged during gameplay), are defined by the development group.

## Installation and Usage
To use this application, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
2. Execute server.py:
   ```bash
   ./server.sh
   
3. Execute client.py:
   ```bash
   ./client.sh

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Authors
- José Augusto Lajo Vieira Vital
