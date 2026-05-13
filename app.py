import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FortressBank Core",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
<style>
    /* Main Background */
    .main { background-color: #f8f9fa; }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #403737;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(255,255,255,0.9);
    }
    
    /* Headers */
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE MANAGEMENT ---
def get_connection():
    conn = sqlite3.connect('fortress_bank.db')
    return conn

def init_db():
    """Create missing tables for new features if they don't exist"""
    conn = get_connection()
    c = conn.cursor()
    
    # Loans Table
    c.execute("""CREATE TABLE IF NOT EXISTS Loans (
        LoanID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER,
        Amount DECIMAL(15,2),
        Type TEXT,
        Status TEXT DEFAULT 'Pending',
        ApplyDate DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Service Requests (Complaints, Chequebooks)
    c.execute("""CREATE TABLE IF NOT EXISTS ServiceRequests (
        ReqID INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerID INTEGER,
        Type TEXT,
        Details TEXT,
        Status TEXT DEFAULT 'Open',
        Date DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Audit Log for Compliance
    c.execute("""CREATE TABLE IF NOT EXISTS AuditLog (
        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
        Action TEXT,
        PerformedBy TEXT,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    return conn

# Initialize DB on load
init_db()

# --- ACID TRANSACTION ENGINE ---
def secure_transfer(sender, receiver, amount):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("BEGIN TRANSACTION")
        
        # Check Balance
        c.execute("SELECT Balance FROM Accounts WHERE AccountID=?", (sender,))
        bal = c.fetchone()
        if not bal or bal[0] < amount:
            conn.rollback()
            return False, "Insufficient Funds or Invalid Sender"
            
        # Execute Transfer
        c.execute("UPDATE Accounts SET Balance = Balance - ? WHERE AccountID = ?", (amount, sender))
        c.execute("UPDATE Accounts SET Balance = Balance + ? WHERE AccountID = ?", (amount, receiver))
        
        # Log Transaction
        c.execute("INSERT INTO Transactions (FromAccountID, ToAccountID, Amount, TxnType, Timestamp) VALUES (?, ?, ?, 'Transfer', datetime('now'))", (sender, receiver, amount))
        
        # Fraud Check Trigger (Simulated logic here for UI feedback)
        if amount > 10000:
            c.execute("INSERT INTO Fraud_Alerts (TxnID, RiskScore, Reason) VALUES (last_insert_rowid(), 9, 'High Value Transfer')")
            
        conn.commit()
        return True, "Transfer Successful"
    except Exception as e:
        conn.rollback()
        return False, str(e)

# --- AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None

def login_screen():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🏦 FortressBank</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>Secure Core Banking System</h4>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("User ID / Username")
            pw = st.text_input("Password", type="password")
            role = st.selectbox("Login Mode", ["Customer", "Bank Official"])
            submitted = st.form_submit_button("Login to System")
            
            if submitted:
                if role == "Bank Official" and user == "admin" and pw == "bank123":
                    st.session_state.logged_in = True
                    st.session_state.role = "Official"
                    st.rerun()
                elif role == "Customer" and user.isdigit() and pw == "pass123":
                    st.session_state.logged_in = True
                    st.session_state.role = "Customer"
                    st.session_state.user_id = int(user)
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

# --- OFFICIAL INTERFACE ---
def official_interface():
    with st.sidebar:
        st.title("🏛️ Admin Portal")
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "Customer 360", "Operations", "Loan Dept", "Compliance"],
            icons=["speedometer2", "people", "hdd-stack", "cash-coin", "shield-lock"],
            default_index=0,
        )
        if st.button("Log Out", type="primary"):
            st.session_state.logged_in = False
            st.rerun()

    conn = get_connection()

    # 1. ANALYTICS DASHBOARD
    if selected == "Dashboard":
        st.title("🏦 Branch Performance Dashboard")
        
        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        total_dep = pd.read_sql("SELECT SUM(Balance) FROM Accounts", conn).iloc[0,0]
        total_cust = pd.read_sql("SELECT COUNT(*) FROM Customers", conn).iloc[0,0]
        pending_loans = pd.read_sql("SELECT COUNT(*) FROM Loans WHERE Status='Pending'", conn).iloc[0,0]
        alerts = pd.read_sql("SELECT COUNT(*) FROM Fraud_Alerts", conn).iloc[0,0]
        
        col1.metric("Total Liquidity", f"${total_dep:,.0f}")
        col2.metric("Total Customers", total_cust)
        col3.metric("Pending Loans", pending_loans)
        col4.metric("Risk Alerts", alerts, delta_color="inverse")
        
        # Charts
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Transaction Volume (Last 7 Days)")
            df_tx = pd.read_sql("SELECT Timestamp, Amount FROM Transactions ORDER BY Timestamp DESC LIMIT 50", conn)
            fig = px.bar(df_tx, x='Timestamp', y='Amount', title="Recent Money Flow")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_b:
            st.subheader("Customer Segmentation")
            df_seg = pd.read_sql("SELECT AccountType, COUNT(*) as Count FROM Accounts GROUP BY AccountType", conn)
            fig2 = px.pie(df_seg, names='AccountType', values='Count', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

    # 2. CUSTOMER 360 MANAGEMENT
    elif selected == "Customer 360":
        st.title("👤 Customer Information Management")
        search_term = st.text_input("Search by Customer ID or Name")
        
        if search_term:
            query = f"SELECT * FROM Customers WHERE CustomerID LIKE '%{search_term}%' OR FirstName LIKE '%{search_term}%'"
            cust = pd.read_sql(query, conn)
            
            if not cust.empty:
                st.success("Customer Found")
                c_id = cust.iloc[0]['CustomerID']
                
                # Profile Header
                with st.expander("View Full Profile (KYC & Bio)", expanded=True):
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.image("https://placehold.co/150", caption="Customer Photo")
                    with c2:
                        st.write(f"**Name:** {cust.iloc[0]['FirstName']} {cust.iloc[0]['LastName']}")
                        st.write(f"**Email:** {cust.iloc[0]['Email']}")
                        st.write(f"**KYC Status:** {cust.iloc[0]['KYC_Status']}")
                        if cust.iloc[0]['KYC_Status'] == 'Flagged':
                            st.error("⚠️ AML ALERT: High Risk Customer")

                # Related Accounts
                st.subheader("Linked Accounts")
                accs = pd.read_sql(f"SELECT * FROM Accounts WHERE CustomerID={c_id}", conn)
                st.dataframe(accs)
                
                # Transaction History
                st.subheader("Transaction History")
                txns = pd.read_sql(f"""
                    SELECT * FROM Transactions 
                    WHERE FromAccountID IN (SELECT AccountID FROM Accounts WHERE CustomerID={c_id})
                    ORDER BY Timestamp DESC LIMIT 10
                """, conn)
                st.dataframe(txns)
                
            else:
                st.warning("No customer found.")

    # 3. OPERATIONS (Account Ops)
    elif selected == "Operations":
        st.title("⚙️ Account Operations")
        tab1, tab2 = st.tabs(["Open New Account", "Service Requests"])
        
        with tab1:
            with st.form("new_acc"):
                c_id_link = st.number_input("Link to Customer ID", step=1)
                acc_type = st.selectbox("Account Type", ["Savings", "Current", "Loan", "Fixed Deposit"])
                deposit = st.number_input("Initial Deposit", min_value=1000.0)
                if st.form_submit_button("Create Account"):
                    c = conn.cursor()
                    c.execute("INSERT INTO Accounts (CustomerID, AccountType, Balance, Status) VALUES (?, ?, ?, 'Active')", (c_id_link, acc_type, deposit))
                    conn.commit()
                    st.success("Account Created Successfully!")
        
        with tab2:
            st.subheader("Pending Service Requests")
            reqs = pd.read_sql("SELECT * FROM ServiceRequests WHERE Status='Open'", conn)
            st.dataframe(reqs)
            if st.button("Mark Selected as Resolved"):
                st.info("Resolution workflow triggered.")

    # 4. LOAN DEPARTMENT
    elif selected == "Loan Dept":
        st.title("💰 Loan Management System")
        loans = pd.read_sql("SELECT * FROM Loans", conn)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Loan Applications")
            st.dataframe(loans)
        with col2:
            st.subheader("Credit Scoring")
            lid = st.number_input("Enter Loan ID to Process", step=1)
            score = 750 # Simulated score
            st.metric("CIBIL Score", score)
            if st.button("Approve Loan"):
                c = conn.cursor()
                c.execute(f"UPDATE Loans SET Status='Approved' WHERE LoanID={lid}")
                conn.commit()
                st.success(f"Loan {lid} Approved!")

    # 5. COMPLIANCE & AUDIT
    elif selected == "Compliance":
        st.title("🛡️ Risk & Compliance")
        st.error("Fraud Detection Alerts (Real-Time)")
        alerts = pd.read_sql("SELECT * FROM Fraud_Alerts ORDER BY Timestamp DESC", conn)
        st.dataframe(alerts, use_container_width=True)
        
        st.divider()
        st.subheader("System Audit Trail")
        # Simulated audit logs
        st.write("Displaying last 50 system actions by officials...")
        st.code("User 'admin' approved Loan #105 at 10:00 AM\nUser 'admin' viewed Customer #55 profile at 10:05 AM")

# --- CUSTOMER INTERFACE ---
def customer_interface():
    user_id = st.session_state.user_id
    conn = get_connection()
    
    # Fetch User Name
    user_name = pd.read_sql(f"""
        SELECT FirstName FROM Customers 
        WHERE CustomerID = (SELECT CustomerID FROM Accounts WHERE AccountID={user_id})
    """, conn).iloc[0,0]

    with st.sidebar:
        st.image("https://placehold.co/100", caption=f"Hello, {user_name}")
        st.write(f"**Account:** #{user_id}")
        selected = option_menu(
            menu_title="My Banking",
            options=["My Home", "Transfers", "Bill Pay", "Services", "Statements"],
            icons=["house", "arrow-left-right", "receipt", "headset", "file-earmark-text"],
            default_index=0,
        )
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # 1. HOMEPAGE
    if selected == "My Home":
        st.title(f"👋 Welcome back, {user_name}")
        
        # Balance Card
        bal = pd.read_sql(f"SELECT Balance, AccountType FROM Accounts WHERE AccountID={user_id}", conn).iloc[0]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;">
            <h3>{bal['AccountType']} Account</h3>
            <h1>${bal['Balance']:,.2f}</h1>
            <p>Account #{user_id} | Status: Active</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Actions
        c1, c2, c3 = st.columns(3)
        if c1.button("💸 Quick Transfer"):
            st.toast("Go to 'Transfers' tab")
        if c2.button("📄 View Statement"):
            st.toast("Go to 'Statements' tab")
        if c3.button("🆘 Help"):
            st.toast("Go to 'Services' tab")

    # 2. TRANSFERS
    elif selected == "Transfers":
        st.title("💸 Fund Transfer")
        tab1, tab2 = st.tabs(["Internal Transfer", "Manage Beneficiaries"])
        
        with tab1:
            st.info("Secure Transfer (NEFT/IMPS/RTGS)")
            with st.form("transfer_form"):
                receiver = st.number_input("Beneficiary Account ID", step=1)
                amount = st.number_input("Amount ($)", min_value=1.0)
                pin = st.text_input("Transaction PIN", type="password")
                
                if st.form_submit_button("Pay Now"):
                    if pin == "1234": # Simulated PIN
                        success, msg = secure_transfer(user_id, receiver, amount)
                        if success:
                            st.success(msg)
                            st.balloons()
                        else:
                            st.error(msg)
                    else:
                        st.error("Incorrect PIN")

    # 3. BILL PAYMENTS
    elif selected == "Bill Pay":
        st.title("🧾 Bill Payments")
        type = st.selectbox("Category", ["Electricity", "Mobile Postpaid", "Credit Card", "FastTag"])
        biller = st.text_input("Biller Name / Consumer ID")
        amt = st.number_input("Bill Amount")
        if st.button("Pay Bill"):
            st.success(f"Payment of ${amt} to {type} successful!")

    # 4. SERVICES
    elif selected == "Services":
        st.title("🎧 Customer Service")
        st.write("Raise a request and track status.")
        
        with st.form("service_req"):
            rtype = st.selectbox("Request Type", ["Cheque Book Request", "Debit Card Issue", "Address Change", "Complaint"])
            desc = st.text_area("Additional Details")
            if st.form_submit_button("Submit Request"):
                c = conn.cursor()
                # Assuming simple mapping for CustomerID from AccountID
                cust_id = pd.read_sql(f"SELECT CustomerID FROM Accounts WHERE AccountID={user_id}", conn).iloc[0,0]
                c.execute("INSERT INTO ServiceRequests (CustomerID, Type, Details) VALUES (?, ?, ?)", (cust_id, rtype, desc))
                conn.commit()
                st.success(f"Ticket Raised: {rtype}")
    
    # 5. STATEMENTS
    elif selected == "Statements":
        st.title("📄 E-Statements")
        
        # Filter
        days = st.slider("Select Duration (Days)", 7, 365, 30)
        
        df = pd.read_sql(f"""
            SELECT Timestamp, TxnType, Amount, ToAccountID 
            FROM Transactions 
            WHERE FromAccountID={user_id} OR ToAccountID={user_id}
            ORDER BY Timestamp DESC
        """, conn)
        
        st.dataframe(df, use_container_width=True)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Statement (CSV)",
            csv,
            "statement.csv",
            "text/csv",
            key='download-csv'
        )

# --- MAIN APP ROUTER ---
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_screen()
    else:
        if st.session_state.role == "Official":
            official_interface()
        elif st.session_state.role == "Customer":
            customer_interface()