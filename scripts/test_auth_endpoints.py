import requests

BASE = "http://127.0.0.1:5000"

# helper to pretty-print responses

def pp(r):
    try:
        return f"{r.status_code} {r.json()}"
    except Exception:
        return f"{r.status_code} {r.text}"

print("=== ADMIN SIGNUP (may already exist) ===")
resp = requests.post(f"{BASE}/auth/signup", json={
    "name": "Admin",
    "email": "admin@example.com",
    "password": "Password123!",
    "role": "admin",
})
print(pp(resp))

print("\n=== ADMIN LOGIN ===")
resp = requests.post(f"{BASE}/auth/login", json={
    "email": "admin@example.com",
    "password": "Password123!",
})
print(pp(resp))
admin_token = None
if resp.status_code == 200:
    admin_token = resp.json().get("access_token")

# create additional users
users = [
    {"name": "Lawyer", "email": "lawyer@example.com", "password": "Lawyer123!", "role": "lawyer"},
    {"name": "Judge", "email": "judge@example.com", "password": "Judge123!", "role": "judge"},
    {"name": "Citizen", "email": "citizen@example.com", "password": "Citizen123!", "role": "citizen"},
]
for u in users:
    print(f"\n=== SIGNUP {u['role'].upper()} ===")
    r = requests.post(f"{BASE}/auth/signup", json=u)
    print(pp(r))

# login each
tokens = {}
for u in users:
    print(f"\n=== LOGIN {u['role'].upper()} ===")
    r = requests.post(f"{BASE}/auth/login", json={"email": u["email"], "password": u["password"]})
    print(pp(r))
    if r.status_code == 200:
        tokens[u["role"]] = r.json().get("access_token")

# use lawyer to create a case
if "lawyer" in tokens:
    print("\n=== LAWYER CREATES CASE ===")
    headers = {"Authorization": f"Bearer {tokens['lawyer']}"}
    r = requests.post(f"{BASE}/case/create", json={"title": "Test Case"}, headers=headers)
    print(pp(r))
    case_id = None
    if r.status_code == 201:
        case_id = r.json().get("case", {}).get("id")

    # admin lists all cases
    if admin_token:
        print("\n=== ADMIN LISTS CASES ===")
        r2 = requests.get(f"{BASE}/case", headers={"Authorization": f"Bearer {admin_token}"})
        print(pp(r2))

    # admin assigns judge if case created
    if case_id and admin_token:
        print("\n=== ADMIN ASSIGNS JUDGE ===")
        r3 = requests.post(f"{BASE}/case/{case_id}/assign-judge", json={"judge_id": 2}, headers={"Authorization": f"Bearer {admin_token}"})
        print(pp(r3))
        # judge fetches case
        if "judge" in tokens:
            print("\n=== JUDGE GETS CASE ===")
            r4 = requests.get(f"{BASE}/case/{case_id}", headers={"Authorization": f"Bearer {tokens['judge']}"})
            print(pp(r4))

# AI endpoint example: lawyer asks explain-order
if "lawyer" in tokens:
    print("\n=== AI EXPLAIN-ORDER ===")
    headers = {"Authorization": f"Bearer {tokens['lawyer']}"}
    r = requests.post(f"{BASE}/ai/explain-order", json={"text": "The court grants the motion."}, headers=headers)
    print(pp(r))
