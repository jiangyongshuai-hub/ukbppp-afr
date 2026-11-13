#!/usr/bin/env python3
import json
import os
import sys

import synapseclient

FOLDERS = {
    "afr": "syn51365304",
    "csa": "syn51365305",
    "mid": "syn51365307",
    "amr": "syn51500434",
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

    if ancestry == "amr" and target.lower() == "manifest":
        os.makedirs(OUT_DIR, exist_ok=True)
        tars.sort(key=lambda c: entity_name(c).lower())
        sample_indexes = sorted(set([0, 1, len(tars) // 4, len(tars) // 2,
                                     (3 * len(tars)) // 4, len(tars) - 2, len(tars) - 1]))
        samples = []
        for index in sample_indexes:
            child = tars[index]
            entity = syn.get(entity_id(child), downloadFile=False)
            handle = entity.get("_file_handle", {})
            size = handle.get("contentSize") or entity.get("dataFileSizeBytes")
            samples.append({"id": entity_id(child), "name": entity_name(child), "size": size})
            print("Sample", entity_name(child), size, flush=True)
        manifest = {
            "folder_id": folder_id,
            "count": len(tars),
            "files": [{"id": entity_id(c), "name": entity_name(c)} for c in tars],
            "samples": samples,
        }
        path = os.path.join(OUT_DIR, "amr_manifest.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2)
        print("Manifest written", path, flush=True)
        return

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
