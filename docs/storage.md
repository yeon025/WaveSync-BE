# 이미지 저장 방식

데이터 종류마다 저장 방식이 다릅니다.

- **무기 이미지**: Encore API가 제공하는 절대 URL을 그대로 `weapon_master.image`에 저장합니다. 별도 다운로드나 MinIO 저장을 하지 않습니다.
- **캐릭터 아이콘**: Encore API가 제공하는 절대 URL을 그대로 `resonator_master.thumbnail_image`에 저장합니다.
- **캐릭터 전신 이미지**: 나무위키 크롤링(`app/admin/namuwiki_client.py`)으로 얻은 절대 URL을 `resonator_master.standing_image`에 저장합니다.
- **프로필 이미지**: 공명자 등록 플로우(`resonator_registration_service.py`)가 업로드된 이미지를 `storage_validator.validate_image()`로 메모리에서 검증·OCR 처리만 하고 스토리지에는 저장하지 않습니다. 그래서 `ObjectStorageService`에는 프로필 업로드용 메서드가 없습니다.
- **에코 이미지**: `storage.echo_bucket`에 실제로 저장된 아이콘 파일을 에코 매칭(`profile_extraction/echo/echo_matching_service.py`)이 ORB 특징으로 읽어 비교합니다. `POST /api/admin/master-data/sync`(`targets: ["echoes"]`)가 Encore API 아이콘을 내려받아 이 버킷을 채웁니다.

스토리지는 `ObjectStorageService` 인터페이스 뒤에 숨어 있으며, `APP_ENV`(dev=MinIO, prod=Supabase)에 따라 factory가 구현체를 고릅니다. 서비스 로직은 어떤 스토리지인지 몰라야 합니다.
