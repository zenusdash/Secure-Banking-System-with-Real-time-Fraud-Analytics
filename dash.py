import sqlite3

# Connect to the same database file used by your Streamlit app
conn = sqlite3.connect('fortress_bank.db')
cursor = conn.cursor()

# Create the Fraud_Alerts table explicitly
cursor.execute("""
CREATE TABLE IF NOT EXISTS Fraud_Alerts (
    AlertID INTEGER PRIMARY KEY AUTOINCREMENT,
    TxnID INTEGER,
    RiskScore INTEGER,
    Reason TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (TxnID) REFERENCES Transactions(TxnID)
);
""")

conn.commit()
conn.close()
print("Table 'Fraud_Alerts' created successfully. You can now refresh the Streamlit dashboard.")