import json
import re
from datetime import datetime, timezone

NOW_UTC = datetime.now(timezone.utc)


def parse_username(machine_name: str) -> str:
    """
    Extract the username from the machine name.
    Assumes the name starts with USERNAME- or USERNAME_.
    """
    # Regex: capture up to the first dash or underscore
    match = re.match(r"^([^-_]+)[-_]?.*$", machine_name)
    if match:
        return match.group(1)
    else:
        return machine_name  # Fallback if pattern doesn't match


def compute_hours_since_creation(created_at_str: str) -> float:
    """
    Given a timestamp string for createdAt, compute
    how many hours have passed from that timestamp until 'now' (UTC).
    """
    created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f %z UTC")
    diff = NOW_UTC - created_at
    hours = diff.total_seconds() / 3600.0
    return round(hours, 2)


def main():
    # 1) Load the JSON data
    with open("running_pods_response.json", "r") as f:
        all_machines = json.load(f)

    # 2) Filter machines by desiredStatus = RUNNING
    running_machines = [m for m in all_machines if m.get("desiredStatus") == "RUNNING"]

    # Dictionary to store usage data by user
    usage_by_user = {}

    for machine in running_machines:
        machine_name = machine["name"]
        username = parse_username(machine_name)

        # 3) Compute costSpentPerHour, totalHours, totalCost
        gpu_count = machine.get("gpuCount", 0)
        cost_per_hr = machine.get("costPerHr", 0.0)
        cost_spent_per_hour = gpu_count * cost_per_hr
        cost_spent_per_hour = round(cost_spent_per_hour, 2)

        total_hours = compute_hours_since_creation(machine["createdAt"])
        total_cost = cost_spent_per_hour * total_hours
        total_cost = round(total_cost, 2)
        # 4) Extract disk/volume info
        container_disk_in_gb = machine.get("containerDiskInGb", 0)
        # Some machines may have no "networkVolume" key if not used:
        network_volume_size = machine.get("networkVolume", {}).get("size", 0)
        gpu_type = machine.get("machine", {}).get("gpuTypeId", "Unknown")

        # 5) Build the machine detail record
        machine_details = {
            "name": machine_name,
            "costPerHrPerGPU": cost_per_hr,
            "costPerHour": cost_spent_per_hour,
            "totalHours": total_hours,
            "totalCost": total_cost,
            "gpuType": gpu_type,
            "gpuCount": gpu_count,
            "containerDiskInGb": container_disk_in_gb,
            "networkVolumeSizeInGb": network_volume_size,
        }

        # Initialize the user record if needed
        if username not in usage_by_user:
            usage_by_user[username] = {
                "summary": {
                    "numberOfMachines": 0,
                    "totalGPUs": 0,
                    "totalCost": 0.0,
                    "totalCostPerHour": 0.0,
                    "totalGpuHours": 0.0,
                },
                "machines": [],
            }

        # Add this machine's details
        usage_by_user[username]["machines"].append(machine_details)
        usage_by_user[username]["summary"]["numberOfMachines"] += 1
        usage_by_user[username]["summary"]["totalGPUs"] += gpu_count
        # Update summary
        usage_by_user[username]["summary"]["totalCost"] += total_cost
        usage_by_user[username]["summary"]["totalCostPerHour"] += cost_spent_per_hour
        # totalGpuHours = sum of (gpuCount * totalHours)
        usage_by_user[username]["summary"]["totalGpuHours"] += gpu_count * total_hours

    # 6) Save the result as JSON
    with open("resource_usage_summary.json", "w") as f_out:
        json.dump(usage_by_user, f_out, indent=4)


if __name__ == "__main__":
    main()
