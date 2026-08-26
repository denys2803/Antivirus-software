import hashlib

file_path = "C:\\Users\\Preds\\Desktop\\МАН прототип антивірусної системи\\Тест\\143.0.7499.110\\chrome.exe.sig"

with open(file_path, 'rb') as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()

print(file_hash)
