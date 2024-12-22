import socket
import threading

# Tic-Tac-Toe board
board = [' ' for _ in range(9)]

# Check for win
def check_win():
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] and board[condition[0]] != ' ':
            return True, board[condition[0]]
    if ' ' not in board:
        return True, 'Draw'
    return False, None

# Display the board as a string
def display_board():
    return f"""
 {board[0]} | {board[1]} | {board[2]}
---+---+---
 {board[3]} | {board[4]} | {board[5]}
---+---+---
 {board[6]} | {board[7]} | {board[8]}
"""

# Broadcast message to all clients
def broadcast(message):
    for client in clients:
        client.sendall(message.encode())

# Handle player turns
def handle_game():
    global current_player
    broadcast(f"Game starts now!\n{display_board()}")
    while True:
        player_conn = clients[0] if current_player == 'X' else clients[1]
        opponent_conn = clients[1] if current_player == 'X' else clients[0]

        player_conn.sendall("Your turn. Enter a position (1-9): ".encode())
        opponent_conn.sendall("Waiting for the other player's move...\n".encode())

        try:
            move = player_conn.recv(1024).decode().strip()
            if not move.isdigit() or int(move) not in range(1, 10):
                player_conn.sendall("Invalid input. Try again.".encode())
                continue

            position = int(move) - 1
            if board[position] != ' ':
                player_conn.sendall("Position already taken. Try again.".encode())
                continue

            # Make the move
            board[position] = current_player
            win, winner = check_win()
            if win:
                if winner == 'Draw':
                    broadcast(f"Game Over! It's a draw!\n{display_board()}")
                else:
                    broadcast(f"Game Over! Player {winner} wins!\n{display_board()}")
                break

            # Update board and switch player
            broadcast(f"Player {current_player} made a move.\n{display_board()}")
            current_player = 'O' if current_player == 'X' else 'X'

        except (ConnectionResetError, ConnectionAbortedError):
            print(f"A player disconnected. Game aborted.")
            break

# Main server logic
def main():
    global current_player, clients
    current_player = 'X'  # Player X starts
    clients = []

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12345))
    server.listen(2)  # Listen for two players
    print("Server started. Waiting for players...")

    while len(clients) < 2:
        conn, addr = server.accept()
        player_symbol = 'X' if len(clients) == 0 else 'O'
        clients.append(conn)
        print(f"Player {player_symbol} connected from {addr}.")
        conn.sendall(f"Welcome Player {player_symbol}! Waiting for the other player to connect...\n".encode())

    broadcast("Both players connected. Starting the game!")
    handle_game()

    server.close()

if __name__ == "__main__":
    main()
