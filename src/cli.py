#!/usr/bin/env python3
"""
Command-line interface for SGFF tools
"""

import sys
import json
import argparse
from pathlib import Path

from .reader import SgffReader
from .writer import SgffWriter
from .internal import SgffObject


def cmd_parse(args):
    """Parse SGFF file to JSON"""
    sgff = SgffReader.from_file(args.input)

    output = {
        "cookie": {
            "type_of_sequence": sgff.cookie.type_of_sequence,
            "export_version": sgff.cookie.export_version,
            "import_version": sgff.cookie.import_version,
        },
        "blocks": sgff.blocks,
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))


def cmd_info(args):
    """Show file information"""
    sgff = SgffReader.from_file(args.input)

    print(f"SnapGene File: {args.input}")
    print(f"Export version: {sgff.cookie.export_version}")
    print(f"Import version: {sgff.cookie.import_version}")
    print(f"\nBlocks:")

    block_types = {}
    for key in sgff.blocks.keys():
        block_type = key.split(".")[0]
        block_types[block_type] = block_types.get(block_type, 0) + 1

    for block_type in sorted(block_types.keys(), key=int):
        count = block_types[block_type]
        print(f"  Type {block_type:>2}: {count} block(s)")


def cmd_filter(args):
    """Filter blocks and write new file"""
    sgff = SgffReader.from_file(args.input)

    # Parse keep list
    keep_types = [int(t.strip()) for t in args.keep.split(",")]

    # Filter blocks
    filtered = SgffObject(cookie=sgff.cookie)
    for key, value in sgff.blocks.items():
        block_type = int(key.split(".")[0])
        if block_type in keep_types:
            filtered.blocks[key] = value

    # Write output
    SgffWriter.to_file(filtered, args.output)
    print(f"Filtered file written to {args.output}")


def main():
    parser = argparse.ArgumentParser(description="SnapGene File Format tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse SGFF to JSON")
    parse_parser.add_argument("input", help="Input SGFF file")
    parse_parser.add_argument(
        "-o", "--output", help="Output JSON file (default: stdout)"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show file information")
    info_parser.add_argument("input", help="Input SGFF file")

    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter blocks")
    filter_parser.add_argument("input", help="Input SGFF file")
    filter_parser.add_argument(
        "-k", "--keep", required=True, help="Block types to keep (comma-separated)"
    )
    filter_parser.add_argument("-o", "--output", required=True, help="Output SGFF file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "parse":
        cmd_parse(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "filter":
        cmd_filter(args)


if __name__ == "__main__":
    main()
