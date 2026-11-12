#!/usr/bin/env python3
import os
import sys

import synapseclient

FOLDERS = {
    "afr": "syn51365304",
    "csa": "syn51365305",
    "mid": "syn51365307",
}


def entity_id(entity):
    return entity["id"] if isinstance(entity, dict) else entity.id


def entity_name(entity):
    return entity["name"] if isinstance(entity, dict) else entity.name


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python download_exact.py <afr|csa|mid> <exact-file-name>")

    ancestry = sys.argv[1].strip().lower()
    target = sys.argv[2].strip().lower()
    if ancestry not in FOLDERS:
        raise SystemExit("Unknown ancestry: " + ancestry)

    token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if not token:
        raise SystemExit("SYNAPSE_AUTH_TOKEN is not set")

    folder_id = FOLDERS[ancestry]
    syn = synapseclient.Synapse()
    syn.login(authToken=token)

    print("Listing", ancestry, folder_id, flush=True)
    children = list(syn.getChildren(folder_id, includeTypes=["file"]))
    matches = [c for c in children if entity_name(c).lower() == target]
    if len(matches) != 1:
        raise SystemExit(
            "Expected exactly one match for %s in %s, found %d"
            % (target, folder_id, len(matches))
        )

    chosen = matches[0]
    os.makedirs("output", exist_ok=True)
    print("Downloading", entity_name(chosen), entity_id(chosen), flush=True)
    result = syn.get(entity_id(chosen), downloadLocation="output")
    size_mb = os.path.getsize(result.path) / 1e6
    print("Downloaded %s (%.1f MB)" % (result.path, size_mb), flush=True)


if __name__ == "__main__":
    main()
