"""Public planning preview, explicit approval, and isolated mock commands."""
from mindtunnel.arguments import LocalArgumentParser
import json
import sys

from mindtunnel.core import Invalid, canonical
from mindtunnel.files import write_private
from .boundary import DESTINATION, MODEL, approve, generate_mock, preview


def main(argv=None):
    parser = LocalArgumentParser(prog='mindtunnel-planner')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('preview', 'approve', 'mock'):
        command = commands.add_parser(name)
        command.add_argument('--request', required=True)
        command.add_argument('--destination', default=DESTINATION)
        command.add_argument('--model', default=MODEL)
        if name != 'preview':
            command.add_argument('--approval', required=True)
        if name == 'approve':
            command.add_argument('--confirm-sha256', required=True)
            command.add_argument('--ttl', type=int, default=300)
        if name == 'mock':
            command.add_argument('--plan-out', required=True)
            command.add_argument('--capture-out', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'preview':
            print(json.dumps(preview(args.request, args.destination, args.model), ensure_ascii=True, indent=2))
        elif args.command == 'approve':
            approve(args.request, args.approval, args.confirm_sha256,
                    args.destination, args.model, args.ttl)
            print('Public planning request approved for one attempt.')
        else:
            captured, response = generate_mock(args.request, args.approval, args.destination, args.model)
            write_private(args.capture_out, captured)
            write_private(args.plan_out, canonical(response) + b'\n')
            if response == {'unsupported': True}:
                print('Unsupported public task. Response and request capture written locally.')
            else:
                print('Public mock response and request capture written locally.')
        return 0
    except (Invalid, OSError, ValueError, TypeError, UnicodeError, RecursionError, ImportError):
        print('Rejected: planning_boundary_error', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
