from tkinter import Tk, Button, messagebox


window = Tk()
window.title("Event Handler")
window.geometry("220x140")


def handle_keypress(event):
    print(event.char)


def show_warning():
    messagebox.showwarning("Alert", "Trojan Horse Virus detected. Take immediate action.")


# Bind keyboard events to the window.
window.bind("<Key>", handle_keypress)

# The command callback is called when the button is clicked.
button = Button(window, text="Do a Virus Scan now.", command=show_warning)
button.pack(pady=45)

window.mainloop()