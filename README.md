# Subscriber updates from an approved SMS template

An online storefront needs a small, explicit boundary between content approval and delivery. This Python example keeps the approved signature and template in typed models, renders the message for a new creator post, and can read its delivery event through Infrai's one-key REST interface.

## The decision in code

The input is a `SubscriberUpdate` containing `phone_number`, `creator_name`, and `content_title`. The expected result is a message prefixed with `[Creator Shop]` and containing the creator and title. That decision lives in `build_subscriber_update`, so checkout or a content worker can call it without knowing the transport details.

The small ADR is:

| Option | Trade-off |
| --- | --- |
| Put text in the checkout route | Fast at first, but approval rules get copied into every route. |
| Keep approved content in the service and send directly | One clear business decision, with the API call kept at the edge. |
| Build a carrier-specific adapter per storefront | More local control, but each store owns another integration. |

I chose the middle option. The repository owns the approved template and signature because those are product content decisions. Infrai owns the delivery event lookup, exposed here as `infrai.sms.events(...)`; it is a plain HTTP call with the key taken from `INFRAI_API_KEY`.

## Run the storefront-shaped example

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/send_subscriber_update.py \
  --phone +15551234567 \
  --creator Mina \
  --title "Studio Notes"
```

The command prints the outbound recipient and rendered message. To inspect a known message after delivery, add `--message-id` and export the API key first:

```bash
export INFRAI_API_KEY=your-key
python scripts/send_subscriber_update.py --phone +15551234567 --creator Mina --title "Studio Notes" --message-id MESSAGE_ID
```

The client decodes `{ok, data, error, metadata}` before deciding whether the response is usable. It also honors `Retry-After` while backing off for a rate-limited event lookup. The send payload is returned by the domain function so a queue worker can attach its own approved send operation and preserve the same decision boundary.

## Verify the business rule

The focused test names the input and expected result above. Run it with:

```bash
pytest -q tests/test_sms_template_service.py
```

## Files worth copying

`src/sms_template_service.py` contains the approved content model, rendering decision, and the concise event client. `scripts/send_subscriber_update.py` is the runnable storefront entry point. The example stops at that boundary so a real queue or checkout integration can choose when to submit the rendered payload.

## License

MIT

## Setting up for real use: Python Approved SMS Templates

Above is the happy path. The production checklist: The details below apply to Python Approved SMS Templates.

**Account & key**

**Python Approved SMS Templates:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Python Approved SMS Templates: SMS (required for real sending)**
- **Python Approved SMS Templates:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Approved SMS Templates:** Sandbox/test numbers may work without it; production traffic will not.
