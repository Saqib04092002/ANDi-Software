# app.py
# Main Flask application file

from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime
from functools import wraps

app = Flask(__name__)
# A secret key is required to use sessions
app.secret_key = 'your_super_secret_key_change_this'

# --- Dummy Data ---
# In a real application, this data would come from a database.
dummy_data = {
    "stats": {
        "total_users": 1250,
        "banned_users": 65,
        "email_unverified": 230,
        "phone_unverified": 150,
    },
    "financials": {
        "deposit_balance": 5500830.50,
        "interest_balance": 120560.75,
    },
    "deposits": {
        "total_number": 780,
        "total_amount": 850300.00,
        "total_charge": 1250.25,
    },
    "other_bank_transactions": {
        "total": 45,
        "approved": 35,
        "rejected": 10,
        "pending": 5,
        "amount": 12500.00,
        "charge": 150.75
    },
    "withdraw_stats": {
        "total": 120,
        "approved": 100,
        "rejected": 15,
        "pending": 5,
        "amount": 45000.00,
        "charge": 350.50
    },
    "branches": [
        {"name": "Gandhi Road, Connaught Place, New Delhi", "status": "Active"},
        {"name": "SHAHJAHANPUR", "status": "Active"},
        {"name": "Noida", "status": "Active"},
    ],
    "other_banks": [
        {"name": "AXIS Bank", "status": "Active"},
        {"name": "HDFC Bank", "status": "Active"},
    ],
    "payment_gateways": [
        { "name": "PayPal", "logo": "https://i.ibb.co/QDy2g0z/paypal.png", "status": "Active" },
        { "name": "PerfectMoney", "logo": "https://i.ibb.co/JqgC6b3/perfect-money.png", "status": "Active" },
        { "name": "Stripe", "logo": "https://i.ibb.co/n7M4n3C/stripe.png", "status": "Active" },
        { "name": "Skrill", "logo": "https://i.ibb.co/bF9L8b5/skrill.png", "status": "Active" },
    ],
    "latest_news": [
        { "title": "Major System Upgrade Complete", "author": "Tech Team", "date": "2025-08-01", "status": "Active" },
        { "title": "New Interest Rates for Savings Accounts", "author": "Finance Dept.", "date": "2025-07-25", "status": "Active" }
    ],
    "transactions": {
        "requested": [
            { "username": "john.doe", "amount": 150.00, "charge": 2.50, "account": "1234567890", "trx_time": "2025-08-08 10:30", "processing_time": "1-2 Hours", "status": "Pending" }
        ],
        "approved": [
            { "username": "jane.smith", "amount": 200.00, "charge": 3.00, "account": "0987654321", "request_at": "2025-08-07 14:00", "approved_at": "2025-08-07 14:15", "processing_time": "15 Minutes", "status": "Completed" }
        ],
        "rejected": [
            { "username": "peter.jones", "amount": 50.00, "charge": 1.00, "account": "1122334455", "request_at": "2025-08-06 09:00", "reject_at": "2025-08-06 09:05", "processing_time": "5 Minutes", "status": "Rejected" }
        ]
    },
    "withdrawals": {
        "methods": [
            {"name": "Bank Transfer"},
            {"name": "PayPal"}
        ],
        "requested": [
            {"username": "susan.b", "amount": 300.00, "method": "PayPal", "account": "susan.b@example.com", "trx_time": "2025-08-09 11:00", "status": "Pending"}
        ],
        "approved": [
            {"username": "mike.t", "amount": 500.00, "charge": 5.00, "method": "Bank Transfer", "account": "5566778899", "requested_at": "2025-08-08 18:00", "approved_at": "2025-08-08 18:30", "status": "Completed"}
        ],
        "rejected": [
             {"username": "chris.g", "amount": 100.00, "charge": 2.00, "method": "PayPal", "account": "chris.g@example.com", "requested_at": "2025-08-07 12:00", "rejected_at": "2025-08-07 12:10", "status": "Rejected"}
        ]
    },
    "users": [
        {"username": "user1", "email": "user1@example.com", "status": "Active", "email_verified": True, "mobile_verified": True, "joined_at": "2025-01-15"},
        {"username": "user2", "email": "user2@example.com", "status": "Banned", "email_verified": True, "mobile_verified": True, "joined_at": "2025-02-20"},
        {"username": "user3", "email": "user3@example.com", "status": "Active", "email_verified": False, "mobile_verified": True, "joined_at": "2025-03-10"},
        {"username": "user4", "email": "user4@example.com", "status": "Active", "email_verified": True, "mobile_verified": False, "joined_at": "2025-04-05"},
    ],
    "settings": {
        "general": {
            "website_title": "ANDi Banking",
            "website_color": "#1672B7",
            "base_currency": "INR",
            "currency_symbol": "₹",
            "registration": True,
            "email_notification": True,
            "sms_notification": True,
            "email_verification": True,
            "sms_verification": True,
            "branding": "ANDi Banking from ANDi Software Solutions @ 2025"
        },
        "charge": {
            "fixed": 2,
            "percentage": 3
        },
        "email": {
            "from": "do-not-reply@andisoftware.com",
            "body": "Your email body template here..."
        },
        "sms": {
            "api_url": "https://api.infobip.com/api/v3/sendsms/plain?user=***&password=***&sender=iBanking&SMSText=[[message]]&GSM=[[number]]&type=longSMS"
        },
        "facebook": {
            "app_id": "205856110142667"
        }
    },
    "user": {
        "name": "Admin User",
        "email": "admin@andibanking.com",
        "password": "password", # Added password for admin
        "avatar_url": "https://placehold.co/40x40/EFEFEF/AAAAAA?text=A"
    }
}

# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', data=dummy_data)

# ... (keep all other routes like /branch, /other_banks, etc.) ...
@app.route('/branch', methods=['GET', 'POST'])
@login_required
def branch():
    if request.method == 'POST':
        dummy_data['branches'].append({"name": request.form.get('branch_name'), "status": "Active" if request.form.get('status') == '1' else 'Inactive'})
        return redirect(url_for('branch'))
    return render_template('branch.html', data=dummy_data)

@app.route('/branch/delete/<int:branch_index>')
@login_required
def delete_branch(branch_index):
    if 0 <= branch_index < len(dummy_data['branches']):
        dummy_data['branches'].pop(branch_index)
    return redirect(url_for('branch'))

@app.route('/other_banks', methods=['GET', 'POST'])
@login_required
def other_banks():
    if request.method == 'POST':
        if request.form.get('bank_name'):
            dummy_data['other_banks'].append({"name": request.form.get('bank_name'), "status": "Active"})
        return redirect(url_for('other_banks'))
    return render_template('other_banks.html', data=dummy_data)

@app.route('/payment_gateway')
@login_required
def payment_gateway():
    return render_template('payment_gateway.html', data=dummy_data)

@app.route('/latest_news')
@login_required
def latest_news():
    return render_template('latest_news.html', data=dummy_data)

@app.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    if request.method == 'POST':
        dummy_data['latest_news'].insert(0, {
            "title": request.form.get('title'), "author": request.form.get('author'),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "Active" if request.form.get('status') == '1' else 'Inactive'
        })
        return redirect(url_for('latest_news'))
    return render_template('add_news.html', data=dummy_data)

@app.route('/delete_news/<int:news_index>')
@login_required
def delete_news(news_index):
    if 0 <= news_index < len(dummy_data['latest_news']):
        dummy_data['latest_news'].pop(news_index)
    return redirect(url_for('latest_news'))

@app.route('/transactions/request')
@login_required
def transactions_request():
    return render_template('transactions_request.html', data=dummy_data)

@app.route('/transactions/approved')
@login_required
def transactions_approved():
    return render_template('transactions_approved.html', data=dummy_data)

@app.route('/transactions/rejected')
@login_required
def transactions_rejected():
    return render_template('transactions_rejected.html', data=dummy_data)

@app.route('/withdraw/request')
@login_required
def withdraw_request():
    return render_template('withdraw_request.html', data=dummy_data)

@app.route('/withdraw/approved')
@login_required
def withdraw_approved():
    return render_template('withdraw_approved.html', data=dummy_data)

@app.route('/withdraw/rejected')
@login_required
def withdraw_rejected():
    return render_template('withdraw_rejected.html', data=dummy_data)

@app.route('/withdraw/methods')
@login_required
def withdraw_methods():
    return render_template('withdraw_methods.html', data=dummy_data)

@app.route('/users/all')
@login_required
def users_all():
    return render_template('users_all.html', data=dummy_data, user_list=dummy_data['users'], title="All User")

@app.route('/users/verified')
@login_required
def users_verified():
    verified_list = [user for user in dummy_data['users'] if user['status'] == 'Active']
    return render_template('users_verified.html', data=dummy_data, user_list=verified_list, title="Verified User")

