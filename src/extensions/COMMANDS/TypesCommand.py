###
# Copyright 2017 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
""" Types Command for RDMC """

import sys

from optparse import OptionParser, SUPPRESS_HELP

import redfish.ris

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                                                    InvalidCommandLineErrorOPTS

class TypesCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='types',\
            usage='types [TYPE] [OPTIONS]\n\n\tRun to display currently ' \
            'available selectable types\n\texample: types',\
            summary='Displays all selectable types within the currently'\
                    ' logged in server.',\
            aliases=['types'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def typesfunction(self, line, returntypes=False):
        """ Main types worker function

        :param line: command line input
        :type line: string.
        :param returntypes: flag to determine if types should be printed
        :type returntypes: boolean.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        self.typesvalidation(options)

        try:
            if not args:
                typeslist = list()
                typeslist = list(set(self._rdmc.app.types(options.fulltypes)))
                typeslist.sort()

                if not returntypes:
                    sys.stdout.write("Type options:")
                    sys.stdout.write('\n')

                    for item in typeslist:
                        sys.stdout.write(item)
                        sys.stdout.write('\n')
                else:
                    return typeslist
            else:
                raise InvalidCommandLineError("The 'types' command does not "\
                                                        "take any arguments.")

        except redfish.ris.InstanceNotFoundError, infe:
            raise redfish.ris.InstanceNotFoundError(infe)

    def run(self, line):
        """ Wrapper function for types main function

        :param line: command line input
        :type line: string.
        """
        self.typesfunction(line)

        #Return code
        return ReturnCodes.SUCCESS

    def typesvalidation(self, options):
        """ types method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

        if inputline or not client:
            runlogin = True
            if not inputline:
                sys.stdout.write(u'Local login initiated...\n')
        if options.includelogs:
            inputline.extend(["--includelogs"])
        if options.path:
            inputline.extend(["--path", options.path])

        if runlogin:
            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            '--url',
            dest='url',
            help="Use the provided iLO URL to login.",
            default=None,
        )
        customparser.add_option(
            '-u',
            '--user',
            dest='user',
            help="If you are not logged in yet, including this flag along"\
            " with the password and URL flags can be used to log into a"\
            " server in the same command.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="""Use the provided iLO password to log in.""",
            default=None,
        )
        customparser.add_option(
            '--includelogs',
            dest='includelogs',
            action="store_true",
            help="Optionally include logs in the data retrieval process.",
            default=False,
        )
        customparser.add_option(
            '--path',
            dest='path',
            help="Optionally set a starting point for data collection."\
            " If you do not specify a starting point, the default path"\
            " will be /redfish/v1/. Note: The path flag can only be specified"\
            " at the time of login, so if you are already logged into the"\
            " server, the path flag will not change the path. If you are"\
            " entering a command that isn't the login command, but include"\
            " your login information, you can still specify the path flag"\
            " there.  ",
            default=None,
        )
        customparser.add_option(
            '--fulltypes',
            dest='fulltypes',
            action='store_true',
            help="Optionally include this flag if you would prefer to "\
            "return the full type name instead of the simplified versions" \
            " (Redfish only option).",
            default=None
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
