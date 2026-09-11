from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.user_api_key import UserApiKey
from app.services.api_key_service import ApiKeyService, SUPPORTED_API_KEY_PROVIDERS


def test_user_api_key_is_encrypted_and_can_be_removed():
    engine = create_engine("sqlite://")
    UserApiKey.__table__.create(engine)
    user_id = uuid4()
    secret = "gsk_example-secret-value"

    with Session(engine) as session:
        service = ApiKeyService(session)
        saved = service.upsert(user_id, "groq", secret)
        assert secret not in saved.encrypted_key
        assert saved.key_hint.endswith("alue")
        assert service.decrypted_for_user(user_id) == {"groq": secret}

        service.remove(user_id, "groq")
        assert service.decrypted_for_user(user_id) == {}

    engine.dispose()


def test_all_declared_byok_providers_can_be_saved():
    engine = create_engine("sqlite://")
    UserApiKey.__table__.create(engine)
    user_id = uuid4()

    with Session(engine) as session:
        service = ApiKeyService(session)
        for provider in SUPPORTED_API_KEY_PROVIDERS:
            service.upsert(user_id, provider, f"{provider}-example-key")

        assert set(service.decrypted_for_user(user_id)) == set(SUPPORTED_API_KEY_PROVIDERS)

    engine.dispose()
