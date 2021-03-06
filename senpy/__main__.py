#!/usr/bin/python
# -*- coding: utf-8 -*-
#    Copyright 2014 J. Fernando Sánchez Rada - Grupo de Sistemas Inteligentes
#                                                       DIT, UPM
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""
Senpy is a modular sentiment analysis server. This script runs an instance of
the server.

"""

from flask import Flask
from senpy.extensions import Senpy
from senpy.utils import easy_test

import logging
import os
import sys
import argparse
import senpy

SERVER_PORT = os.environ.get("PORT", 5000)


def main():
    parser = argparse.ArgumentParser(description='Run a Senpy server')
    parser.add_argument(
        '--level',
        '-l',
        metavar='logging_level',
        type=str,
        default="WARN",
        help='Logging level')
    parser.add_argument(
        '--debug',
        '-d',
        action='store_true',
        default=False,
        help='Run the application in debug mode')
    parser.add_argument(
        '--default-plugins',
        action='store_true',
        default=False,
        help='Load the default plugins')
    parser.add_argument(
        '--host',
        type=str,
        default="0.0.0.0",
        help='Use 0.0.0.0 to accept requests from any host.')
    parser.add_argument(
        '--port',
        '-p',
        type=int,
        default=SERVER_PORT,
        help='Port to listen on.')
    parser.add_argument(
        '--plugins-folder',
        '-f',
        type=str,
        default='.',
        help='Where to look for plugins.')
    parser.add_argument(
        '--only-install',
        '-i',
        action='store_true',
        default=False,
        help='Do not run a server, only install plugin dependencies')
    parser.add_argument(
        '--only-test',
        '-t',
        action='store_true',
        default=False,
        help='Do not run a server, just test all plugins')
    parser.add_argument(
        '--only-list',
        '--list',
        action='store_true',
        default=False,
        help='Do not run a server, only list plugins found')
    parser.add_argument(
        '--data-folder',
        '--data',
        type=str,
        default=None,
        help='Where to look for data. It be set with the SENPY_DATA environment variable as well.')
    parser.add_argument(
        '--threaded',
        action='store_false',
        default=True,
        help='Run a threaded server')
    parser.add_argument(
        '--version',
        '-v',
        action='store_true',
        default=False,
        help='Output the senpy version and exit')
    args = parser.parse_args()
    if args.version:
        print('Senpy version {}'.format(senpy.__version__))
        print(sys.version)
        exit(1)
    rl = logging.getLogger()
    rl.setLevel(getattr(logging, args.level))
    app = Flask(__name__)
    app.debug = args.debug
    sp = Senpy(app, args.plugins_folder,
               default_plugins=args.default_plugins,
               data_folder=args.data_folder)
    if args.only_list:
        plugins = sp.plugins()
        maxwidth = max(len(x.id) for x in plugins)
        for plugin in plugins:
            import inspect
            fpath = inspect.getfile(plugin.__class__)
            print('{: <{width}} @ {}'.format(plugin.id, fpath, width=maxwidth))
        return
    sp.install_deps()
    if args.only_install:
        return
    sp.activate_all()
    if args.only_test:
        easy_test(sp.plugins())
        return
    print('Senpy version {}'.format(senpy.__version__))
    print('Server running on port %s:%d. Ctrl+C to quit' % (args.host,
                                                            args.port))
    app.run(args.host,
            args.port,
            threaded=args.threaded,
            debug=app.debug)
    sp.deactivate_all()


if __name__ == '__main__':
    main()
