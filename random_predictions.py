#!/usr/bin/env python
"""Generate 10 random cases and call /ai/predict-delay endpoint."""
import requests
import random
import json

BASE_URL = "http://127.0.0.1:5000"

# distributions matching training generator
case_types = ["civil", "criminal", "family", "tax", "labor"]
priorities = ["low", "medium", "high"]
court_levels = ["magistrate", "district", "high_court", "supreme"]

# helper to pick with weights similar to generator

def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]


def random_case():
    case_type = weighted_choice(case_types, [0.4, 0.3, 0.15, 0.05, 0.1])
    number_of_hearings = max(1, int(random.gauss(3, 1)))
    judge_workload = max(1, int(random.gauss(50, 15)))
    document_count = max(0, int(random.poisson(5) if hasattr(random, 'poisson') else random.gauss(5,2)))
    case_priority = weighted_choice(priorities, [0.6, 0.3, 0.1])
    filing_to_first_hearing_days = abs(int(random.expovariate(1/30)))
    court_level = weighted_choice(court_levels, [0.5, 0.35, 0.1, 0.05])
    previous_adjournments = int(random.poisson(1) if hasattr(random, 'poisson') else max(0,int(random.gauss(1,1))))
    return {
        "case_type": case_type,
        "number_of_hearings": number_of_hearings,
        "judge_workload": judge_workload,
        "document_count": document_count,
        "case_priority": case_priority,
        "filing_to_first_hearing_days": filing_to_first_hearing_days,
        "court_level": court_level,
        "previous_adjournments": previous_adjournments,
    }


def get_token():
    r = requests.post(f"{BASE_URL}/auth/login", json={"email":"admin@example.com","password":"admin123"}, timeout=10)
    return r.json().get("access_token")


def main():
    token = get_token()
    if not token:
        print("Failed to obtain JWT")
        return
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    for i in range(10):
        case = random_case()
        r = requests.post(f"{BASE_URL}/ai/predict-delay", json={"case_data": case}, headers=headers, timeout=10)
        print(f"\n=== Random Case {i+1} input ===")
        print(case)
        print("response:", json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    main()
