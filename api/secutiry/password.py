from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(password: str) -> str:

    return _ph.hash(password)


def verify_password(hashed_password: str, password: str) -> bool:

    try:

        match = _ph.verify(hashed_password, password)

        return match
    
    except VerifyMismatchError:

        return False
