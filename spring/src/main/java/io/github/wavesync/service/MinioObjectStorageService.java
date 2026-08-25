// MIGRATED to fastapi/app/services/minio_object_storage_service.py
package io.github.wavesync.service;
import io.github.wavesync.exception.CustomException;
import io.github.wavesync.exception.ErrorCode;
import io.github.wavesync.util.StorageUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.multipart.MultipartFile;
import java.util.UUID;



@Slf4j
@Service
@RequiredArgsConstructor
@Profile("dev")
public class MinioObjectStorageService implements ObjectStorageService {

    private final MinioClient minioClient;

    @Value("${MINIO_ENDPOINT}")
    private String endpoint;

    @Value("${MINIO_PUBLIC_URL}")
    private String publicUrl;

    @Value("${MINIO_BUCKET_PROFILES}")
    private String profileBucket;


    @Override
    public String createUrl(String path) {
        return publicUrl + "/" + path;
    }

    @Override
    public String uploadProfileImage(MultipartFile file) {
        log.info("MinIO 스토리지에 접근합니다.");

        StorageUtil.validateImage(file);
        log.debug("이미지 검증을 완료했습니다.");

        String objectName = UUID.randomUUID() + StorageUtil.getExtension(file);

        try {
            minioClient.putObject(PutObjectArgs.builder()
                            .bucket(profileBucket)
                            .object(objectName)
                            .stream(file.getInputStream(), file.getSize(), -1)
                            .contentType(file.getContentType())
                            .build()
            );
            log.debug("프로필 이미지를 업로드했습니다.");

        } catch (Exception e) {
            log.error("Image upload failed", e);
            throw new CustomException(ErrorCode.IMAGE_PROCESSING_FAILED);
        }

        return endpoint+ "/" + profileBucket + "/" + objectName;
    }
}
