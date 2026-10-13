from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

root = Tk()
root.title("Denomination Counter")
root.configure(bg="light blue")
root.geometry("650x400")

upload = Image.open("app_img.jpg")
upload = upload.resize((300, 300))
image = ImageTk.PhotoImage(upload)

label = Label(root, image=image, bg="light blue")
label.place(x=180, y=20)

label1 = Label(
    root,
    text="Hey User! Welcome to Denomination Counter Application.",
    bg="light blue"
)
label1.place(relx=0.5, y=340, anchor=CENTER)

def msg():
    MsgBox = messagebox.showinfo(
        "Alert",
        "Do you want to calculate the denomination count?"
    )
    if MsgBox == "ok":
        topwin()

button1 = Button(
    root,
    text="Let's get started!",
    command=msg,
    bg="brown",
    fg="white"
)

button1.place(relx=0.5, y=370, anchor=CENTER)
button1 = Button(
    root,
    text="Let's get started!",
    command=msg,
    bg="brown",
    fg="white"
)

button1.place(relx=0.5, y=370, anchor=CENTER)

def topwin():
    top = Toplevel()
    top.title("Denominations Calculator")
    top.configure(bg="light grey")
    top.geometry("600x350+50+50")

    label = Label(top, text="Enter total amount", bg="light grey")
    label.grid(row=0, column=0, padx=10, pady=10, sticky=W)
    entry = Entry(top)
    entry.grid(row=0, column=1, padx=10, pady=10)

    lbl = Label(
        top,
        text="Here are number of notes for each denomination",
        bg="light grey"
    )
    lbl.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    denominations = (2000, 500, 100)
    for row, denomination in enumerate(denominations, start=2):
        Label(top, text=str(denomination), bg="light grey").grid(
            row=row, column=0, padx=10, pady=5, sticky=W
        )
        Entry(top).grid(row=row, column=1, padx=10, pady=5)

