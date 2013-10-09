# Copyright (C) 2013 Linaro Limited
#
# Author: Fu Wei <fu.wei@linaro.org>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along
# with this program; if not, see <http://www.gnu.org/licenses>.
import logging

import lava_dispatcher.actions.lmp.eth as lmp_eth
import lava_dispatcher.actions.lmp.sata as lmp_sata
import lava_dispatcher.actions.lmp.hdmi as lmp_hdmi
import lava_dispatcher.actions.lmp.lsgpio as lmp_lsgpio
import lava_dispatcher.actions.lmp.usb as lmp_usb

from lava_dispatcher.actions.lmp.board import get_module_serial


#for LMP signal process
def lsgpio_signal(connection, config, command, module_name):
    if not connection:
        logging.error("No connection available for lsgpio_signal")
        return
    lmp_lsgpio_id = get_module_serial(config.lmp_lsgpio_id, module_name, config)
    if not lmp_lsgpio_id:
        logging.error("No lmp_lsgpio_id available for lsgpio_signal")
        return
    logging.debug("Handling signal <LAVA_LSGPIO %s>" % command)
    if command == "a_in":
        lmp_lsgpio.a_dir_in(lmp_lsgpio_id)
    elif command == "a_out":
        lmp_lsgpio.a_dir_out(lmp_lsgpio_id)
    elif command == "b_in":
        lmp_lsgpio.b_dir_in(lmp_lsgpio_id)
    elif command == "b_out":
        lmp_lsgpio.b_dir_out(lmp_lsgpio_id)
    elif command == "passthru":
        lmp_lsgpio.audio_passthru(lmp_lsgpio_id)
    elif command == "disconnect":
        lmp_lsgpio.audio_disconnect(lmp_lsgpio_id)

    message_str = ""
    connection.sendline("<LAVA_LSGPIO_COMPLETE%s>" % message_str)


def eth_signal(connection, config, command, module_name):
    if not connection:
        logging.error("No connection available for eth_signal")
        return
    lmp_eth_id = get_module_serial(config.lmp_eth_id, module_name, config)
    if not lmp_eth_id:
        logging.error("No lmp_eth_id available for eth_signal")
        return
    logging.debug("Handling signal <LAVA_ETH %s>" % command)
    if command == "passthru":
        lmp_eth.passthru(lmp_eth_id)
    elif command == "disconnect":
        lmp_eth.disconnect(lmp_eth_id)

    message_str = ""
    connection.sendline("<LAVA_ETH_COMPLETE%s>" % message_str)


def hdmi_signal(connection, config, command, module_name, fakeedid=None):
    if not connection:
        logging.error("No connection available for hdmi_signal")
        return
    lmp_hdmi_id = get_module_serial(config.lmp_hdmi_id, module_name, config)
    if not lmp_hdmi_id:
        logging.error("No lmp_hdmi_id available for hdmi_signal")
        return
    logging.debug("Handling signal <LAVA_HDMI %s>" % command)
    if command == "passthru":
        lmp_hdmi.passthru(lmp_hdmi_id)
    elif command == "disconnect":
        lmp_hdmi.disconnect(lmp_hdmi_id)
    elif command == "fakeedid":
#FIXME: How to pass the fake edid to target board?
        lmp_hdmi.fake(lmp_hdmi_id)

    message_str = ""
    connection.sendline("<LAVA_HDMI_COMPLETE%s>" % message_str)


def sata_signal(connection, config, command, module_name):
    if not connection:
        logging.error("No connection available for _on_SATA")
        return
    lmp_sata_id = get_module_serial(config.lmp_sata_id, module_name, config)
    if not lmp_sata_id:
        logging.error("No lmp_sata_id available for _on_SATA")
        return
    logging.debug("Handling signal <LAVA_SATA %s>" % command)
    if command == "passthru":
        lmp_sata.dutPassthru(lmp_sata_id)
    elif command == "disconnect":
        lmp_sata.dutDisconnect(lmp_sata_id)

    message_str = ""
    connection.sendline("<LAVA_SATA_COMPLETE%s>" % message_str)


def usb_signal(connection, config, command, module_name):
    if not connection:
        logging.error("No connection available for usb_signal")
        return
    lmp_usb_id = get_module_serial(config.lmp_usb_id, module_name, config)
    if not lmp_usb_id:
        logging.error("No lmp_usb_id available for usb_signal")
        return
    logging.debug("Handling signal <LAVA_USB %s>" % command)
    if command == "device":
        lmp_usb.device(lmp_usb_id)
    elif command == "host":
        lmp_usb.host(lmp_usb_id)
    elif command == "disconnect":
        lmp_usb.disconnect(lmp_usb_id)

    message_str = ""
    connection.sendline("<LAVA_USB_COMPLETE%s>" % message_str)
