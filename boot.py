# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

# boot.py: This file started life as the basic boot.py file that comes with
#   Micropython.  I turned it into a utility to initialize an ESP8266
#   microcontroller and get it onto a wireless network set in config.py.
#   It's a quick-and-dirty hack to make a wifi gizmo that does nothing but
#   generate monitorable network traffic for testing Faraday shielding.

# By: The Doctor <drwho at virtadpt dot net>
#       0x807B17C1 / 7960 1CDC 85C9 0B63 8D9F  DD89 3BD8 FF2B 807B 17C1

# License: GPLv3

# v1.0 - Initial release.

# TO-DO:
# -

# Bare minimum to bootstrap the uc.
import gc
import network
import time
import sys
import urequests

# Pull in the configuration file.
import config

# Handle to a wifi configurator.
wifi = None

# Network configuration information.
local_networks = []
ifconfig = None

# Handle to a urequests object.
request = None

# Configure up the wireless interface as a client (it defaults to an access
# point) and associate with the configured network.
print("Searching for configured wireless network.")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
if not wifi.active():
    print("Wifi not online.  Trying again.")
    time.sleep(config.delay)

# This should make sure the wifi nic is awake.
local_networks = wifi.scan()
i = 0
for ap in local_networks:
    local_networks[i] = ap[0]
    i = i + 1
print("Networks found: %s" % local_networks)

if bytes(config.network, "utf-8") not in local_networks:
    print("Configured wireless network %s not found.  Trying again." % config.network)
    time.sleep(config.delay)
    sys.exit(1)

# Connect to the wireless network.
print("Trying to connect to wireless network.")
wifi.connect(config.network, config.password)
time.sleep(config.delay)

# Print the network configuration information.
# This is actually supposed to go to the local display.
if wifi.isconnected():
    ifconfig = wifi.ifconfig()
    print("Successfully connected to wifi network %s!" % config.network)
    print("IP address is: %s" % ifconfig[0])
    time.sleep(config.delay)
else:
    print("Unable to connect to network.")
    time.sleep(config.delay)
    sys.exit(1)

# Clean up.
gc.collect()

# Now that the device is online, pull the URL every couple of seconds.  The
# idea is that we want to make a noticable trace in the web server logs that
# is easy to grep for.
while wifi.active():
    print("Trying to contact target URL...")
    try:
        request = urequests.get(config.target)
        print("Got HTTP %s" % request.status_code)
    except:
        print("Connection attempt failed.")
    print()

    # Nullify the request handle so the garbage collector can handle it.
    request = None
    gc.collect()

    # Nap for a few seconds.
    time.sleep(config.delay)

# If we wound up down here, just reboot the ESP.
print("Rebooting!")
sys.exit(1)
