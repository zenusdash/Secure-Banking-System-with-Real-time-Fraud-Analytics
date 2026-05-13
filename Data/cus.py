import pandas as pd
from faker import Faker
import random

fake = Faker()
num_customers = 100
num_transactions = 500

# 1. Generate Customers
customers = []
for i in range(1, num_customers + 1):
    customers.append({
        "CustomerID": i,
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Email": fake.unique.email(),
        "KYC_Status": random.choices(['Verified', 'Pending', 'Flagged'], weights=[80, 15, 5])[0]
    })

# 2. Generate Accounts
accounts = []
for i in range(1, num_customers + 1):
    accounts.append({
        "AccountID": 1000 + i,
        "CustomerID": i,
        "AccountType": random.choice(['Savings', 'Current', 'Business']),
        "Balance": round(random.uniform(500, 50000), 2),
        "Status": 'Active'
    })

# 3. Generate Transactions (The "Data Analytics" meat)
transactions = []
account_ids = [a['AccountID'] for a in accounts]
for i in range(1, num_transactions + 1):
    from_acc = random.choice(account_ids)
    to_acc = random.choice([acc for acc in account_ids if acc != from_acc])
    amount = round(random.uniform(10, 15000), 2) # Some will trigger our >10k fraud rule
    
    transactions.append({
        "TxnID": i,
        "FromAccountID": from_acc,
        "ToAccountID": to_acc,
        "Amount": amount,
        "TxnType": 'Transfer',
        "Timestamp": fake.date_time_this_year()
    })

# Save to CSV
pd.DataFrame(customers).to_csv('customers.csv', index=False)
pd.DataFrame(accounts).to_csv('accounts.csv', index=False)
pd.DataFrame(transactions).to_csv('transactions.csv', index=False)

print("Datasets generated successfully!")