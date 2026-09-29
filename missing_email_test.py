





email = None

if email is None:
    print("Email is missing.")
else:
    clean_email = email.strip().lower()
    print(clean_email)