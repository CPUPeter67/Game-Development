from tkinter import END, BOTH, LEFT, RIGHT, TOP, X, Y, Button, Frame, Scrollbar, Text, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

window = Tk()
window.title("Text Editor")
window.geometry("600x500")
window.rowconfigure(0, weight=1)
window.columnconfigure(1, weight=1)


def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete(1.0, END)
    with open(filepath, "r", encoding="utf-8") as input_file:
        txt_edit.insert(END, input_file.read())
    window.title(f"Codingal's Text Editor - {filepath}")


def save_file():
    """Save the current text to a file."""
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return

    with open(filepath, "w", encoding="utf-8") as output_file:
        output_file.write(txt_edit.get("1.0", END))
    window.title(f"Text Editor - {filepath}")


button_frame = Frame(window, relief="raised", bd=1)
button_frame.pack(side=LEFT, fill=Y)

txt_edit = Text(window, wrap="word", undo=True)
txt_edit.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(window, command=txt_edit.yview)
scrollbar.pack(side=RIGHT, fill=Y)
txt_edit.configure(yscrollcommand=scrollbar.set)

open_button = Button(button_frame, text="Open", command=open_file)
open_button.pack(side=TOP, fill=X, padx=5, pady=5)

save_button = Button(button_frame, text="Save As", command=save_file)
save_button.pack(side=TOP, fill=X, padx=5, pady=5)

window.mainloop()