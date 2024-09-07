import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

DARK_GREY = '#333'
MEDIUM_GREY = '#ccc'
OCEAN_BLUE = '#3498db'
WHITE = "#fff"
BLACK = "#000000"
FONT = ("Helvetica", 14)
BUTTON_FONT = ("Helvetica", 14)
SMALL_FONT = ("Monaco", 12)

client = None
is_connected = False

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

def connect():
    global client, is_connected

    if is_connected:
        messagebox.showinfo("Already connected", "You are already connected to the server")
        return

    host = ip_textbox.get()
    port = int(port_textbox.get())

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        is_connected = True
        add_message("[SERVER] Successfully connected to the server")
    except:
        messagebox.showerror("Unable to connect to server", f"Unable to connect to server {host} {port}")
        return

    username = username_textbox.get()
    if username:
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid username", "Username cannot be empty")
        return

    threading.Thread(target=listen_for_messages_from_server, args=(client, )).start()

    ip_textbox.config(state=tk.DISABLED)
    port_textbox.config(state=tk.DISABLED)
    username_textbox.config(state=tk.DISABLED)
    connect_button.config(state=tk.DISABLED)
    logout_button.config(state=tk.NORMAL)

def logout():
    global client, is_connected

    if not is_connected:
        return

    client.sendall("/logout".encode())
    client.close()
    is_connected = False

    ip_textbox.config(state=tk.NORMAL)
    port_textbox.config(state=tk.NORMAL)
    username_textbox.config(state=tk.NORMAL)
    connect_button.config(state=tk.NORMAL)
    logout_button.config(state=tk.DISABLED)
    add_message("[CLIENT] Disconnected from the server")

def send_message():
    if not is_connected:
        messagebox.showerror("Not connected", "You are not connected to any server")
        return

    message = message_textbox.get()
    if message:
        client.sendall(message.encode())
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

def listen_for_messages_from_server(client):
    global is_connected
    while is_connected:
        try:
            message = client.recv(2048).decode('utf-8')
            if message:
                if message.startswith("[SERVER] You have been kicked from the chat"):
                    add_message(message)
                    logout()
                    break
                elif message.startswith("@"):
                    add_message(message)
                else:
                    username = message.split("~")[0]
                    content = message.split('~')[1]
                    add_message(f"[{username}] {content}")
            else:
                messagebox.showerror("Error", "Message received from client is empty")
                logout()
                break
        except:
            break

root = tk.Tk()
root.geometry("600x600")
root.title("Client")
root.resizable(False, False)

top_frame = tk.Frame(root, bg=DARK_GREY)
top_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

ip_label = tk.Label(top_frame, text="Server IP:", font=FONT, bg=DARK_GREY, fg=WHITE)
ip_label.grid(row=0, column=0, padx=5, pady=5)

ip_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK, width=11)
ip_textbox.grid(row=0, column=1, padx=5, pady=5)

port_label = tk.Label(top_frame, text="Port:", font=FONT, bg=DARK_GREY, fg=WHITE)
port_label.grid(row=0, column=2, padx=5, pady=5)

port_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK, width=5)
port_textbox.grid(row=0, column=3, padx=5, pady=5)

username_label = tk.Label(top_frame, text="Username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.grid(row=0, column=4, padx=5, pady=5)

username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK, width=11)
username_textbox.grid(row=0, column=5, padx=5, pady=5)

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

button_frame = tk.Frame(root, bg=DARK_GREY)
button_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

connect_button = tk.Button(button_frame, text="Connect", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
connect_button.grid(row=0, column=0, padx=5, pady=5)

logout_button = tk.Button(button_frame, text="Logout", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, state=tk.DISABLED, command=logout)
logout_button.grid(row=0, column=1, padx=5, pady=5)

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

middle_frame = tk.Frame(root, bg=MEDIUM_GREY)
middle_frame.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=BLACK)
message_box.config(state=tk.DISABLED)
message_box.pack(fill=tk.BOTH, expand=True)

separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
separator.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

bottom_frame = tk.Frame(root, bg=DARK_GREY)
bottom_frame.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK, width=45)
message_textbox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_message)
message_button.grid(row=0, column=1, padx=5, pady=5)

root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)
root.rowconfigure(3, weight=0)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=0)
root.rowconfigure(6, weight=0)
root.columnconfigure(0, weight=1)

root.mainloop()