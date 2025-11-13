import customtkinter as ctk

# Set appearance (optional: "Dark", "Light", "System")
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# -------------------- Logic --------------------
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

        label_result.configure(text=f"Result: {result}")
    except ValueError:
        label_result.configure(text="Result: —")

# -------------------- UI Setup --------------------
app = ctk.CTk()
app.title("🧮 Modern Calculator")
app.geometry("360x220")

# Frame for layout
frame = ctk.CTkFrame(app, corner_radius=10)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# First Number
label_num1 = ctk.CTkLabel(frame, text="First Number:")
label_num1.grid(row=0, column=0, padx=10, pady=10, sticky="e")

entry_num1 = ctk.CTkEntry(frame, width=100)
entry_num1.grid(row=0, column=1, padx=5, pady=10)

# Second Number
label_num2 = ctk.CTkLabel(frame, text="Second Number:")
label_num2.grid(row=1, column=0, padx=10, pady=10, sticky="e")

entry_num2 = ctk.CTkEntry(frame, width=100)
entry_num2.grid(row=1, column=1, padx=5, pady=10)

# Operation dropdown
operation_var = ctk.StringVar(value="+")
operation_dropdown = ctk.CTkOptionMenu(frame, variable=operation_var, values=["+", "-", "×", "÷"], command=lambda _: calculate())
operation_dropdown.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

# Result label
label_result = ctk.CTkLabel(frame, text="Result: —", font=ctk.CTkFont(size=16, weight="bold"))
label_result.grid(row=3, column=0, columnspan=3, pady=20)

# Instant updates on typing
entry_num1.bind("<KeyRelease>", calculate)
entry_num2.bind("<KeyRelease>", calculate)

app.mainloop()
