// MIGRATED to fastapi/app/services/object_storage_service.py
package io.github.wavesync.service;
import org.springframework.web.multipart.MultipartFile;



public interface ObjectStorageService {

    String uploadProfileImage(MultipartFile file);

    String createUrl(String path);
}
