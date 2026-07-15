package io.github.wavesync.util;

import io.github.wavesync.exception.CustomException;
import io.github.wavesync.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.multipart.MultipartFile;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.IOException;


@Slf4j
public class StorageUtil {

    public static void validateImage(MultipartFile file) {
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


    public static String getExtension(MultipartFile file) {
        String originalFilename = file.getOriginalFilename();

        if (originalFilename == null || !originalFilename.contains(".")) {
            return "";
        }

        return originalFilename.substring(
                originalFilename.lastIndexOf(".")
        );
    }
}
