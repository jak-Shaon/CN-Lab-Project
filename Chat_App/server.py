import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

HOST = '127.10.10.1'
PORT = 8890
LISTENER_LIMIT = 5
active_clients = []

server = None
is_running = False

DARK_GREY = '#333'
MEDIUM_GREY = '#ccc'
OCEAN_BLUE = '#3498db'
WHITE = "#fff"
BLACK = "#000000"
FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 12)
SMALL_FONT = ("Monaco", 10)

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

def update_client_list():
    client_list_box.config(state=tk.NORMAL)
    client_list_box.delete(1.0, tk.END)
    for client in active_clients:
        client_list_box.insert(tk.END, client[0] + '\n')
    client_list_box.config(state=tk.DISABLED)

def listen_for_messages(client, username):
    while is_running:
        try:
            message = client.recv(2048).decode('utf-8')
            if message:
                if message.startswith("@"):
                    recipient, personal_msg = message.split(": ", 1)
                    recipient = recipient[1:]
                    send_personal_message(username, recipient, personal_msg)
                else:
                    final_msg = username + '~' + message
                    add_message(f"[{username}] {message}")
                    send_messages_to_all(final_msg)
            else:
                remove_client(client, username)
        except:
            remove_client(client, username)
            break

def send_message_to_client(client, message):
    client.sendall(message.encode())

def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

def send_personal_message(sender, recipient, message):
    for user in active_clients:
        if user[0] == recipient:
            final_msg = f"@{sender}: {message}"
            send_message_to_client(user[1], final_msg)
            return
    # If recipient is not found, notify the sender
    for user in active_clients:
        if user[0] == sender:
            send_message_to_client(user[1], f"[SERVER] User {recipient} not found")

def remove_client(client, username=None):
    for user in active_clients:
        if user[1] == client:
            if username is None:
                username = user[0]
            active_clients.remove(user)
            update_client_list()
            add_message(f"[SERVER] {username} has left the chat")
            send_messages_to_all(f"[SERVER] {username} has left the chat")
            break
    client.close()

def kick_client(username):
    for user in active_clients:
        if user[0] == username:
            client_socket = user[1]
            client_socket.sendall(f"[SERVER] You have been kicked from the chat".encode())
            active_clients.remove(user)
            update_client_list()
            add_message(f"[SERVER] {username} has been kicked from the chat")
            send_messages_to_all(f"[SERVER] {username} has been kicked from the chat")
            client_socket.close()
            break
    else:
        add_message(f"[SERVER] User {username} not found")

def client_handler(client):
    while is_running:
        try:
            username = client.recv(2048).decode('utf-8')
            if username:
                active_clients.append((username, client))
                add_message(f"[SERVER] {username} joined the chat")
                update_client_list()
                prompt_message = "SERVER~" + f"{username} added to the chat"
                send_messages_to_all(prompt_message)
                threading.Thread(target=listen_for_messages, args=(client, username)).start()
                break
            else:
                add_message("Client username is empty")
        except:
            continue

def start_server():
    global server, is_running

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen(LISTENER_LIMIT)
        is_running = True
        add_message(f"[SERVER] Running on {HOST}:{PORT}")
        threading.Thread(target=accept_clients).start()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("Error", f"Unable to start the server: {e}")

def stop_server():
    global server, is_running
    is_running = False
    for client in active_clients:
        client[1].close()
    active_clients.clear()
    update_client_list()
    if server:
        server.close()
    add_message("[SERVER] Server stopped")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def accept_clients():
    global server
    while is_running:
        try:
            client, address = server.accept()
            add_message(f"[SERVER] Connected to {address[0]}:{address[1]}")
            threading.Thread(target=client_handler, args=(client,)).start()
        except:
            break

def on_closing():
    if is_running:
        stop_server()
    root.destroy()

# GUI setup
root = tk.Tk()
root.title("Server")
root.geometry("500x600")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)

top_frame = tk.Frame(root, bg=DARK_GREY)
top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

message_box = scrolledtext.ScrolledText(top_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=BLACK, state=tk.DISABLED, height=15, width=55)
message_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

client_list_box = scrolledtext.ScrolledText(top_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=BLACK, state=tk.DISABLED, height=14, width=20)
client_list_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

button_frame = tk.Frame(root, bg=DARK_GREY)
button_frame.pack(fill=tk.X, padx=10, pady=10)

start_button = tk.Button(button_frame, text="Start Server", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=start_server)
start_button.pack(side=tk.LEFT, padx=5, pady=5)

stop_button = tk.Button(button_frame, text="Stop Server", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, state=tk.DISABLED, command=stop_server)
stop_button.pack(side=tk.LEFT, padx=5, pady=5)

kick_button = tk.Button(button_frame, text="Kick Client", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=lambda: kick_client(kick_entry.get()))
kick_button.pack(side=tk.LEFT, padx=5, pady=5)

kick_entry = tk.Entry(button_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
kick_entry.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()