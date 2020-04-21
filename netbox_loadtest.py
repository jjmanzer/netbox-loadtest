#!/usr/bin/env python3

"""
Test the netbox API by running a set of scenarios at it designed to show how netbox responds to heavy load.

1. Allocate addresses using get next free logic, then deallocate those addresses.
2. Randomly grab addresses, then deallocate them in that order.
3. Use get next free address logic in a heavily fragmented prefix, then deallocate only those addresses.

After running each of these 3 tests, results are combined and a more general report is generated.
"""

import argparse
import ipaddress
import queue
import random
import threading
import time

import requests
from openpyxl import Workbook

from helpers import netbox
from helpers.excel import add_worker_data_to_sheet

parser = argparse.ArgumentParser(description="Test the Netbox API.")
parser.add_argument(
    "parent_prefix",
    type=str,
    help="the prefix the worker should pull the child prefix from",
)
parser.add_argument(
    "prefix_length", type=int, help="the size of the prefix to carve out"
)
parser.add_argument("workers", type=int, help="number of workers concurrenting working")
parser.add_argument("fqdn", type=str, help="FQDN of netbox")
parser.add_argument("token", type=str, help="Auth token for netbox API")
args = parser.parse_args()

report_queue = queue.Queue()
session = requests.Session()
session.headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Token { args.token }",
}


def test_get_next_free_address(prefix: dict) -> dict:
    """Use the get next free logic to allocate every address in prefix then deallocate."""

    report = {
        "prefix": prefix["prefix"],
        "allocate": {"data": {}},
        "deallocate": {"data": {}},
    }
    addresses_assigned = []

    while True:
        try:
            start = time.time()
            address = netbox.get_and_reserve_next_free_address(
                prefix, session, args.fqdn
            )
            _address = address["address"].split("/", 1)[0]
            report["allocate"]["data"][_address] = time.time() - start
            addresses_assigned.append(address)
        except RuntimeError:
            break

    for address in addresses_assigned:
        _address = address["address"].split("/", 1)[0]
        start = time.time()
        if netbox.deallocate_address(address, session, args.fqdn):
            report["deallocate"]["data"][_address] = time.time() - start

    return report


def test_get_next_free_address_fragmented(prefix: dict) -> dict:
    """Use the get next free logic to allocate every other address in prefix then deallocate them."""

    report = {
        "prefix": prefix["prefix"],
        "allocate": {"data": {}},
        "deallocate": {"data": {}},
    }
    addresses_assigned = []
    prefix_obj = ipaddress.IPv4Network(prefix["prefix"])
    fragmentated_addresses = []

    # create the fragmentation
    for address_obj in prefix_obj.hosts():
        if int(address_obj) % 2:
            address = netbox.reserve_address(
                str(address_obj), session, args.fqdn, "fragmentation for a test"
            )
            fragmentated_addresses.append((address_obj, address))

    while True:
        try:
            start = time.time()
            address = netbox.get_and_reserve_next_free_address(
                prefix, session, args.fqdn
            )
            _address = address["address"].split("/", 1)[0]
            report["allocate"]["data"][_address] = time.time() - start
            addresses_assigned.append(address)
        except RuntimeError:
            break

    for address in addresses_assigned:
        _address = address["address"].split("/", 1)[0]
        start = time.time()
        netbox.deallocate_address(address, session, args.fqdn)
        report["deallocate"]["data"][_address] = time.time() - start

    # clean up fragmentation
    for address_obj, address in fragmentated_addresses:
        if int(address_obj) % 2:
            netbox.deallocate_address(address, session, args.fqdn)

    return report


def test_scattered_assignments(prefix: dict) -> dict:
    """Execute a non-linear pattern of allocating addresses and then deallocating them."""

    addresses_to_unassign = []
    report = {
        "prefix": prefix["prefix"],
        "allocate": {"data": {}},
        "deallocate": {"data": {}},
    }

    addresses_to_assign = [
        str(address) for address in ipaddress.ip_network(prefix["prefix"]).hosts()
    ]
    random.shuffle(addresses_to_assign)

    for address in addresses_to_assign:
        start = time.time()
        _address = netbox.reserve_address(address, session, args.fqdn)
        if _address:
            addresses_to_unassign.append(_address)
            report["allocate"]["data"][address] = time.time() - start

    for address in addresses_to_unassign:
        start = time.time()
        _address = address["address"].split("/", 1)[0]
        if netbox.deallocate_address(address, session, args.fqdn):
            report["deallocate"]["data"][_address] = time.time() - start

    return report


def worker(prefix: dict):
    """Execute all 3 scenarios against prefix then save the report."""

    print("    testing with {}".format(prefix["prefix"]))
    report = {}
    start = time.time()

    report["test_get_next_free_address"] = test_get_next_free_address(prefix)
    report[
        "test_get_next_free_address_fragmented"
    ] = test_get_next_free_address_fragmented(prefix)
    report["test_scattered_assignments"] = test_scattered_assignments(prefix)

    report["total_duration"] = time.time() - start

    report_queue.put(report)
    print("    finished with {}".format(prefix["prefix"]))


def start():
    """ Spawn some worker threads and load test the NetBox API and then make an excel spreadsheet about it."""
    workbook = Workbook()
    worker_data = {}

    for worker_max in range(1, args.workers + 1):
        threads = []
        print(f"starting the { worker_max } worker scenario")

        for worker_id in range(1, worker_max + 1):
            prefix = netbox.carve_new_prefix(
                args.parent_prefix, args.prefix_length, session, args.fqdn
            )
            _prefix = prefix["prefix"]
            print(
                f"  starting worker thread { worker_id } of { worker_max } with { _prefix }"
            )
            thread = threading.Thread(target=worker, args=(prefix,))
            thread.start()
            threads.append((thread, prefix))
        for thread, prefix in threads:
            thread.join()
            netbox.delete_prefix(prefix, session, args.fqdn)
            worker_data[prefix["prefix"]] = report_queue.get()

        sheet = workbook.create_sheet(f"{ worker_max } workers")
        add_worker_data_to_sheet(worker_data, sheet)

    workbook.save(
        filename="netbox_load_test_report_{}.xlsx".format(
            args.parent_prefix.replace("/", "_")
        )
    )
