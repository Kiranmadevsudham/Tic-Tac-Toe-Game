import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))

    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            print(data)
            if "Your turn" in data:
                move = input("Enter your move (1-9): ")
                client.sendall(move.encode())
            elif "Game Over" in data:
                print("Game Over! Exiting...")
                break
        except (ConnectionResetError, ConnectionAbortedError):
            print("Connection to server lost.")
            break

    client.close()

if __name__ == "__main__":
    main()
