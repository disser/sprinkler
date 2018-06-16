import logging
import re
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
    preamble_animation()
    end_time = time.time() + seconds
    relay = ZONE_MAP[zone]
    relay.on()

    while time.time() < end_time:
        relay.light_no.on()
        time.sleep(0.25)
        relay.light_nc.on()
        time.sleep(0.25)
        relay.light_no.off()
        time.sleep(0.25)
        relay.light_nc.off()
        
    turn_everything_off()


def main():
    parser = ArgumentParser()
    parser.add_argument("zone", choices=ZONE_MAP.keys())
    parser.add_argument("runtime")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    run_time = parse_time(args.runtime)
    logging.debug("Parse runtime of %s to %d seconds", args.runtime, run_time)
    logging.info("Turning on zone %s for %d seconds", args.zone, run_time)

    turn_everything_off()
    run_zone(args.zone, run_time)

if __name__ == "__main__":
    exit(main())