"""
Streamlit Web Application for Tour Expense Tracker
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Tour Expense Tracker",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }
    .big-font {
        font-size: 50px !important;
        font-weight: bold;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tour_created' not in st.session_state:
    st.session_state.tour_created = False
    st.session_state.participants = []
    st.session_state.expenses = []

def calculate_summary():
    """Calculate expense summary"""
    if not st.session_state.participants or not st.session_state.expenses:
        return None
    
    total_expenses = sum(exp['amount'] for exp in st.session_state.expenses)
    num_participants = len(st.session_state.participants)
    avg_per_head = total_expenses / num_participants if num_participants > 0 else 0
    
    # Calculate contributions
    contributions = {p: 0 for p in st.session_state.participants}
    for expense in st.session_state.expenses:
        contributions[expense['paid_by']] += expense['amount']
    
    # Calculate balances
    balances = {}
    for participant in st.session_state.participants:
        balance = contributions[participant] - avg_per_head
        balances[participant] = {
            'contribution': contributions[participant],
            'balance': balance,
            'status': 'Should Get Back' if balance > 0 else ('Should Pay' if balance < 0 else 'Settled')
        }
    
    # Calculate settlements
    settlements = calculate_settlements(balances)
    
    return {
        'total_expenses': total_expenses,
        'num_participants': num_participants,
        'avg_per_head': avg_per_head,
        'balances': balances,
        'settlements': settlements,
        'contributions': contributions
    }

def calculate_settlements(balances):
    """Calculate simplified settlements"""
    settlements = []
    
    # Separate creditors and debtors
    creditors = {k: v['balance'] for k, v in balances.items() if v['balance'] > 0}
    debtors = {k: abs(v['balance']) for k, v in balances.items() if v['balance'] < 0}
    
    # Match debtors with creditors
    for debtor in list(debtors.keys()):
        for creditor in list(creditors.keys()):
            if debtors[debtor] > 0 and creditors[creditor] > 0:
                transfer = min(debtors[debtor], creditors[creditor])
                settlements.append({
                    'from': debtor,
                    'to': creditor,
                    'amount': round(transfer, 2)
                })
                debtors[debtor] -= transfer
                creditors[creditor] -= transfer
    
    return settlements

# Header
st.markdown('<p class="big-font">🧳 Tour Expense Tracker</p>', unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Split expenses fairly and track who owes what</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Sidebar for tour creation
with st.sidebar:
    st.header("⚙️ Tour Settings")
    
    if not st.session_state.tour_created:
        st.subheader("Create Your Tour")
        
        tour_name = st.text_input("Tour Name", placeholder="e.g., Goa Trip 2024")
        
        st.subheader("Add Participants")
        participant_name = st.text_input("Participant Name", placeholder="Enter name")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add", use_container_width=True):
                if participant_name and participant_name not in st.session_state.participants:
                    st.session_state.participants.append(participant_name)
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.participants = []
                st.rerun()
        
        if st.session_state.participants:
            st.success(f"Added {len(st.session_state.participants)} participants:")
            for p in st.session_state.participants:
                st.write(f"• {p}")
        
        st.markdown("---")
        
        if st.button("🚀 Create Tour", type="primary", use_container_width=True):
            if tour_name and len(st.session_state.participants) >= 2:
                st.session_state.tour_created = True
                st.session_state.tour_name = tour_name
                st.success("Tour created successfully!")
                st.rerun()
            else:
                st.error("Please enter tour name and add at least 2 participants")
    
    else:
        st.success(f"✅ Tour: {st.session_state.tour_name}")
        st.info(f"👥 {len(st.session_state.participants)} participants")
        
        if st.button("🔄 Reset Tour", use_container_width=True):
            st.session_state.tour_created = False
            st.session_state.participants = []
            st.session_state.expenses = []
            st.rerun()

# Main content
if not st.session_state.tour_created:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 Create a tour from the sidebar to get started!")
        
        st.markdown("""
        ### How to use:
        1. Enter your tour name
        2. Add all participants
        3. Click "Create Tour"
        4. Start adding expenses
        5. View summary and settlements
        """)

else:
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["💰 Add Expenses", "📊 Summary", "📈 Analytics"])
    
    with tab1:
        st.header("Add Expense")
        
        col1, col2 = st.columns(2)
        
        with col1:
            expense_desc = st.text_input("Description", placeholder="e.g., Hotel Booking")
            expense_amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, format="%.2f")
            expense_paid_by = st.selectbox("Paid By", st.session_state.participants)
        
        with col2:
            expense_category = st.selectbox(
                "Category",
                ["Accommodation", "Transportation", "Food", "Activities", "Shopping", "Other"]
            )
            expense_date = st.date_input("Date", value=datetime.now())
            st.write("")  # Spacing
            
            if st.button("➕ Add Expense", type="primary", use_container_width=True):
                if expense_desc and expense_amount > 0:
                    st.session_state.expenses.append({
                        'description': expense_desc,
                        'amount': float(expense_amount),
                        'paid_by': expense_paid_by,
                        'category': expense_category,
                        'date': expense_date.strftime('%Y-%m-%d')
                    })
                    st.success(f"Added: {expense_desc} - ₹{expense_amount:.2f}")
                    st.rerun()
                else:
                    st.error("Please fill all fields")
        
        st.markdown("---")
        st.subheader("📋 Expense List")
        
        if st.session_state.expenses:
            # Create DataFrame for expenses
            df_expenses = pd.DataFrame(st.session_state.expenses)
            df_expenses.index = range(1, len(df_expenses) + 1)
            
            # Display expenses with delete buttons
            for idx, expense in enumerate(st.session_state.expenses):
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{expense['description']}**")
                with col2:
                    st.write(f"₹{expense['amount']:.2f}")
                with col3:
                    st.write(f"{expense['paid_by']}")
                with col4:
                    st.write(f"{expense['category']}")
                with col5:
                    st.write(f"{expense['date']}")
                with col6:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.expenses.pop(idx)
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("No expenses added yet. Add your first expense above!")
    
    with tab2:
        st.header("💰 Expense Summary")
        
        summary = calculate_summary()
        
        if summary:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Total Expenses",
                    value=f"₹{summary['total_expenses']:.2f}"
                )
            
            with col2:
                st.metric(
                    label="Participants",
                    value=summary['num_participants']
                )
            
            with col3:
                st.metric(
                    label="Per Person",
                    value=f"₹{summary['avg_per_head']:.2f}"
                )
            
            st.markdown("---")
            
            # Balance details
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("⚖️ Balance Details")
                
                for participant, data in summary['balances'].items():
                    balance = data['balance']
                    status = data['status']
                    
                    if balance > 0:
                        st.success(f"**{participant}** - Should Get Back: ₹{abs(balance):.2f}")
                    elif balance < 0:
                        st.error(f"**{participant}** - Should Pay: ₹{abs(balance):.2f}")
                    else:
                        st.info(f"**{participant}** - Settled")
                    
                    st.caption(f"Total Paid: ₹{data['contribution']:.2f}")
            
            with col2:
                st.subheader("💸 Settlement Recommendations")
                
                if summary['settlements']:
                    for settlement in summary['settlements']:
                        st.warning(
                            f"**{settlement['from']}** → **{settlement['to']}**: ₹{settlement['amount']:.2f}"
                        )
                else:
                    st.success("🎉 All settled! Everyone has paid their share.")
            
            st.markdown("---")
            
            # Category breakdown
            st.subheader("📊 Expense Breakdown by Category")
            
            category_totals = {}
            for expense in st.session_state.expenses:
                cat = expense['category']
                category_totals[cat] = category_totals.get(cat, 0) + expense['amount']
            
            if category_totals:
                df_categories = pd.DataFrame(
                    list(category_totals.items()),
                    columns=['Category', 'Amount']
                )
                st.bar_chart(df_categories.set_index('Category'))
        else:
            st.info("Add expenses to see the summary")
    
    with tab3:
        st.header("📈 Analytics")
        
        summary = calculate_summary()
        
        if summary and st.session_state.expenses:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Individual Contributions")
                
                df_contributions = pd.DataFrame(
                    list(summary['contributions'].items()),
                    columns=['Participant', 'Amount Paid']
                )
                df_contributions = df_contributions.sort_values('Amount Paid', ascending=False)
                
                st.dataframe(
                    df_contributions,
                    hide_index=True,
                    use_container_width=True
                )
                
                st.bar_chart(df_contributions.set_index('Participant'))
            
            with col2:
                st.subheader("📅 Expenses Over Time")
                
                df_expenses = pd.DataFrame(st.session_state.expenses)
                df_expenses['date'] = pd.to_datetime(df_expenses['date'])
                daily_expenses = df_expenses.groupby('date')['amount'].sum().reset_index()
                
                st.line_chart(daily_expenses.set_index('date'))
                
                st.subheader("🏷️ Top Expenses")
                top_expenses = sorted(
                    st.session_state.expenses,
                    key=lambda x: x['amount'],
                    reverse=True
                )[:5]
                
                for exp in top_expenses:
                    st.write(f"• **{exp['description']}**: ₹{exp['amount']:.2f}")
            
            # Export section
            st.markdown("---")
            st.subheader("📥 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Create export data
                export_text = f"""
TOUR EXPENSE SUMMARY
====================
Tour Name: {st.session_state.tour_name}
Date: {datetime.now().strftime('%Y-%m-%d')}

PARTICIPANTS:
{chr(10).join(f'• {p}' for p in st.session_state.participants)}

EXPENSES:
{chr(10).join(f'{i+1}. {exp["description"]} - ₹{exp["amount"]:.2f} (Paid by: {exp["paid_by"]})' for i, exp in enumerate(st.session_state.expenses))}

SUMMARY:
Total Expenses: ₹{summary['total_expenses']:.2f}
Per Person: ₹{summary['avg_per_head']:.2f}

SETTLEMENTS:
{chr(10).join(f'• {s["from"]} → {s["to"]}: ₹{s["amount"]:.2f}' for s in summary['settlements'])}
"""
                st.download_button(
                    label="📄 Download as Text",
                    data=export_text,
                    file_name=f"tour_expenses_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                df_export = pd.DataFrame(st.session_state.expenses)
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv,
                    file_name=f"tour_expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("Add expenses to see analytics")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: white;'>Made with ❤️ using Streamlit | Tour Expense Tracker v1.0</p>",
    unsafe_allow_html=True
)