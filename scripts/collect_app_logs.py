"""Collect only allowlisted structured application events; never forward arbitrary pod text."""

import collections
import json
import subprocess
import time
from pathlib import Path

DESTINATION = Path("/var/log/secure-delivery/application.jsonl")


def main():
    seen = collections.OrderedDict()
    while True:
        result = subprocess.run(  # noqa: S603
            [
                "/usr/local/bin/k3s",
                "kubectl",
                "-n",
                "secure-delivery",
                "logs",
                "-l",
                "app=release-inventory",
                "--all-containers=false",
                "--since=45s",
                "--tail=500",
            ],
            capture_output=True,
            text=True,
            timeout=25,
        )
        events = []
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("event") != "http_request" or event.get("request_id") in seen:
                    continue
                if event.get("route", "").startswith("/health/") and event.get("status") == 200:
                    continue
                seen[event["request_id"]] = True
                fields = ["event", "request_id", "method", "route", "status"]
                selected = {key: event[key] for key in fields if key in event}
                selected["service"] = "secure-delivery"
                selected["http_status"] = selected.pop("status", None)
                events.append(json.dumps(selected))
            while len(seen) > 10000:
                seen.popitem(last=False)
        if events:
            with DESTINATION.open("a", encoding="utf-8") as output:
                output.write("\n".join(events) + "\n")
        time.sleep(15)


if __name__ == "__main__":
    main()
