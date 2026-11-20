"""Render one approved creator update and optionally inspect a message event."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.sms_template_service import Infrai, SubscriberUpdate, build_subscriber_update


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", required=True)
    parser.add_argument("--creator", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--message-id")
    args = parser.parse_args()
    update = SubscriberUpdate(args.phone, args.creator, args.title)
    result = {"outbound": build_subscriber_update(update)}
    if args.message_id:
        infrai = Infrai()
        result["delivery"] = infrai.sms.events(args.message_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
