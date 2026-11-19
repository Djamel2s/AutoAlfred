"""Run the simulated robot: python -m robot_stub --profile ainex --port 8100"""

import argparse

from .server import build_server


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoAlfred — robot MCP simulé")
    parser.add_argument("--profile", default="ainex", help="tonypi | ainex")
    parser.add_argument("--scenario", default="ranger")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8100)
    args = parser.parse_args()

    server = build_server(args.profile, args.scenario, args.seed)
    print(f"Robot simulé '{args.profile}' sur http://{args.host}:{args.port}/mcp")
    server.run("streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
