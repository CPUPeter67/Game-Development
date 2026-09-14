from datetime import date
import tkinter as tk


window = tk.Tk()
window.title("Demo Window")
window.geometry("400x300")
window.mainloop()
root = tk.Tk()
root.title("Getting Started with Widgets")
root.geometry("400x300")

lbl = tk.Label(text="Hello, Tkinterer!", fg="white", bg="#072FSF", height=1, width=300)

name_lbl = tk.Label(text="Full Name", bg="#3895D3")
name_entry = tk.Entry()
text_box = tk.Text(root, height=5, width=40)

def display():
    name = name_entry.get()
    global message
    message = "Welcome to the Application! \nToday's date is: "
    greet = "Hello "+name+"\n"
    text_box.insert(tk.END, greet)
    text_box.insert(tk.END, message)
    text_box.insert(tk.END, date.today())

text_box = tk.Text(height=3)

btn = tk.Button(text="Begin", command=display, height=1, bg="#1261A0", fg='white')

lbl.pack()
name_lbl.pack()
name_entry.pack()
btn.pack()
text_box.pack()

root.mainloop()    