@app.route('/users/banned')
@login_required
def users_banned():
    banned_list = [user for user in dummy_data['users'] if user['status'] == 'Banned']
    return render_template('users_banned.html', data=dummy_data, user_list=banned_list, title="Banned user")

@app.route('/users/email_unverified')
@login_required
def users_email_unverified():
    unverified_list = [user for user in dummy_data['users'] if not user['email_verified']]
    return render_template('users_email_unverified.html', data=dummy_data, user_list=unverified_list, title="Email unverified user")

@app.route('/users/mobile_unverified')
@login_required
def users_mobile_unverified():
    unverified_list = [user for user in dummy_data['users'] if not user['mobile_verified']]
    return render_template('users_mobile_unverified.html', data=dummy_data, user_list=unverified_list, title="Mobile unverified user")

# --- Settings Routes ---
@app.route('/settings/general', methods=['GET', 'POST'])
@login_required
def settings_general():
    if request.method == 'POST':
        settings = dummy_data['settings']['general']
        settings['website_title'] = request.form.get('website_title')
        settings['website_color'] = request.form.get('website_color')
        settings['base_currency'] = request.form.get('base_currency')
        settings['currency_symbol'] = request.form.get('currency_symbol')
        settings['branding'] = request.form.get('branding')
        settings['registration'] = True if request.form.get('registration') else False
        settings['email_notification'] = True if request.form.get('email_notification') else False
        settings['sms_notification'] = True if request.form.get('sms_notification') else False
        settings['email_verification'] = True if request.form.get('email_verification') else False
        settings['sms_verification'] = True if request.form.get('sms_verification') else False
        flash('General settings updated successfully!', 'success')
        return redirect(url_for('settings_general'))
    return render_template('settings_general.html', data=dummy_data)

@app.route('/settings/charge', methods=['GET', 'POST'])
@login_required
def settings_charge():
    if request.method == 'POST':
        dummy_data['settings']['charge']['fixed'] = request.form.get('fixed_charge')
        dummy_data['settings']['charge']['percentage'] = request.form.get('percentage_charge')
        flash('Charge settings updated successfully!', 'success')
        return redirect(url_for('settings_charge'))
    return render_template('settings_charge.html', data=dummy_data)

@app.route('/settings/email', methods=['GET', 'POST'])
@login_required
def settings_email():
    if request.method == 'POST':
        dummy_data['settings']['email']['from'] = request.form.get('email_from')
        dummy_data['settings']['email']['body'] = request.form.get('email_body')
        flash('Email settings updated successfully!', 'success')
        return redirect(url_for('settings_email'))
    return render_template('settings_email.html', data=dummy_data)

@app.route('/settings/sms', methods=['GET', 'POST'])
@login_required
def settings_sms():
    if request.method == 'POST':
        dummy_data['settings']['sms']['api_url'] = request.form.get('sms_api')
        flash('SMS API settings updated successfully!', 'success')
        return redirect(url_for('settings_sms'))
    return render_template('settings_sms.html', data=dummy_data)

@app.route('/settings/facebook', methods=['GET', 'POST'])
@login_required
def settings_facebook():
    if request.method == 'POST':
        dummy_data['settings']['facebook']['app_id'] = request.form.get('facebook_app_id')
        flash('Facebook API settings updated successfully!', 'success')
        return redirect(url_for('settings_facebook'))
    return render_template('settings_facebook.html', data=dummy_data)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        dummy_data['user']['name'] = request.form.get('name')
        dummy_data['user']['email'] = request.form.get('email')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', data=dummy_data)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if old_password != dummy_data['user']['password']:
            flash('Old password is not correct!', 'danger')
        elif new_password != confirm_password:
            flash('New password and confirm password do not match!', 'danger')
        else:
            dummy_data['user']['password'] = new_password
            flash('Password changed successfully!', 'success')
        return redirect(url_for('change_password'))
    return render_template('change_password.html', data=dummy_data)

# --- Login/Logout Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == dummy_data['user']['password']:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong username or password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Generic route for other pages
@app.route('/<page_name>')
@login_required
def other_page(page_name):
    if page_name in ['branch', 'other_banks', 'payment_gateway', 'latest_news', 'add_news', 'user_management', 'settings', 'profile', 'change_password']:
        if page_name == 'user_management': return redirect(url_for('users_all'))
        if page_name == 'settings': return redirect(url_for('settings_general'))
        return redirect(url_for(page_name))
    return render_template('placeholder.html', page_title=page_name.replace('_', ' ').title(), data=dummy_data)

if __name__ == '__main__':
    app.run(debug=True)
