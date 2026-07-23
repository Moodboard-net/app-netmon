import argparse

from app.core.security import generate_master_key


def main() -> None:
    parser = argparse.ArgumentParser(prog="netmon")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "generate-key",
        help="Generate master key AES-256 baru untuk CREDENTIAL_ENCRYPTION_KEY",
    )

    args = parser.parse_args()

    if args.command == "generate-key":
        print(generate_master_key())


if __name__ == "__main__":
    main()
