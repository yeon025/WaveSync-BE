package io.github.wavesync.service;
import org.springframework.web.multipart.MultipartFile;



public interface ObjectStorageService {

    String uploadProfileImage(MultipartFile file);

    String createUrl(String path);
}
