import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# --------------- Calculation Logic ---------------
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

# --------------- UI Setup ---------------
root = ttk.Window(themename="flatly")  # ✅ main window with theme
root.title("🧮 TTKBootstrap Calculator")
root.geometry("360x220")

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# First Number
ttk.Label(frame, text="First Number:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_num1 = ttk.Entry(frame, width=10)
entry_num1.grid(row=0, column=1, padx=5, pady=10)

# Second Number
ttk.Label(frame, text="Second Number:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_num2 = ttk.Entry(frame, width=10)
entry_num2.grid(row=1, column=1, padx=5, pady=10)

# Operation dropdown
operation_var = ttk.StringVar(value="+")
operation_dropdown = ttk.Combobox(
    frame,
    textvariable=operation_var,
    values=["+", "-", "×", "÷"],
    width=3,
    state="readonly",
)
operation_dropdown.grid(row=0, column=2, rowspan=2, padx=10)
operation_dropdown.bind("<<ComboboxSelected>>", calculate)

# Result Label
label_result = ttk.Label(frame, text="Result: —", font=("Segoe UI", 12, "bold"))
label_result.grid(row=3, column=0, columnspan=3, pady=20)

# Instant calculation when typing
entry_num1.bind("<KeyRelease>", calculate)
entry_num2.bind("<KeyRelease>", calculate)

root.mainloop()
