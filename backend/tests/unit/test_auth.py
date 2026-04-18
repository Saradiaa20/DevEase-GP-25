# import pytest
# from datetime import timedelta

# from app.core.auth import (
#     get_password_hash,
#     verify_password,
#     create_access_token,
#     decode_token,
#     check_permission
# )


# # ---------------------------
# # Password Tests
# # ---------------------------

# def test_password_hashing():
#     password = "mysecret123"
#     hashed = get_password_hash(password)

#     assert hashed != password
#     assert isinstance(hashed, str)


# def test_verify_password_correct():
#     password = "mypassword"
#     hashed = get_password_hash(password)

#     assert verify_password(password, hashed) is True


# def test_verify_password_wrong():
#     password = "mypassword"
#     hashed = get_password_hash(password)

#     assert verify_password("wrongpassword", hashed) is False


# # ---------------------------
# # JWT Token Tests
# # ---------------------------

# def test_create_access_token():
#     data = {"sub": "user1"}

#     token = create_access_token(data)

#     assert isinstance(token, str)
#     assert len(token) > 0


# def test_decode_valid_token():
#     data = {"sub": "user1"}
#     token = create_access_token(data)

#     decoded = decode_token(token)

#     assert decoded is not None
#     assert decoded["sub"] == "user1"


# def test_decode_invalid_token():
#     token = "invalid.token.value"

#     decoded = decode_token(token)

#     assert decoded is None


# def test_token_expiration():
#     data = {"sub": "user1"}

#     token = create_access_token(data, expires_delta=timedelta(seconds=1))

#     import time
#     time.sleep(2)

#     decoded = decode_token(token)

#     assert decoded is None


# # ---------------------------
# # Permission Tests
# # ---------------------------

# def test_permission_valid():
#     assert check_permission("team_lead", "developer") is True


# def test_permission_equal():
#     assert check_permission("developer", "developer") is True


# def test_permission_invalid():
#     assert check_permission("developer", "team_lead") is False


# def test_permission_unknown_role():
#     assert check_permission("intern", "developer") is False