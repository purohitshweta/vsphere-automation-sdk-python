
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

import datetime
import logging

from com.vmware.vcenter.lcm.deployment_client import MigrationUpgrade

logger = logging.getLogger(__name__)


class ApplySpec:
    def __init__(self, schedule_downtime: int = None, pause_before_switchover: bool = None):
        """
        Helper class to populate the apply spec for RDU.
        :param schedule_downtime: After how many hours to schedule the downtime of the upgrade
        :param pause_before_switchover: Whether to pause the upgrade before the downtime starts.
        """
        if schedule_downtime and pause_before_switchover:
            logger.error("Cannot create an apply spec which has both a pause point and a scheduled switchover time.")
            raise Exception("Apply spec has both schedule_downtime and pause_before_switchover set.")

        self.start_switchover = schedule_downtime
        self.pause_before_switchover = pause_before_switchover

    def get_apply_spec(self):
        """
        get_apply_spec builds the MigrationUpgrade.ApplySpec object from the provided parameters.
        :return:
        """
        apply_spec = MigrationUpgrade.ApplySpec()
        if self.start_switchover:
            current_time = datetime.datetime.utcnow()
            apply_spec.start_switchover = current_time + datetime.timedelta(hours=self.start_switchover)

        if self.pause_before_switchover:
            apply_spec.pause = MigrationUpgrade.PausePolicy.BEFORE_SWITCHOVER

        return apply_spec
