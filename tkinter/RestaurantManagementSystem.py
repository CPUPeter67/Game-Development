import tkinter as tk
from tkinter import ttk, messagebox

class RestaurantOrderManagement:
    MAX_QUANTITY_PER_ITEM = 20
    MAX_TOTAL_ITEMS = 50
    TAX_RATE = 0.08

    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Order Management System")
        self.root.geometry("1020x720")
        self.root.minsize(800, 620)
        self.root.configure(bg="#f1f4f2")

        self.menu_items = {
            "Fries Deluxe": 5.99,
            "Lunch Deal": 9.99,
            "Cheeseburger Combo": 7.99,
            "Medium Pizza + Free Drink": 12.99,
            "Drink of Choice": 1.99,
        }

        self.currency_rates = {"USD": 1.0, "GBP": 0.79, "EUR": 0.92}
        self.currency_symbols = {"USD": "$", "GBP": "£", "EUR": "€"}
        self.menu_price_labels = {}
        self.menu_quantities = {}

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f1f4f2")
        style.configure("Surface.TFrame", background="#ffffff")
        style.configure("Header.TLabel", background="#f1f4f2", foreground="#183b34",
                        font=("Aptos", 21, "bold"))
        style.configure("Subtitle.TLabel", background="#f1f4f2", foreground="#61716c",
                        font=("Aptos", 10))
        style.configure("Section.TLabel", background="#ffffff", foreground="#183b34",
                        font=("Aptos", 14, "bold"))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#667671",
                        font=("Aptos", 9))
        style.configure("Item.TLabel", background="#ffffff", foreground="#263732",
                        font=("Aptos", 10, "bold"))
        style.configure("Price.TLabel", background="#ffffff", foreground="#53645e",
                        font=("Aptos", 10))
        style.configure("Summary.TLabel", background="#ffffff", foreground="#344640",
                        font=("Aptos", 10))
        style.configure("Total.TLabel", background="#ffffff", foreground="#a8462b",
                        font=("Aptos", 15, "bold"))
        style.configure("Primary.TButton", background="#b65336", foreground="#ffffff",
                        padding=(12, 9), font=("Aptos", 10, "bold"), borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#98432d")])
        style.configure("Quiet.TButton", background="#e7eeea", foreground="#263732",
                        padding=(12, 8), font=("Aptos", 9, "bold"), borderwidth=0)
        style.map("Quiet.TButton", background=[("active", "#d8e2dd")])

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        container = ttk.Frame(root, padding=(30, 24), style="App.TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ttk.Label(container, text="Restaurant orders", style="Header.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2)
        )
        ttk.Label(
            container,
            text="Choose menu items and review your cart before placing the order.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky=tk.W, pady=(2, 18))

        content = ttk.Frame(container, style="App.TFrame")
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=3, uniform="panels")
        content.grid_columnconfigure(2, weight=2, uniform="panels")

        menu_panel = ttk.Frame(content, padding=(20, 22), style="Surface.TFrame")
        menu_panel.grid(row=0, column=0, sticky="nsew")
        menu_panel.grid_columnconfigure(0, weight=1, minsize=180)
        menu_panel.grid_columnconfigure(1, minsize=76)
        menu_panel.grid_columnconfigure(2, minsize=66)

        ttk.Label(menu_panel, text="Menu", style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, sticky=tk.W
        )
        ttk.Label(
            menu_panel,
            text=f"Up to {self.MAX_QUANTITY_PER_ITEM} of each item",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(3, 20))
        ttk.Label(menu_panel, text="ITEM", style="Muted.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 8)
        )
        ttk.Label(menu_panel, text="PRICE", style="Muted.TLabel").grid(
            row=2, column=1, sticky=tk.E, padx=(0, 14), pady=(0, 8)
        )
        ttk.Label(menu_panel, text="QTY", style="Muted.TLabel").grid(
            row=2, column=2, sticky=tk.E, pady=(0, 8)
        )

        validate_quantity = (root.register(self.validate_quantity), "%P")
        for row, (item, price) in enumerate(self.menu_items.items(), start=3):
            ttk.Label(menu_panel, text=item, style="Item.TLabel").grid(
                row=row, column=0, sticky=tk.W, pady=12
            )
            price_label = ttk.Label(menu_panel, text=f"${price:.2f}", style="Price.TLabel")
            price_label.grid(row=row, column=1, sticky=tk.E, padx=(0, 14))
            self.menu_price_labels[item] = price_label

            quantity = ttk.Spinbox(
                menu_panel,
                from_=0,
                to=self.MAX_QUANTITY_PER_ITEM,
                increment=1,
                width=5,
                justify=tk.CENTER,
                validate="key",
                validatecommand=validate_quantity,
                command=self.update_menu_prices,
            )
            quantity.set("0")
            quantity.grid(row=row, column=2, sticky=tk.E, pady=8)
            quantity.bind("<KeyRelease>", self.update_menu_prices)
            self.menu_quantities[item] = quantity

        ttk.Separator(content, orient=tk.VERTICAL).grid(
            row=0, column=1, sticky="ns", padx=18
        )

        cart_panel = ttk.Frame(content, padding=(22, 22), style="Surface.TFrame")
        cart_panel.grid(row=0, column=2, sticky="nsew")
        cart_panel.grid_columnconfigure(0, weight=1)
        cart_panel.grid_rowconfigure(3, weight=1)

        ttk.Label(cart_panel, text="Your cart", style="Section.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )
        self.item_count_label = ttk.Label(
            cart_panel, text=f"0 / {self.MAX_TOTAL_ITEMS} items", style="Muted.TLabel"
        )
        self.item_count_label.grid(row=1, column=0, sticky=tk.W, pady=(3, 16))

        currency_row = ttk.Frame(cart_panel, style="Surface.TFrame")
        currency_row.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        currency_row.grid_columnconfigure(0, weight=1)
        ttk.Label(currency_row, text="Currency", style="Muted.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )
        self.currency_var = tk.StringVar(value="USD")
        currency_dropdown = ttk.Combobox(
            currency_row,
            textvariable=self.currency_var,
            state="readonly",
            width=7,
            values=tuple(self.currency_rates),
        )
        currency_dropdown.grid(row=0, column=1, sticky=tk.E)
        currency_dropdown.bind("<<ComboboxSelected>>", self.update_menu_prices)

        self.cart_summary_label = ttk.Label(
            cart_panel,
            text="Your cart is empty.",
            justify=tk.LEFT,
            anchor=tk.NW,
            wraplength=300,
            style="Summary.TLabel",
        )
        self.cart_summary_label.grid(row=3, column=0, sticky="nsew", pady=(0, 16))

        ttk.Separator(cart_panel, orient=tk.HORIZONTAL).grid(
            row=4, column=0, sticky="ew", pady=(0, 12)
        )
        self.subtotal_label = ttk.Label(cart_panel, text="Subtotal: $0.00", style="Summary.TLabel")
        self.subtotal_label.grid(row=5, column=0, sticky=tk.EW, pady=3)
        self.tax_label = ttk.Label(
            cart_panel, text=f"Tax ({self.TAX_RATE:.0%} sample): $0.00", style="Muted.TLabel"
        )
        self.tax_label.grid(row=6, column=0, sticky=tk.EW, pady=3)
        self.total_label = ttk.Label(cart_panel, text="Total: $0.00", style="Total.TLabel")
        self.total_label.grid(row=7, column=0, sticky=tk.EW, pady=(8, 16))

        ttk.Button(
            cart_panel, text="Place order", style="Primary.TButton", command=self.place_order
        ).grid(row=8, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(
            cart_panel, text="Clear order", style="Quiet.TButton", command=self.clear_order
        ).grid(row=9, column=0, sticky="ew")

        self.update_menu_prices()

    def validate_quantity(self, proposed_value):
        if not proposed_value:
            return True
        return (
            proposed_value.isascii()
            and proposed_value.isdigit()
            and int(proposed_value) <= self.MAX_QUANTITY_PER_ITEM
        )

    def update_menu_prices(self, _event=None):
        currency = self.currency_var.get()
        rate = self.currency_rates[currency]
        symbol = self.currency_symbols[currency]

        for item, label in self.menu_price_labels.items():
            price = self.menu_items[item] * rate
            label.config(text=f"{symbol}{price:.2f}")

        subtotal = 0.0
        item_count = 0
        order_lines = []
        for item, entry in self.menu_quantities.items():
            try:
                quantity = int(entry.get().strip() or "0")
            except ValueError:
                quantity = 0
            item_count += quantity
            if quantity:
                unit_price = self.menu_items[item] * rate
                line_total = unit_price * quantity
                subtotal += line_total
                order_lines.append(
                    f"{quantity} x {item} @ {symbol}{unit_price:.2f} = {symbol}{line_total:.2f}"
                )

        tax = subtotal * self.TAX_RATE
        total = subtotal + tax
        self.item_count_label.config(text=f"{item_count} / {self.MAX_TOTAL_ITEMS} items")
        self.cart_summary_label.config(text="\n".join(order_lines) or "Your cart is empty.")
        self.subtotal_label.config(text=f"Subtotal: {symbol}{subtotal:.2f}")
        self.tax_label.config(text=f"Tax ({self.TAX_RATE:.0%} sample): {symbol}{tax:.2f}")
        self.total_label.config(text=f"Total: {symbol}{total:.2f}")

    def clear_order(self):
        if not any(entry.get().strip() not in ("", "0") for entry in self.menu_quantities.values()):
            return

        if not messagebox.askyesno("Clear order", "Remove all quantities from this order?"):
            return

        for entry in self.menu_quantities.values():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        self.update_menu_prices()

    def place_order(self):
        currency = self.currency_var.get()
        rate = self.currency_rates[currency]
        symbol = self.currency_symbols[currency]
        order_lines = []
        subtotal = 0.0
        item_count = 0

        for item, entry in self.menu_quantities.items():
            value = entry.get().strip() or "0"
            try:
                quantity = int(value)
            except ValueError:
                messagebox.showerror("Invalid quantity", f"Enter a whole-number quantity for {item}.")
                entry.focus_set()
                return

            if quantity < 0:
                messagebox.showerror("Invalid quantity", "Quantities cannot be negative.")
                entry.focus_set()
                return

            if quantity > self.MAX_QUANTITY_PER_ITEM:
                messagebox.showerror(
                    "Item limit exceeded",
                    f"You can order up to {self.MAX_QUANTITY_PER_ITEM} of {item}.",
                )
                entry.focus_set()
                return

            item_count += quantity

            if quantity:
                unit_price = self.menu_items[item] * rate
                line_total = unit_price * quantity
                subtotal += line_total
                order_lines.append(
                    f"{quantity} x {item} @ {symbol}{unit_price:.2f} = {symbol}{line_total:.2f}"
                )

        if item_count > self.MAX_TOTAL_ITEMS:
            messagebox.showerror(
                "Order limit exceeded",
                f"An order can contain no more than {self.MAX_TOTAL_ITEMS} items.",
            )
            return

        if not order_lines:
            messagebox.showwarning("No items selected", "Enter a quantity for at least one menu item.")
            return

        tax = subtotal * self.TAX_RATE
        total = subtotal + tax
        receipt = (
            f"{'\n'.join(order_lines)}\n\n"
            f"Subtotal: {symbol}{subtotal:.2f}\n"
            f"Tax ({self.TAX_RATE:.0%} sample): {symbol}{tax:.2f}\n"
            f"Total: {symbol}{total:.2f} {currency}"
        )
        confirmation = (
            f"{receipt}\n\nPlace this order?"
        )
        if not messagebox.askyesno("Confirm order", confirmation):
            return

        messagebox.showinfo(
            "Order placed",
            receipt,
        )


if __name__ == "__main__":
    window = tk.Tk()
    RestaurantOrderManagement(window)
    window.mainloop()


