import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Currency Converter 💱",
    page_icon="💱",
    layout="centered"
)

# Static exchange rates (base: INR)
EXCHANGE_RATES = {
    'INR': 1.0,
    'USD': 0.012,    # 1 INR = 0.012 USD
    'EUR': 0.011,    # 1 INR = 0.011 EUR
    'GBP': 0.0094    # 1 INR = 0.0094 GBP
}

def convert_currency(amount, from_currency, to_currency):
    """Convert currency using static exchange rates"""
    # Convert to INR first, then to target currency
    amount_in_inr = amount / EXCHANGE_RATES[from_currency]
    converted_amount = amount_in_inr * EXCHANGE_RATES[to_currency]
    return round(converted_amount, 2)

def main():
    # App title and description
    st.title("💱 Currency Converter")
    st.markdown("Convert between **INR**, **USD**, **EUR**, and **GBP** using static exchange rates.")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:

        # From currency dropdown
        from_currency = st.selectbox(
            "From Currency",
            options=list(EXCHANGE_RATES.keys()),
            index=0  # Default to INR
        )
        # Amount input
        amount = st.number_input(
            "💰 Amount",
            min_value=0.0,
            value=100.0,
            step=1.0,
            format="%.2f"
        )
    
    
    with col2:
        # To currency dropdown
        to_currency = st.selectbox(
            "To Currency",
            options=list(EXCHANGE_RATES.keys()),
            index=1  # Default to USD
        )
        
        # Display current exchange rate
    # with col3:
        if from_currency != to_currency:
            rate = EXCHANGE_RATES[to_currency] / EXCHANGE_RATES[from_currency]
            st.info(f"💹 Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    
    # Perform conversion 
    if from_currency == to_currency:
        result = amount
        st.warning("⚠️ Same currency selected - no conversion needed")
    else:
        result = convert_currency(amount, from_currency, to_currency)
    
    # Display result
    st.success(f"**🎯 Converted Amount: {result:,.2f} {to_currency}**")
    
    # Add some spacing
    st.markdown("---")
    
    # Display all exchange rates in a table
    st.subheader("📊 Current Exchange Rates (Base: INR)")
    
    # Create rates table
    rates_data = []
    for currency, rate in EXCHANGE_RATES.items():
        if currency != 'INR':
            rates_data.append({
                'Currency': currency,
                'Rate (1 INR)': f"{rate:.4f}",
                'Inverse (1 Foreign)': f"{1/rate:.2f} INR"
            })
    
    st.table(rates_data)
    
    # Footer
    st.markdown("---")
    st.caption("💡 Note: These are static exchange rates for demonstration purposes.")

if __name__ == "__main__":
    main()