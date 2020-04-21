"""
A helper for talking to the NetBox API.
"""

import json


def get_prefix(prefix: str, session, fqdn) -> dict:
    """Get a prefix object from the API."""

    url = "{}/ipam/prefixes/?prefix={}".format(
        f"http://{ fqdn }/api", prefix.replace("/", "%2F")
    )
    result = session.get(url)

    return result.json()["results"][0]


def delete_prefix(prefix: dict, session, fqdn) -> int:
    """Call API to delete the prefix."""

    id = prefix["id"]
    result = session.delete(f"http://{ fqdn }/api/ipam/prefixes/{ id }/")

    return result


def carve_new_prefix(parent_prefix: str, prefix_length: int, session, fqdn) -> dict:
    """Call API to create a new prefix object from parent prefix object."""

    data = {
        "prefix_length": prefix_length,
        "description": "test_netbox created this prefix",
    }
    id = get_prefix(parent_prefix, session, fqdn)["id"]
    result = session.post(
        f"http://{ fqdn }/api/ipam/prefixes/{ id }/available-prefixes/",
        data=json.dumps(data),
    )

    return result.json()


def get_and_reserve_next_free_address(prefix: dict, session, fqdn) -> dict:
    """Call API to allocate a new address from prefix."""

    data = {"description": "test_netbox allocated this address"}
    id = prefix["id"]
    result = session.post(
        f"http://{ fqdn }/api/ipam/prefixes/{ id }/available-ips/",
        data=json.dumps(data),
    )

    if result.status_code == 204:
        raise RuntimeError

    return result.json()


def deallocate_address(address: dict, session, fqdn) -> bool:
    """Remove assignment data from an address."""

    id = address["id"]
    response = session.delete(f"http://{ fqdn }/api/ipam/ip-addresses/{ id }/")

    return True if response.status_code == 204 else False


def reserve_address(
    address: str, session, fqdn, description="allocated as part of a test"
) -> dict:
    """Assign data to fields of an address to claim it."""

    data = {"address": address, "description": description}
    response = session.post(
        f"http://{ fqdn }/api/ipam/ip-addresses/", data=json.dumps(data)
    )

    return response.json()
