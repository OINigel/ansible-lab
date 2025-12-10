#!/usr/bin/env python3
import json
import subprocess
import sys

# Slurm controller host we will SSH into
SLURM_CTL_HOST = "rocky-slurmctld"  # uses your default SSH user


def get_slurm_nodes():
    """
    Get node names by SSH'ing into the Slurm controller and running sinfo there.
    """
    try:
        cmd = [
            "ssh",
            SLURM_CTL_HOST,
            "sinfo -Nh -o '%N'",
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().splitlines()
        hosts = sorted(set(h.strip() for h in out if h.strip()))
        return hosts
    except Exception:
        return []


def build_inventory():
    # 1) Dynamic part: nodes from Slurm
    slurm_nodes = get_slurm_nodes()

    inv = {
        "_meta": {"hostvars": {}},
        "all": {
            "children": [
                "slurm_controller",
                "slurm_backup_controller",
                "monitor",
                "compute",
            ]
        },
        # 2) Static hosts that aren't Slurm nodes
        "slurm_controller": {
            "hosts": ["rocky-slurmctld"],
        },
        "slurm_backup_controller": {
            "hosts": ["rocky-slurmctld2"],
        },
        "monitor": {
            "hosts": ["rocky-monitor"],
        },
        # 3) Dynamic compute group from Slurm
        "compute": {
            "hosts": [],
        },
    }

    for name in slurm_nodes:
        # Anything with "compute" in its name is treated as a compute node
        if "compute" in name:
            inv["compute"]["hosts"].append(name)

    return inv


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(build_inventory()))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        print(json.dumps({}))
    else:
        print(json.dumps(build_inventory()))
