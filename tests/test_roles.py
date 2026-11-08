from opera.auth import User, allowed, can_access_bu, hash_password, verify_password


def test_hash_and_roles():
    stored = hash_password("A-strong-password-2026", "00112233445566778899aabbccddeeff")
    assert verify_password("A-strong-password-2026", stored)
    assert not verify_password("wrong", stored)
    viewer = User("v", "Viewer", "Viewer", ("cement",))
    operator = User("o", "Operator", "Operator", ("refinery",))
    admin = User("a", "Admin", "Super Admin", ("*",))
    assert allowed(viewer, "view") and not allowed(viewer, "input")
    assert allowed(operator, "events") and not allowed(operator, "configure")
    assert allowed(admin, "users") and can_access_bu(admin, "bu9")
    assert can_access_bu(viewer, "cement") and not can_access_bu(viewer, "refinery")
