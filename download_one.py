#!/usr/bin/env python3
import os
import sys

import synapseclient

FOLDERS = {
    "afr": "syn51365304",
    "csa": "syn51365305",
    "mid": "syn51365307",
}
OUT_DIR = "output"


def entity_id(entity):
    return entity["id"] if isinstance(entity, dict) else entity.id


def entity_name(entity):
    return entity["name"] if isinstance(entity, dict) else entity.name


def main():
    token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if not token:
        raise SystemExit("SYNAPSE_AUTH_TOKEN is not set")

    raw = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    ancestry = "afr"
    target = raw
    for prefix in FOLDERS:
        marker = prefix + "_"
        if raw.lower().startswith(marker):
            ancestry = prefix
            target = raw[len(marker):]
            break

    folder_id = FOLDERS[ancestry]
    syn = synapseclient.Synapse()
    syn.login(authToken=token)

    print("Listing", ancestry, folder_id, flush=True)
    children = list(syn.getChildren(folder_id, includeTypes=["file"]))
    tars = [c for c in children if entity_name(c).lower().endswith(".tar")]
    print("Found", len(tars), "tar files", flush=True)

    if target.lower().endswith(".tar"):
        matches = [c for c in tars if entity_name(c).lower() == target.lower()]
        if len(matches) != 1:
            raise SystemExit("Exact file match count for %s: %d" % (target, len(matches)))
        chosen = matches[0]
    elif target:
        matches = [c for c in tars if entity_name(c).upper().startswith(target.upper() + "_")]
        if not matches:
            raise SystemExit("Protein not found: " + target)
        chosen = matches[0]
    else:
        chosen = tars[0]

    os.makedirs(OUT_DIR, exist_ok=True)
    print("Downloading", entity_name(chosen), entity_id(chosen), flush=True)
    result = syn.get(entity_id(chosen), downloadLocation=OUT_DIR)
    print("Downloaded %s (%.1f MB)" % (result.path, os.path.getsize(result.path) / 1e6), flush=True)


if __name__ == "__main__":
    main()
