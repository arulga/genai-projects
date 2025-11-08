import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import db, os

db.init_db()
st.set_page_config(page_title="🧾 Billing System", layout="wide")

if not os.path.exists("invoices"):
    os.makedirs("invoices")

# ---------- LOGIN HANDLING ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None


def login_page():
    st.title("🔐 Billing System")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if db.check_login(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            if db.register_user(new_u, new_p):
                st.success("User registered successfully!")
            else:
                st.error("Username already exists!")


# ---------- PDF INVOICE ----------
def generate_pdf(bill_id, customer, items, total, gst, grand_total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="Billing Invoice", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Customer: {customer}", ln=True)
    pdf.cell(100, 10, txt=f"Bill ID: {bill_id}", ln=True)
    pdf.cell(100, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Product", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(40, 10, "Unit Price", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for i in items:
        pdf.cell(60, 10, i['Product'], 1)
        pdf.cell(30, 10, str(i['Quantity']), 1)
        pdf.cell(40, 10, f"Rs{i['Unit Price']}", 1)
        pdf.cell(40, 10, f"Rs{i['Total']}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(100, 10, "", 0)
    pdf.cell(40, 10, "Subtotal:", 0)
    pdf.cell(40, 10, f"Rs{total}", 0, 1)
    pdf.cell(100, 10, "", 0)
    pdf.cell(40, 10, "GST (18%):", 0)
    pdf.cell(40, 10, f"Rs{gst}", 0, 1)
    pdf.cell(100, 10, "", 0)
    pdf.cell(40, 10, "Grand Total:", 0)
    pdf.cell(40, 10, f"Rs{grand_total}", 0, 1)

    file_path = f"invoices/invoice_{bill_id}.pdf"
    pdf.output(file_path)
    return file_path


# ---------- MAIN APP ----------
def main_app():
    st.sidebar.title(f"👋 {st.session_state.username}")
    choice = st.sidebar.radio("Navigation", ["🏠 Product Master", "💵 Billing Entry", "📊 Reports", "🚪 Logout"])

    # ------------------ PRODUCT MASTER ------------------
    if choice == "🏠 Product Master":
        st.header("🧾 Product Master")
        name = st.text_input("Product Name")
        price = st.number_input("Price (₹)", min_value=1.0)
        if st.button("Add Product"):
            if db.add_product(name, price):
                st.success("✅ Product added successfully!")
                st.rerun()
            else:
                st.error("⚠️ Product already exists!")

        products = db.get_products()
        if products:
            df = pd.DataFrame(products, columns=["Product", "Price (₹)"])
            st.subheader("🗂️ Product List")

            for index, row in df.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                with col1:
                    st.text(row["Product"])
                with col2:
                    st.text(f"₹{row['Price (₹)']}")
                with col3:
                    if st.button("✏️ Edit", key=f"edit_{index}"):
                        st.session_state.edit_product = row["Product"]
                        st.session_state.edit_price = row["Price (₹)"]
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{index}"):
                        db.delete_product(row["Product"])
                        st.success(f"Deleted {row['Product']}")
                        st.rerun()

            # --- Edit Form ---
            if "edit_product" in st.session_state:
                st.markdown("---")
                st.subheader(f"✏️ Edit Product: {st.session_state.edit_product}")
                new_name = st.text_input("New Product Name", st.session_state.edit_product)
                new_price = st.number_input("New Price (₹)", min_value=1.0, value=float(st.session_state.edit_price))
                if st.button("💾 Save Changes"):
                    db.update_product(st.session_state.edit_product, new_name, new_price)
                    st.success("✅ Product updated successfully!")
                    del st.session_state["edit_product"]
                    del st.session_state["edit_price"]
                    st.rerun()
        else:
            st.info("No products yet.")

    # ------------------ BILLING ENTRY ------------------
    elif choice == "💵 Billing Entry":
        st.header("🧾 Create Bill")
        customer = st.text_input("Customer Name")
        products = db.get_products()
        if not products:
            st.warning("Please add products first.")
            return

        product_dict = dict(products)
        if "bill_items" not in st.session_state:
            st.session_state.bill_items = []

        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Product", list(product_dict.keys()))
        with col2:
            qty = st.number_input("Quantity", min_value=1, step=1)

        if st.button("Add Item"):
            st.session_state.bill_items.append({
                "Product": item,
                "Quantity": qty,
                "Unit Price": product_dict[item],
                "Total": product_dict[item] * qty
            })
            st.success("Item added!")

        # --- Show current bill items ---
        if st.session_state.bill_items:
            st.subheader("🧾 Current Items")
            df = pd.DataFrame(st.session_state.bill_items)
            for idx, row in df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 1, 2, 2, 1])
                with c1:
                    st.text(row["Product"])
                with c2:
                    st.text(row["Quantity"])
                with c3:
                    st.text(f"₹{row['Unit Price']}")
                with c4:
                    st.text(f"₹{row['Total']}")
                with c5:
                    if st.button("❌", key=f"del_item_{idx}"):
                        st.session_state.bill_items.pop(idx)
                        st.rerun()

            total = df["Total"].sum()
            gst = round(total * 0.18, 2)
            grand_total = total + gst
            st.markdown(f"### 💰 Total: ₹{total}")
            st.markdown(f"### 🧾 GST (18%): ₹{gst}")
            st.markdown(f"### 💵 Grand Total: ₹{grand_total}")

            if st.button("Generate Bill"):
                bill_id = db.save_bill(
                    st.session_state.username,
                    customer,
                    st.session_state.bill_items,
                    total,
                    gst,
                    grand_total,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                pdf_path = generate_pdf(bill_id, customer, st.session_state.bill_items, total, gst, grand_total)
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download Invoice (PDF)", f, file_name=os.path.basename(pdf_path))
                st.session_state.bill_items = []

    # ------------------ REPORTS ------------------
    elif choice == "📊 Reports":
        st.header("📊 Sales Report")
        bills = db.get_bills()
        if bills:
            df = pd.DataFrame(bills, columns=["Bill ID", "User", "Customer", "Subtotal", "GST", "Grand Total", "Date"])
            st.dataframe(df, use_container_width=True)
            total_sales = df["Grand Total"].sum()
            st.markdown(f"### 💰 Total Sales: ₹{total_sales}")
            st.download_button("📥 Download Report (CSV)", df.to_csv(index=False), "sales_report.csv", "text/csv")
        else:
            st.info("No bills yet.")

    # ------------------ LOGOUT ------------------
    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.bill_items = []
        st.rerun()


# ---------- CONTROLLER ----------
if st.session_state.logged_in:
    main_app()
else:
    login_page()
