import os
files = [r"C:\Users\xingk\bank\index.html", r"C:\Users\xingk\bank\admin.html"]
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace("#0d74ce", "#d71e28")
    content = content.replace("submitWells Fargo", "submitWf")
    content = content.replace("chase-card", "wf-card")
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
