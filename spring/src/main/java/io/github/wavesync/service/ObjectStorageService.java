package io.github.wavesync.service;
import io.github.wavesync.exception.CustomException;
import io.github.wavesync.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.multipart.MultipartFile;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.UUID;



@Slf4j
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
            log.debug("이미지 검증을 완료했습니다.");

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

            log.debug("이미지 업로드를 완료했습니다.");

            return bucketName + "/" + objectName;

        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            log.error("Image upload failed", e);
            throw new CustomException(ErrorCode.IMAGE_PROCESSING_FAILED);
        }
    }

    private void validateImage(MultipartFile file) {
        // 빈 이미지인지 확인
        if (file.isEmpty()) {
            throw new CustomException(ErrorCode.IMAGE_REQUIRED);
        }

        String contentType = file.getContentType();

        // 이미지 파일인지 확인
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new CustomException(ErrorCode.INVALID_IMAGE_FILE);
        }

        // 1920×1080인지 해상도 검증
        try {
            BufferedImage image = ImageIO.read(file.getInputStream());

            if (image.getWidth() != 1920 || image.getHeight() != 1080) {
                throw new CustomException(ErrorCode.INVALID_IMAGE_RESOLUTION);
            }
        } catch (IOException e) {
            log.error(e.getMessage());
            throw new CustomException(ErrorCode.IMAGE_PROCESSING_FAILED);
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
