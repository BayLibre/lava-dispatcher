# Copyright (C) 2012 Linaro Limited
#
# Author: Antonio Terceiro <antonio.terceiro@linaro.org>
#
# This file is part of LAVA Dispatcher.
#
# LAVA Dispatcher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LAVA Dispatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along
# with this program; if not, see <http://www.gnu.org/licenses>.

# TODO document all the crazy stuff needed by LAVA to deal with the Nexus,
# constraints, hacks, etc

import subprocess
import pexpect
from time import sleep
import logging
import contextlib

from lava_dispatcher.device.target import (
    Target
)
from lava_dispatcher.downloader import (
    download_image
)
from lava_dispatcher.utils import (
        logging_spawn
)

class NexusTarget(Target):

    def __init__(self, context, config):
        super(NexusTarget, self).__init__(context, config)
        self._powered_on = False

    def deploy_android(self, boot, system, userdata):
        sdir = self.scratch_dir

        boot = download_image(boot, self.context, sdir, decompress=False)
        system = download_image(system, self.context, sdir, decompress=False)
        userdata = download_image(userdata, self.context, sdir, decompress=False)

        self.reboot()

        self.fastboot('erase boot')

        self.fastboot('flash system %s' % system)
        self.fastboot('flash userdata %s' % userdata)

        self.deployment_data = Target.android_deployment_data
        self.deployment_data['boot_image'] = boot

    def power_on(self):
        self.reboot()
        self.fastboot('reboot')
        sleep(10) # wait for the bootloader to reboot
        self.fastboot('boot %s' % self.deployment_data['boot_image'])
        self.adb('wait-for-device')
        self._powered_on = True
        proc = self.adb('shell', spawn = True)
        proc.sendline("") # required to put the adb shell in a reasonable state
        proc.sendline("export PS1='%s'" % self.deployment_data['TESTER_PS1'])
        self._runner = self._get_runner(proc)

        self._system_etc_cleanup()

        return proc

    def _system_etc_cleanup(self):
        """ This makes it a lot faster to pull/push from/to /system/etc. There
        is A LOT of useless files under /system/etc/terminfo/.
        """
        with self.make_filesystem_readwrite('/system'):
            runner = self._runner
            runner.run('mv /system/etc/terminfo/v/vt100 /system/etc')
            runner.run('rm -r /system/etc/terminfo/*')
            runner.run('mkdir /system/etc/terminfo/v')
            runner.run('mv /system/etc/vt100 /system/etc/terminfo/v/')

    def reboot(self):
        # tell android to reboot. A failure probably means that the device is not
        # booted on android, and we ignore that.
        self.adb('reboot', ignore_failure = True)
        sleep(10)

    # TODO implement power_off

    # TODO implement file_system
    @contextlib.contextmanager
    def file_system(self, partition, directory):

        if not self._powered_on:
            self.power_on()

        mount_point = self.get_partition_mount_point(partition)

        with self.make_filesystem_readwrite(mount_point):
            host_dir = '%s/mnt/%s' % (self.scratch_dir, directory)
            target_dir = '%s/%s' % (mount_point, directory)

            subprocess.check_call(['mkdir', '-p', host_dir])
            self.adb('pull %s %s' % (target_dir, host_dir), ignore_failure = True)

            yield host_dir

            self.adb('push %s %s' % (host_dir, target_dir))

    def get_partition_mount_point(self, partition):
        lookup = {
            self.config.data_part_android_org: '/data',
            self.config.sys_part_android_org: '/system',
        }
        return lookup[partition]

    @contextlib.contextmanager
    def make_filesystem_readwrite(self, mount_point):
        if mount_point  == '/system':
            self._runner.run("mount -o remount,rw %s" % mount_point)
        yield
        if mount_point  == '/system':
            self._runner.run("mount -o remount,ro %s" % mount_point)

    # TODO implement extract_tarball

    def get_device_version(self):
        # this is tricky, because fastboot does not have a visible version
        # number. For now let's use just the adb version number.
        return subprocess.check_output(
            "adb version | sed 's/.* version //'",
            shell = True
        ).strip()

    # TODO implement get_test_data_attachments (??)

    def adb(self, args, ignore_failure = False, spawn = False):
        cmd = self.config.adb_command + ' ' + args
        if spawn:
            return logging_spawn(cmd, timeout = 60)
        else:
            self._call(cmd, ignore_failure)

    def fastboot(self, args, ignore_failure = False):
        self._call(self.config.fastboot_command + ' ' + args, ignore_failure)

    def _call(self, cmd, ignore_failure):
        if ignore_failure:
            subprocess.call(cmd, shell = True)
        else:
            subprocess.check_call(cmd, shell = True)

target_class = NexusTarget
