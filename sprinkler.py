#!/usr/bin/env python3

import logging
import logging.handlers
import re
import sys
import time
from argparse import ArgumentParser
from collections import OrderedDict

import automationhat

ZONE_MAP = OrderedDict([
    ("backyard", automationhat.relay.one),
    ("frontyard", automationhat.relay.two),
    ("aux", automationhat.relay.three),
])


def parse_time(spec):
    regexes = [
        (r'(\d+)s', 1),
        (r'(\d+)secs?', 1),
        (r'(\d+)m', 60),
        (r'(\d+)mins?', 60),
        (r'(\d+)', 1),
    ]
    for regex in regexes:
        match = re.match(regex[0], spec, re.IGNORECASE)
        if match:
            return int(match.group(1)) * regex[1]
    raise ValueError("Unable to parse time {}".format(spec))


def turn_everything_off():
    for relay in ZONE_MAP.values():
        relay.auto_light(False)
        relay.off()
        relay.light_nc.off()
        relay.light_no.off()


def preamble_animation():
    for name, relay in ZONE_MAP.items():
        relay.off()
        relay.auto_light(False)
        relay.light_no.on()
        time.sleep(0.25)
        relay.light_nc.on()
        time.sleep(0.25)
    time.sleep(1)

    for name, relay in ZONE_MAP.items():
        relay.light_no.off()
        relay.light_nc.off()
    time.sleep(0.5)

    for name, relay in ZONE_MAP.items():
        relay.light_no.on()
        relay.light_nc.on()
    time.sleep(0.5)

    for name, relay in ZONE_MAP.items():
        relay.light_no.off()
        relay.light_nc.off()
    time.sleep(0.5)

    for name, relay in ZONE_MAP.items():
        relay.light_no.on()
        relay.light_nc.on()
    time.sleep(0.5)

    turn_everything_off()


def run_zone(zone, seconds):
    end_time = time.time() + seconds
    relay = ZONE_MAP[zone]
    relay.on()

    while time.time() < end_time:
        light_counter = int(time.time())%4
        relay.light_no.write(light_counter >> 1)
        relay.light_nc.write(light_counter & 1)
        time.sleep(0.25)

    turn_everything_off()


def config_logging():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

    system_handler = logging.handlers.RotatingFileHandler("/var/log/sprinkler/sprinkler.log", maxBytes=100*(2**20),
                                                          backupCount=10)
    system_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    system_handler.setFormatter(system_formatter)
    system_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(system_handler)

    logging.getLogger().setLevel(logging.DEBUG)


def main():
    parser = ArgumentParser()
    parser.add_argument("zone", choices=ZONE_MAP.keys())
    parser.add_argument("runtime")
    args = parser.parse_args()

    config_logging()

    run_time = parse_time(args.runtime)
    logging.debug("Parse runtime of %s to %d seconds", args.runtime, run_time)

    turn_everything_off()
    logging.info("Turned off all zones")
    preamble_animation()

    logging.info("Turning on zone %s for %d seconds", args.zone, run_time)
    run_zone(args.zone, run_time)
    logging.info("Turned off all zones")


if __name__ == "__main__":
    exit(main())