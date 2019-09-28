#!/usr/bin/env python
import os
import re
import socket
import sys
import time
from typing import List

import django
import pyuwsgi
from django.contrib.auth import get_user_model
from django.core.management import call_command, execute_from_command_line


DEFAULT_ENVS = {
    "DJANGO_SETTINGS_MODULE": "pydis_site.settings",
    "SUPER_USERNAME": "admin",
    "SUPER_PASSWORD": "admin",
    "DEFAULT_BOT_API_KEY": "badbot13m0n8f570f942013fc818f234916ca531",
}


for key, value in DEFAULT_ENVS.items():
    os.environ.setdefault(key, value)


class SiteManager:
    """
    Manages the preparation and serving of the website.

    Handles both development and production environments.

    Usage:
        manage.py run [option]...

    Options:
        --debug    Runs a development server with debug mode enabled.
        --silent   Sets minimal console output.
        --verbose  Sets verbose console output.
    """

    def __init__(self, args: List[str]):
        self.debug = "--debug" in args
        self.silent = "--silent" in args

        if self.silent:
            self.verbosity = 0
        else:
            self.verbosity = 2 if "--verbose" in args else 1

        if self.debug:
            os.environ.setdefault("DEBUG", "true")
            print("Starting in debug mode.")

    @staticmethod
    def create_superuser() -> None:
        """Create a default django admin super user in development environments."""
        print("Creating a superuser.")

        name = os.environ["SUPER_USERNAME"]
        password = os.environ["SUPER_PASSWORD"]
        bot_token = os.environ["DEFAULT_BOT_API_KEY"]
        user = get_user_model()

        # Get or create admin superuser.
        if user.objects.filter(username=name).exists():
            user = user.objects.get(username=name)
            print('Admin superuser already exists.')
        else:
            user = user.objects.create_superuser(name, '', password)
            print('Admin superuser created.')

        # Setup a default bot token to connect with site API
        from rest_framework.authtoken.models import Token
        token, is_new = Token.objects.update_or_create(user=user)
        if token.key != bot_token:
            token.delete()
        token, is_new = Token.objects.update_or_create(user=user, key=bot_token)
        if is_new:
            print(f"New bot token created: {token}")
        else:
            print(f"Existing bot token found: {token}")

    @staticmethod
    def wait_for_postgres() -> None:
        """Wait for the PostgreSQL database specified in DATABASE_URL."""
        print("Waiting for PostgreSQL database.")

        # Get database URL based on environmental variable passed in compose
        database_url = os.environ["DATABASE_URL"]
        match = re.search(r"@(\w+):(\d+)/", database_url)
        if not match:
            raise OSError("Valid DATABASE_URL environmental variable not found.")
        domain = match.group(1)
        port = int(match.group(2))

        # Attempt to connect to the database socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                # Ignore 'incomplete startup packet'
                s.connect((domain, port))
                s.shutdown(socket.SHUT_RDWR)
                print("Database is ready.")
                break
            except socket.error:
                print("Not ready yet, retrying.")
                time.sleep(0.5)

    def prepare_server(self) -> None:
        """Perform preparation tasks before running the server."""
        django.setup()

        if self.debug:
            self.wait_for_postgres()
            self.create_superuser()

        print("Applying migrations.")
        call_command("migrate", verbosity=self.verbosity)
        print("Collecting static files.")
        call_command("collectstatic", interactive=False, clear=True, verbosity=self.verbosity)

    def run_server(self) -> None:
        """Prepare and run the web server."""
        in_reloader = os.environ.get('RUN_MAIN') == 'true'

        # Prevent preparing twice when in dev mode due to reloader
        if not self.debug or in_reloader:
            self.prepare_server()

        print("Starting server.")

        # Run the development server
        if self.debug:
            call_command("runserver", "0.0.0.0:8000")
            return

        # Run uwsgi for production server
        pyuwsgi.run(["--ini", "docker/uwsgi.ini"])


def main() -> None:
    """Entry point for Django management script."""
    # Use the custom site manager for launching the server
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        SiteManager(sys.argv).run_server()

    # Pass any others directly to standard management commands
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
