// MIGRATED to fastapi/app/services/supabase_storage_service.py
package io.github.wavesync.service;
import io.github.wavesync.exception.CustomException;
import io.github.wavesync.exception.ErrorCode;
import io.github.wavesync.util.StorageUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;


@Slf4j
@Service
@RequiredArgsConstructor
@Profile("prod")
public class SupabaseStorageService implements ObjectStorageService {

    private final RestClient supabaseRestClient;

    @Value("${supabase.url}")
    private String publicUrl;

    @Value("${supabase.bucket.profiles}")
    private String profileBucket;


    @Override
    public String createUrl(String path) {
        return publicUrl + "/storage/v1/object/public/" + path;
    }

    @Override
    public String uploadProfileImage(MultipartFile file) {
        log.info("SupaBase 스토리지에 접근합니다.");

        StorageUtil.validateImage(file);
        log.debug("이미지 검증을 완료했습니다.");

        String objectName = UUID.randomUUID() + StorageUtil.getExtension(file);

        try {
            supabaseRestClient.post()
                    .uri("/storage/v1/object/" + profileBucket + "/" + objectName)
                    .contentType(MediaType.parseMediaType(file.getContentType()))
                    .header("x-upsert", "true")
                    .body(file.getBytes())
                    .retrieve()
                    .toBodilessEntity();
            log.debug("프로필 이미지를 업로드했습니다.");

        } catch (Exception e) {
            log.error("Image upload failed", e);
            throw new CustomException(ErrorCode.IMAGE_PROCESSING_FAILED);
        }

        return createUrl(profileBucket + "/" + objectName);
    }
}
