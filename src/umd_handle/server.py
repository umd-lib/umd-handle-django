#!/usr/bin/env python
"""Server startup script."""

import click
from waitress import serve

from umd_handle.wsgi import application


@click.command()
@click.option(
    '--listen',
    default='0.0.0.0:3000',
    help='Address and port to listen on. Default is "0.0.0.0:3000".',
    metavar='[ADDRESS]:PORT',
)
def run(listen: str):
    serve(application, listen=listen, threads=8)
