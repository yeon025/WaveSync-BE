package io.github.wavesync.service;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;


@Service
@RequiredArgsConstructor
public class ObjectStorageService {

    private final MinioClient minioClient;

    @Value("${MINIO_BUCKET_PROFILES}")
    private String profileBucket;

    @Value("${MINIO_BUCKET_ECHOES}")
    private String echoBucket;

    @Value("${MINIO_BUCKET_WEAPONS}")
    private String weaponBucket;

    @Value("${MINIO_BUCKET_RESONATOR_THUMBNAILS}")
    private String resonatorThumbnailBucket;

    @Value("${MINIO_BUCKET_RESONATOR_STANDINGS}")
    private String resonatorStandingBucket;

    public String uploadProfileImage(MultipartFile file) {
        return upload(file, profileBucket);
    }


    private String upload(MultipartFile file, String bucketName) {
        try {
            validateImage(file);

            String objectName = UUID.randomUUID() + getExtension(file);

            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucketName)
                            .object(objectName)
                            .stream(
                                    file.getInputStream(),
                                    file.getSize(),
                                    -1
                            )
                            .contentType(file.getContentType())
                            .build()
            );

            return bucketName + "/" + objectName;

        } catch (Exception e) {
            throw new RuntimeException("이미지 업로드 실패", e);
        }
    }

    private void validateImage(MultipartFile file) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("빈 파일입니다.");
        }

        String contentType = file.getContentType();

        if (contentType == null || !contentType.startsWith("image/")) {
            throw new IllegalArgumentException("이미지 파일만 업로드 가능합니다.");
        }
    }

    private String getExtension(MultipartFile file) {
        String originalFilename = file.getOriginalFilename();

        if (originalFilename == null || !originalFilename.contains(".")) {
            return "";
        }

        return originalFilename.substring(
                originalFilename.lastIndexOf(".")
        );
    }
}
