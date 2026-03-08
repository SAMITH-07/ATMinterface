import streamlit as st
import json
import os
from datetime import datetime

class ATMSystem:
    def __init__(self):
        self.data_file = "atm_users.json"
        self.users = self.load_users()
        self.current_user = None
        
    def load_users(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def register_user(self, name, username, password, account_no):
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'name': name,
            'password': password,
            'account_no': account_no,
            'balance': 100000.0,
            'transactions': [],
            'transaction_count': 0
        }
        self.save_users()
        return True, "Registration successful! Please login."
    
    def login_user(self, username, password):
        if username in self.users and self.users[username]['password'] == password:
            self.current_user = username
            return True, "Login successful!"
        return False, "Invalid username or password"
    
    def withdraw(self, amount):
        if self.current_user and amount > 0:
            user = self.users[self.current_user]
            if amount <= user['balance']:
                user['balance'] -= amount
                user['transaction_count'] += 1
                transaction = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Withdrawn: ₹{amount:.2f}"
                user['transactions'].append(transaction)
                self.save_users()
                return True, f"Withdrawal successful! Remaining balance: ₹{user['balance']:.2f}"
            else:
                return False, "Insufficient balance!"
        return False, "Invalid operation"
    
    def deposit(self, amount):
        if self.current_user and amount > 0:
            user = self.users[self.current_user]
            user['balance'] += amount
            user['transaction_count'] += 1
            transaction = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Deposited: ₹{amount:.2f}"
            user['transactions'].append(transaction)
            self.save_users()
            return True, f"Deposit successful! New balance: ₹{user['balance']:.2f}"
        return False, "Invalid operation"
    
    def transfer(self, recipient_username, amount):
        if self.current_user and amount > 0:
            if recipient_username not in self.users:
                return False, "Recipient username not found"
            
            sender = self.users[self.current_user]
            if amount <= sender['balance']:
                recipient = self.users[recipient_username]
                sender['balance'] -= amount
                recipient['balance'] += amount
                
                # Update sender's transactions
                sender['transaction_count'] += 1
                transaction = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Transferred: ₹{amount:.2f} to {recipient_username}"
                sender['transactions'].append(transaction)
                
                # Update recipient's transactions
                recipient['transaction_count'] += 1
                transaction = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Received: ₹{amount:.2f} from {self.current_user}"
                recipient['transactions'].append(transaction)
                
                self.save_users()
                return True, f"Transfer successful! Remaining balance: ₹{sender['balance']:.2f}"
            else:
                return False, "Insufficient balance!"
        return False, "Invalid operation"
    
    def get_balance(self):
        if self.current_user:
            return self.users[self.current_user]['balance']
        return 0
    
    def get_transaction_history(self):
        if self.current_user:
            return self.users[self.current_user]['transactions']
        return []
    
    def logout(self):
        self.current_user = None

def main():
    st.set_page_config(page_title="SBI ATM System", page_icon="🏦", layout="centered")
    
    if 'atm_system' not in st.session_state:
        st.session_state.atm_system = ATMSystem()
    
    atm = st.session_state.atm_system
    
    st.title("🏦 SBI ATM System")
    st.markdown("---")
    
    # Check if user is logged in
    if atm.current_user:
        user_data = atm.users[atm.current_user]
        st.success(f"Welcome, {user_data['name']}!")
        st.info(f"Account Number: {user_data['account_no']}")
        
        # Show current balance
        st.metric("Current Balance", f"₹{atm.get_balance():.2f}")
        
        # Menu options
        menu = st.selectbox("Choose an option:", 
                          ["Withdraw", "Deposit", "Transfer", "Transaction History", "Logout"])
        
        if menu == "Withdraw":
            st.subheader("💸 Withdraw Money")
            amount = st.number_input("Enter amount to withdraw:", min_value=0.0, step=100.0)
            if st.button("Withdraw"):
                if amount > 0:
                    success, message = atm.withdraw(amount)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please enter a valid amount")
        
        elif menu == "Deposit":
            st.subheader("💰 Deposit Money")
            amount = st.number_input("Enter amount to deposit:", min_value=0.0, step=100.0)
            if st.button("Deposit"):
                if amount > 0:
                    success, message = atm.deposit(amount)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please enter a valid amount")
        
        elif menu == "Transfer":
            st.subheader("💳 Transfer Money")
            recipient = st.text_input("Enter recipient username:")
            amount = st.number_input("Enter amount to transfer:", min_value=0.0, step=100.0)
            if st.button("Transfer"):
                if recipient and amount > 0:
                    success, message = atm.transfer(recipient, amount)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please enter recipient username and valid amount")
        
        elif menu == "Transaction History":
            st.subheader("📋 Transaction History")
            transactions = atm.get_transaction_history()
            if transactions:
                for i, transaction in enumerate(reversed(transactions[-10:]), 1):
                    st.write(f"{i}. {transaction}")
            else:
                st.info("No transactions yet")
        
        elif menu == "Logout":
            if st.button("Confirm Logout"):
                atm.logout()
                st.success("Logged out successfully!")
                st.rerun()
    
    else:
        # Login/Register page
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("🔐 Login")
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            if st.button("Login"):
                if username and password:
                    success, message = atm.login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
        
        with tab2:
            st.subheader("📝 Register")
            name = st.text_input("Full Name:")
            username = st.text_input("Choose Username:")
            password = st.text_input("Choose Password:", type="password")
            account_no = st.text_input("Account Number:")
            if st.button("Register"):
                if name and username and password and account_no:
                    success, message = atm.register_user(name, username, password, account_no)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields")

if __name__ == "__main__":
    main()
