#!/usr/bin/env python
import os
import sys
import socket
import time

if __name__ == "__main__":

    postgres_is_alive = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while not postgres_is_alive:
        try:
            s.connect(('postgresql', 5432))
        except socket.error:
            time.sleep(1)
        else:
            postgres_is_alive = True

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
