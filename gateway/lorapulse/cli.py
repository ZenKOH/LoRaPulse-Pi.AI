from __future__ import annotations

import argparse
import json

from .airtime_budget import AirTimeBudget, estimate_lora_airtime_seconds, get_region_profile
from .event_router import Event, EventRouter
from .profiles import load_profile


def cmd_airtime(args: argparse.Namespace) -> int:
    seconds = estimate_lora_airtime_seconds(args.payload_bytes, args.spreading_factor, args.bandwidth)
    print(json.dumps({"payload_bytes": args.payload_bytes, "spreading_factor": args.spreading_factor, "airtime_seconds": seconds}, indent=2))
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile)
    router = EventRouter(AirTimeBudget(get_region_profile(profile.region)), max_lora_payload_bytes=profile.max_payload_bytes)
    data = json.loads(args.event)
    event = Event(
        node_id=str(data.get("node_id", data.get("node", "unknown"))),
        kind=str(data.get("kind", "sensor_summary")),
        priority=int(data.get("priority", 1)),
        battery=int(data.get("battery", 100)),
        payload=dict(data.get("payload", {})),
        size_hint_bytes=data.get("size_hint_bytes"),
    )
    decision = router.route(event)
    print(json.dumps({"action": decision.action.value, "reason": decision.reason, "airtime_seconds": decision.airtime_seconds, "packet": decision.packet.to_dict() if decision.packet else None}, indent=2))
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    from simulator.simulate_nodes import simulate
    print(json.dumps(simulate(nodes=args.nodes, events=args.events, region=args.region), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LoRaPulse-Pi.AI gateway toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    airtime = sub.add_parser("airtime", help="Estimate LoRa time-on-air")
    airtime.add_argument("--payload-bytes", type=int, required=True)
    airtime.add_argument("--spreading-factor", type=int, default=9)
    airtime.add_argument("--bandwidth", type=int, default=125000)
    airtime.set_defaults(func=cmd_airtime)
    route = sub.add_parser("route", help="Route one JSON event")
    route.add_argument("--profile", required=True)
    route.add_argument("--event", required=True)
    route.set_defaults(func=cmd_route)
    sim = sub.add_parser("simulate", help="Run a software-only telemetry simulation")
    sim.add_argument("--nodes", type=int, default=4)
    sim.add_argument("--events", type=int, default=40)
    sim.add_argument("--region", default="EU868")
    sim.set_defaults(func=cmd_simulate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
