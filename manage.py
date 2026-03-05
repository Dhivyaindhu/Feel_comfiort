#!/usr/bin/env python
import os
import sys

def auto_migrate():
    """Automatically run migrations before starting the server."""
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        try:
            from django.core.management import call_command
            print("[Feel Comfort] Checking database migrations...")
            call_command('migrate', '--run-syncdb', verbosity=1)
            print("[Feel Comfort] Database ready.")
        except Exception as e:
            print(f"[Feel Comfort] Migration warning: {e}")

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feel_comfort.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    auto_migrate()
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
