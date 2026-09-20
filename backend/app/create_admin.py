"""Create or promote a Signalpost administrator.

Usage from the backend directory:
    python -m app.create_admin --email admin@example.com --name Admin
"""

import argparse
import getpass
import secrets

from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.utils.auth import PasswordManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote a Signalpost administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="Signalpost Admin")
    args = parser.parse_args()
    password = getpass.getpass("Admin password: ")

    valid, message = PasswordManager.validate_password_strength(password)
    if not valid:
        raise SystemExit(message)

    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            user = User(
                id=secrets.token_urlsafe(36),
                name=args.name,
                email=args.email,
                password_hash=PasswordManager.hash_password(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(user)
        else:
            user.name = args.name
            user.password_hash = PasswordManager.hash_password(password)
            user.role = UserRole.ADMIN
            user.is_active = True
        db.commit()
        print(f"Administrator ready: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
