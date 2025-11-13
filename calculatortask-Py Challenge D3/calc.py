import tkinter as tk
from tkinter import ttk

# Function to calculate the result instantly
def calculate(*args):
    try:
        num1 = float(entry_num1.get())
        num2 = float(entry_num2.get())
        op = operation_var.get()

        if op == "+":
            result = num1 + num2
        elif op == "-":
            result = num1 - num2
        elif op == "×":
            result = num1 * num2
        elif op == "÷":
            result = "∞" if num2 == 0 else num1 / num2
        else:
            result = ""

        label_result.config(text=f"Result: {result}")
    except ValueError:
        label_result.config(text="Result: —")

# ----------------- UI Setup -----------------
root = tk.Tk()
root.title("🧮 Simple Calculator")
root.geometry("300x180")
root.resizable(False, False)

# Labels & Inputs
tk.Label(root, text="First Number:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_num1 = tk.Entry(root, width=10)
entry_num1.grid(row=0, column=1, padx=5)

tk.Label(root, text="Second Number:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_num2 = tk.Entry(root, width=10)
entry_num2.grid(row=1, column=1, padx=5)

# Dropdown for operation
operation_var = tk.StringVar(value="+")
operations = ["+", "-", "×", "÷"]
operation_dropdown = ttk.Combobox(root, textvariable=operation_var, values=operations, width=3, state="readonly")
operation_dropdown.grid(row=0, column=2, rowspan=2, padx=10)
operation_dropdown.bind("<<ComboboxSelected>>", calculate)

# Result Label
label_result = tk.Label(root, text="Result: —", font=("Arial", 12, "bold"))
label_result.grid(row=3, column=0, columnspan=3, pady=15)

# Trigger instant calculation on input change
entry_num1.bind("<KeyRelease>", calculate)
entry_num2.bind("<KeyRelease>", calculate)

# Run the app
root.mainloop()
