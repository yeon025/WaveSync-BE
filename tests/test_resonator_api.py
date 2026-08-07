import json
import pytest
from unittest.mock import Mock
from app.schemas.response import Echo, Stat


def make_dummy_response(image_bytes):
    # simple dummy response object for requests.get
    class Resp:
        def __init__(self, status_code, content):
            self.status_code = status_code
            self.content = content

    return Resp(200, image_bytes)


def test_api_success(client, override_db, dummy_db, sample_image_bytes, monkeypatch):
    # mock external calls to avoid network/filesystem
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    # preprocess no-ops
    monkeypatch.setattr("app.services.preprocess_service.crop_circles", lambda img: None)
    monkeypatch.setattr("app.services.preprocess_service.crop_and_stack", lambda img: None)
    # chain calculation
    monkeypatch.setattr("app.services.resonance_chain_service.calculate_chain_level", lambda a, b: 2)
    # ocr pipeline
    monkeypatch.setattr("app.services.ocr_service.extract_text", lambda path: Mock())
    monkeypatch.setattr("app.services.ocr_service.process_ocr_result", lambda resp: ["ResonatorX", "WeaponY", "Attack 10%", "Secondary 5"])
    monkeypatch.setattr("app.services.ocr_service.clean_text", lambda merged: ["ResonatorX", "WeaponY"])
    # EchoMapper.run -> return one echo
    def fake_run(self, cleaned_texts):
        e = Echo(main=Stat(type="Attack", value=10), secondary=Stat(type="Secondary", value=5), subs=[])
        return [e]

    monkeypatch.setattr("app.mapper.echo.EchoMapper.run", fake_run)
    # validators no-op
    monkeypatch.setattr("app.validators.resonator_validator.validate_resonator", lambda name, db: None)
    monkeypatch.setattr("app.validators.weapon_validator.validate_weapon", lambda name, db: name)
    monkeypatch.setattr("app.validators.echo_sub_validator.validate_sub", lambda echo_list: None)

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == "OK"
    assert body["data"]["resonatorName"] == "ResonatorX"
    assert body["data"]["weaponName"] == "WeaponY"
    assert body["data"]["resonanceChainLevel"] == 2
    assert isinstance(body["data"]["echoes"], list)


def test_api_invalid_input_422(client):
    # missing imageUrl
    resp = client.post("/api/resonators/images", json={})
    assert resp.status_code == 422


def test_api_image_not_found_404(client, override_db, sample_image_bytes, monkeypatch):
    # mock 404 response
    class Resp:
        def __init__(self):
            self.status_code = 404
            self.content = b""

    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: Resp())

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/missing.png"})
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == "IMAGE_NOT_FOUND"


def test_api_image_access_denied_403(client, override_db, sample_image_bytes, monkeypatch):
    class Resp:
        def __init__(self):
            self.status_code = 403
            self.content = b""

    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: Resp())

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/denied.png"})
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == "IMAGE_ACCESS_DENIED"


def test_api_image_load_failed_400(client, override_db, sample_image_bytes, monkeypatch):
    class Resp:
        def __init__(self):
            self.status_code = 500
            self.content = b""

    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: Resp())

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/error.png"})
    assert resp.status_code == 400
    body = resp.json()
    assert "이미지를 불러올 수 없습니다" in body["message"] or body["code"] is None


def test_api_ocr_failure_500(client, override_db, sample_image_bytes, monkeypatch):
    # mock successful GET
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    # make extract_text raise to simulate vision failure
    monkeypatch.setattr("app.services.ocr_service.extract_text", lambda path: (_ for _ in ()).throw(Exception("vision auth fail")))

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})
    assert resp.status_code == 500


def test_api_empty_ocr_results_500(client, override_db, sample_image_bytes, monkeypatch):
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    monkeypatch.setattr("app.services.preprocess_service.crop_circles", lambda img: None)
    monkeypatch.setattr("app.services.preprocess_service.crop_and_stack", lambda img: None)
    monkeypatch.setattr("app.services.resonance_chain_service.calculate_chain_level", lambda a, b: 0)

    monkeypatch.setattr("app.services.ocr_service.extract_text", lambda path: Mock())
    # process_ocr_result returns empty -> clean_text will fail (indexing)
    monkeypatch.setattr("app.services.ocr_service.process_ocr_result", lambda resp: [])
    monkeypatch.setattr("app.services.ocr_service.clean_text", lambda merged: [])

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})
    # should result in 500 due to unexpected index error
    assert resp.status_code == 500


def test_api_storage_failure_500(client, override_db, sample_image_bytes, monkeypatch):
    # simulate crop_and_stack encountering an OSError when trying to save merged image
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    monkeypatch.setattr("app.services.preprocess_service.crop_circles", lambda img: None)

    def fail_crop_and_stack(img):
        raise OSError("disk full")

    monkeypatch.setattr("app.services.preprocess_service.crop_and_stack", fail_crop_and_stack)

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})
    assert resp.status_code == 500


