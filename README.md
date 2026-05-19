# tcp-guessing-game# TCP Guessing Game

A client-server number guessing game over TCP sockets in Python. The client uses binary search to find the secret number in O(log n) guesses.

## Features

- Server picks a random number (1-100) and handles multiple clients via non-blocking I/O (select)
- Client uses binary search - finds the number in at most 7 guesses
- Binary message protocol using Python struct
- Graceful disconnect and error handling

## Tech Stack

Python, TCP sockets, struct, select

## How to Run

Start the server:
```
python server.py <host> <port>
```
Start the client:
```
python client.py <host> <port>
```

## Author

Rustam Kazimov - [github.com/rustamkazimov6-crypto](https://github.com/rustamkazimov6-crypto)
