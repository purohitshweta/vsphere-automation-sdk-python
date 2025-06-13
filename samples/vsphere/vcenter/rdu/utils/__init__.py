"""
* *******************************************************
* Copyright (c) Broadcom, Inc. 2025. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'Broadcom, Inc.'
__vcenter_version__ = '9.0.0'

import requests
import logging
import argparse

from com.vmware.cis_client import Session
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.lib.connect import get_requests_connector
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.client.security_context_filter import \
    LegacySecurityContextFilter
from vmware.vapi.security.user_password import \
    create_user_password_security_context

from samples.vsphere.common import sample_cli
from samples.vsphere.common.ssl_helper import get_unverified_session

logger = logging.getLogger(__name__)


def get_plugin_update_arg_parser(parser: argparse.ArgumentParser = None):
    if not parser:
        parser = sample_cli.build_arg_parser()

    parser.add_help = True
    parser.add_argument('--plugin-repo',
                        action='store',
                        required=True,
                        help="URL to the lifecycle plugin repository.")
    return parser


def get_rdu_arg_parser(parser: argparse.ArgumentParser = None):
    if not parser:
        parser = sample_cli.build_arg_parser()

    parser.add_help = True
    parser.add_argument('--target-temp-password',
                        action='store',
                        required=True,
                        help="A temporary password for the deployed target machine")
    parser.add_argument('--target-version',
                        action='store',
                        required=True,
                        help="The target version in format A.B.C.DDDD")
    parser.add_argument('--target-upgrade-repo',
                        action='store',
                        required=True,
                        help="URL to the target upgrade repository.")
    parser.add_argument('--target-ova',
                        action='store',
                        required=True,
                        help="URL to the target machine's OVA")
    parser.add_argument('--autocancellation',
                        action='store_true',
                        help="Auto cancel if the upgrade fails")
    parser.add_argument('--preserve-original-name',
                        action='store_true',
                        help="Preserve the original name of the source vCenter VM.")

    return parser


def get_vcenter_client(server: str, username: str, password: str, skip_verification: bool, endpoint: str = "lcm/api"):
    """
    Create the session and the connection to the desired vCenter
    :param server: vCenter hostname
    :param username: vCenter username for authentication
    :param password: vCenter password for authentication
    :param skip_verification: Whether to disable the certificate verification when creating a session.
    :param endpoint: Endpoint in which to call the vCenter api's. For RDU the default is lcm/api.
    :return: Configuration for the vapi stubs.
    """
    session = get_unverified_session() if skip_verification else None
    if not session:
        session = requests.Session()

    host_url = "https://{}/{}".format(server, endpoint)
    logger.info("Connecting on endpoint: %s", host_url)

    sec_ctx = create_user_password_security_context(username,
                                                    password)
    session_svc = Session(
        StubConfigurationFactory.new_std_configuration(
            get_requests_connector(
                session=session, url=host_url,
                provider_filter_chain=[
                    LegacySecurityContextFilter(
                        security_context=sec_ctx)])))
    session_id = session_svc.create()

    logger.info("Authenticating with session ID: %s", session_id)

    sec_ctx = create_session_security_context(session_id)
    stub_config = StubConfigurationFactory.new_std_configuration(
        get_requests_connector(
            session=session, url=host_url,
            provider_filter_chain=[
                LegacySecurityContextFilter(
                    security_context=sec_ctx)]))

    return stub_config, session_id
