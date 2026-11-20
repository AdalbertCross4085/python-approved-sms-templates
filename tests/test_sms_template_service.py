from src.sms_template_service import SubscriberUpdate, build_subscriber_update


def test_new_content_update_uses_approved_signature_and_values():
    update = SubscriberUpdate("+15551234567", "Mina", "Studio Notes")

    assert build_subscriber_update(update) == {
        "to": "+15551234567",
        "message": "[Creator Shop] Mina published Studio Notes. Open your subscriber page to view it.",
    }