def test_api_db_validation_failed_422(client, override_db, sample_image_bytes, monkeypatch):
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    monkeypatch.setattr("app.services.preprocess_service.crop_circles", lambda img: None)
    monkeypatch.setattr("app.services.preprocess_service.crop_and_stack", lambda img: None)
    monkeypatch.setattr("app.services.resonance_chain_service.calculate_chain_level", lambda a, b: 1)
    monkeypatch.setattr("app.services.ocr_service.extract_text", lambda path: Mock())
    monkeypatch.setattr("app.services.ocr_service.process_ocr_result", lambda resp: ["BadName", "WeaponY", "..."])
    monkeypatch.setattr("app.services.ocr_service.clean_text", lambda merged: ["BadName", "WeaponY"])

    # make validate_resonator raise CustomException -> handled as 422
    from app.exceptions.error_code import ErrorCode
    from app.exceptions.custom_exception import CustomException

    def raise_validation(name, db):
        raise CustomException(ErrorCode.VALIDATION_FAILED)

    monkeypatch.setattr("app.validators.resonator_validator.validate_resonator", raise_validation)

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "VALIDATION_FAILED"


def test_api_db_failure_500(client, sample_image_bytes, app, monkeypatch):
    # override DB dependency to raise exception when created
    from app.database.deps import get_db

    def broken_get_db():
        raise Exception("db down")

    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = broken_get_db

    # successful image fetch
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})

    # cleanup
    app.dependency_overrides.clear()

    assert resp.status_code == 500


def test_service_unexpected_exception_500(client, override_db, sample_image_bytes, monkeypatch):
    # simulate EchoMapper.run raising unexpected exception
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    monkeypatch.setattr("app.services.preprocess_service.crop_circles", lambda img: None)
    monkeypatch.setattr("app.services.preprocess_service.crop_and_stack", lambda img: None)
    monkeypatch.setattr("app.services.resonance_chain_service.calculate_chain_level", lambda a, b: 1)
    monkeypatch.setattr("app.services.ocr_service.extract_text", lambda path: Mock())
    monkeypatch.setattr("app.services.ocr_service.process_ocr_result", lambda resp: ["ResonatorX", "WeaponY", "Attack 1%"])
    monkeypatch.setattr("app.services.ocr_service.clean_text", lambda merged: ["ResonatorX", "WeaponY"])

    def raise_from_run(self, cleaned_texts):
        raise RuntimeError("mapper bug")

    monkeypatch.setattr("app.mapper.echo.EchoMapper.run", raise_from_run)

    resp = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/image.png"})
    assert resp.status_code == 500


def test_boundary_chain_level_values(client, override_db, sample_image_bytes, monkeypatch):
    # Verify chain level 0 and large values propagate correctly
    monkeypatch.setattr("app.services.resonator_profile_service.requests.get", lambda url, timeout=10: make_dummy_response(sample_image_bytes))
    monkeypatch.setattr("app.services.preprocess_service.crop_circles", lambda img: None)
    monkeypatch.setattr("app.services.preprocess_service.crop_and_stack", lambda img: None)
    monkeypatch.setattr("app.services.ocr_service.extract_text", lambda path: Mock())
    monkeypatch.setattr("app.services.ocr_service.process_ocr_result", lambda resp: ["ResonatorX", "WeaponY", "Attack 1%"])
    monkeypatch.setattr("app.services.ocr_service.clean_text", lambda merged: ["ResonatorX", "WeaponY"])
    monkeypatch.setattr("app.validators.resonator_validator.validate_resonator", lambda name, db: None)
    monkeypatch.setattr("app.validators.weapon_validator.validate_weapon", lambda name, db: name)
    monkeypatch.setattr("app.validators.echo_sub_validator.validate_sub", lambda echo_list: None)
    monkeypatch.setattr("app.mapper.echo.EchoMapper.run", lambda self, ct: [Echo(main=Stat(type='A', value=1), secondary=Stat(type='B', value=2), subs=[])])

    # chain level 0
    monkeypatch.setattr("app.services.resonance_chain_service.calculate_chain_level", lambda a, b: 0)
    resp0 = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/0.png"})
    assert resp0.status_code == 200
    assert resp0.json()["data"]["resonanceChainLevel"] == 0

    # chain level large
    monkeypatch.setattr("app.services.resonance_chain_service.calculate_chain_level", lambda a, b: 10)
    resp1 = client.post("/api/resonators/images", json={"imageUrl": "http://example.com/10.png"})
    assert resp1.status_code == 200
    assert resp1.json()["data"]["resonanceChainLevel"] == 10
