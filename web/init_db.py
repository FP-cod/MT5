"""Initialize the accounting DB (helper script).
Usage: python web/init_db.py --create-admin
"""
from pathlib import Path
from web import accounting
import argparse

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "accounting.db"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-admin', action='store_true')
    parser.add_argument('--username', type=str, default='admin')
    parser.add_argument('--password', type=str, help='password for admin (if --create-admin)')
    args = parser.parse_args()
    accounting.init_db(DB_PATH)
    print("DB initialized at", DB_PATH)
    if args.create_admin:
        if args.password is None:
            print("Specify --password to create admin")
        else:
            accounting.create_user(DB_PATH, args.username, args.password)
            print("Admin user created")
