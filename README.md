# 🏦 FortressBank Prime

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-success)
![Architecture](https://img.shields.io/badge/Architecture-3--Tier-orange)

FortressBank Prime is a secure, ACID-compliant core banking system designed to bridge traditional financial reliability with modern fintech agility. It features a robust transaction engine, real-time fraud monitoring via SQL triggers, and role-based "Neo-Modern" dashboards backed by advanced data science analytics.

## ✨ Key Features

### 🔒 Core Banking & Security
* **ACID-Compliant Transaction Engine:** Ensures absolute data integrity (Atomicity, Consistency, Isolation, Durability) during fund transfers. Implements automatic rollbacks to prevent data loss or "vanishing funds" during system failures.
* **Real-Time Fraud Detection:** Pushes security logic to the database layer using automated SQL Triggers to instantly flag high-value anomalies (>$10,000) at the point of entry.

### 📊 Advanced Data Analytics
* **Behavioral & Temporal Analysis:** Analyzes transaction velocity and spending patterns to establish user baselines and detect statistical outliers.
* **Executive Intelligence:** Visualizes branch liquidity, market share by account type, and KYC (Know Your Customer) compliance risk using integrated Plotly charts.

### 👥 Role-Based Portals
* **Bank Official Portal:** Features a comprehensive "Customer 360" degree view, allowing admins to inspect full KYC profiles, linked accounts, and transaction histories seamlessly.
* **Customer Dashboard:** Provides users with a responsive interface to view their balance, securely transfer funds via PIN verification, and analyze their weekly spending insights.

## 🛠️ Tech Stack

* **Frontend UI:** HTML5, CSS3 (Custom Neo-Modern Gradient Theme), Vanilla JavaScript
* **Data Visualization:** Plotly.js 
* **Backend API:** Node.js, Express.js
* **Database:** SQLite3 (Relational mapping with Foreign Keys and Constraints)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/FortressBank-Prime.git](https://github.com/yourusername/FortressBank-Prime.git)
   cd FortressBank-Prime
Install backend dependencies:
Ensure you have Node.js installed, then run:

Bash
npm install
Start the backend server:
This will initialize the SQLite database, create the necessary tables, and start listening on port 3000.

Bash
node server.js
Launch the Application:
Simply double-click the index.html file to open the frontend in your preferred web browser.

🧪 Testing Credentials
Use the following credentials to explore the different role-based views:

Bank Official (Admin) Access:

Role: Bank Official

Username: admin

Password: bank123

Customer Access:

Role: Customer

Account ID: 1001

Password: pass123

Transaction PIN: 1234 (Required for making transfers)

🔮 Future Scope
Integration of Machine Learning (Isolation Forests) for predictive, behavior-based anomaly detection.

Implementation of real-time SMS/Email alerts using Twilio or Nodemailer.

Migration to PostgreSQL for enterprise-grade horizontal scalability.

📄 License
This project is licensed under the MIT License - see the LICENSE.md file for details.
