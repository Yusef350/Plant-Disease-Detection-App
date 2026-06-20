"""
End-to-end API test script.
Run: python test_api.py
"""

import json
import urllib.request
import urllib.error
import sys
import time

BASE = "http://127.0.0.1:5000"
TOKEN = None
USER_ID = None
TEST_EMAIL = f"apitester_{int(time.time())}@test.com"
TEST_PASSWORD = "SecurePass123"


def req(method, path, data=None, auth=False):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if auth and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test(name, status, body, expected_status):
    ok = status == expected_status
    icon = "✅" if ok else "❌"
    print(f"  {icon} {name} — {status}")
    if not ok:
        print(f"     Expected {expected_status}, got {status}: {body}")
    return ok


def main():
    global TOKEN, USER_ID
    passed = 0
    failed = 0

    print("\n🔬 PLANT DISEASE DETECTION API — TEST SUITE\n")

    # ── 1. Health Check ──────────────────────────────────────────────
    print("1️⃣  Health Check")
    s, b = req("GET", "/api/health")
    if test("GET /api/health", s, b, 200):
        passed += 1
    else:
        failed += 1

    # ── 2. Auth — Register ───────────────────────────────────────────
    print("\n2️⃣  Authentication")

    # Register new user
    s, b = req("POST", "/api/auth/register", {
        "displayName": "API Tester",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if test("POST /api/auth/register (new user)", s, b, 201):
        passed += 1
        TOKEN = b.get("token")
        USER_ID = b.get("user", {}).get("id")
    else:
        failed += 1

    # Register duplicate email
    s, b = req("POST", "/api/auth/register", {
        "displayName": "Dup",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if test("POST /api/auth/register (duplicate → 409)", s, b, 409):
        passed += 1
    else:
        failed += 1

    # Register validation — bad email
    s, b = req("POST", "/api/auth/register", {
        "displayName": "Bad",
        "email": "not-an-email",
        "password": "123456"
    })
    if test("POST /api/auth/register (bad email → 400)", s, b, 400):
        passed += 1
    else:
        failed += 1

    # ── 3. Auth — Login ──────────────────────────────────────────────
    s, b = req("POST", "/api/auth/login", {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if test("POST /api/auth/login (valid)", s, b, 200):
        passed += 1
        TOKEN = b.get("token")
    else:
        failed += 1

    # Login wrong password
    s, b = req("POST", "/api/auth/login", {
        "email": TEST_EMAIL,
        "password": "WrongPassword"
    })
    if test("POST /api/auth/login (wrong password → 401)", s, b, 401):
        passed += 1
    else:
        failed += 1

    # ── 4. Auth — Me ─────────────────────────────────────────────────
    s, b = req("GET", "/api/auth/me", auth=True)
    if test("GET /api/auth/me (authenticated)", s, b, 200):
        passed += 1
    else:
        failed += 1

    # Me without token
    s, b = req("GET", "/api/auth/me")
    if test("GET /api/auth/me (no token → 401)", s, b, 401):
        passed += 1
    else:
        failed += 1

    # ── 5. Diseases ──────────────────────────────────────────────────
    print("\n3️⃣  Diseases (Knowledge Base)")
    s, b = req("GET", "/api/diseases")
    if test("GET /api/diseases (list all)", s, b, 200):
        passed += 1
        total = b.get("total", 0)
        print(f"     → {total} diseases in database")
        if total > 0:
            first_id = b["diseases"][0]["id"]
    else:
        failed += 1
        first_id = None

    # Disease detail
    if first_id:
        s, b = req("GET", f"/api/diseases/{first_id}")
        if test(f"GET /api/diseases/{{id}} (detail)", s, b, 200):
            passed += 1
            d = b["disease"]
            print(f"     → {d['name']}: {d['description'][:60]}...")
        else:
            failed += 1

    # Disease not found
    s, b = req("GET", "/api/diseases/000000000000000000000000")
    if test("GET /api/diseases/{{bad_id}} (→ 404)", s, b, 404):
        passed += 1
    else:
        failed += 1

    # ── 6. User Profile ──────────────────────────────────────────────
    print("\n4️⃣  User Profile")
    s, b = req("GET", "/api/users/profile", auth=True)
    if test("GET /api/users/profile", s, b, 200):
        passed += 1
        print(f"     → User: {b['user']['displayName']}, Scans: {b['stats']['totalScans']}")
    else:
        failed += 1

    # Update profile
    s, b = req("PUT", "/api/users/profile", {"displayName": "Updated Name"}, auth=True)
    if test("PUT /api/users/profile (update name)", s, b, 200):
        passed += 1
        print(f"     → New name: {b['user']['displayName']}")
    else:
        failed += 1

    # Change password
    NEW_PASSWORD = "NewSecurePass456"
    s, b = req("PUT", "/api/users/password", {
        "currentPassword": TEST_PASSWORD,
        "newPassword": NEW_PASSWORD
    }, auth=True)
    if test("PUT /api/users/password", s, b, 200):
        passed += 1
    else:
        failed += 1

    # Login with new password
    s, b = req("POST", "/api/auth/login", {
        "email": TEST_EMAIL,
        "password": NEW_PASSWORD
    })
    if test("POST /api/auth/login (new password)", s, b, 200):
        passed += 1
        TOKEN = b.get("token")
    else:
        failed += 1

    # ── 7. Scans (without AI model — expect graceful error) ─────────
    print("\n5️⃣  Scans")

    # List scans (empty)
    s, b = req("GET", "/api/scans", auth=True)
    if test("GET /api/scans (empty history)", s, b, 200):
        passed += 1
        print(f"     → {b['total']} scans")
    else:
        failed += 1

    # Scan without image
    s, b = req("POST", "/api/scans", auth=True)
    if test("POST /api/scans (no image → 400)", s, b, 400):
        passed += 1
    else:
        failed += 1

    # Scan not found
    s, b = req("GET", "/api/scans/000000000000000000000000", auth=True)
    if test("GET /api/scans/{{bad_id}} (→ 404)", s, b, 404):
        passed += 1
    else:
        failed += 1

    # ── 8. Admin — Access denied for normal user ─────────────────────
    print("\n6️⃣  Admin (access control)")
    s, b = req("GET", "/api/admin/users", auth=True)
    if test("GET /api/admin/users (non-admin → 403)", s, b, 403):
        passed += 1
    else:
        failed += 1

    s, b = req("GET", "/api/admin/analytics", auth=True)
    if test("GET /api/admin/analytics (non-admin → 403)", s, b, 403):
        passed += 1
    else:
        failed += 1

    # ── Summary ──────────────────────────────────────────────────────
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print("  ⚠️  Some tests failed — check output above.")
    print(f"{'='*50}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
