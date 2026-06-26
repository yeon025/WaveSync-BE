package io.github.wavesync.controller;
import org.springframework.http.*;
import io.github.wavesync.dto.request.*;
import io.github.wavesync.dto.response.*;
import org.springframework.web.bind.annotation.*;
import lombok.RequiredArgsConstructor;
import io.github.wavesync.service.ResonatorService;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;


@RestController
@RequiredArgsConstructor
@RequestMapping("/api/resonators")
public class ResonatorController {

    private final ResonatorService resonatorService;

    @PostMapping("")
    public ResponseEntity<ApiResponseDto<CreateResonatorResponseDto>> createResonator(
            @RequestParam("resonatorProfile") MultipartFile resonatorProfile
    ) {
        CreateResonatorResponseDto response = resonatorService.createResonator(resonatorProfile);

        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponseDto.of("OK", "공명자가 등록되었습니다.", response));
    }


    @GetMapping("")
    public ResponseEntity<ApiResponseDto<List<ResonatorSummaryResponseDto>>> getResonatorSummary() {

        List<ResonatorSummaryResponseDto> response = resonatorService.getResonatorSummary();

        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponseDto.of("OK", "전체 공명자 목록을 조회했습니다.", response));
    }


    @GetMapping("/{userResonatorId}")
    public ResponseEntity<ApiResponseDto<ResonatorDetailResponseDto>> getResonatorDetail(
            @PathVariable Long userResonatorId
    ) {
        ResonatorDetailResponseDto response = resonatorService.getResonatorDetail(userResonatorId);

        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponseDto.of("OK", "공명자를 조회했습니다.", response));
    }


    @GetMapping("/{userResonatorId}/setting")
    public ResponseEntity<ApiResponseDto<ResonatorSettingResponseDto>> getResonatorSetting(
            @PathVariable Long userResonatorId
    ) {
        ResonatorSettingResponseDto response = resonatorService.getResonatorSetting(userResonatorId);

        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponseDto.of("OK", "설정 정보를 조회했습니다.", response));
    }


    @PutMapping("/{userResonatorId}/setting")
    public ResponseEntity<ApiResponseDto<Void>> updateResonator(
            @PathVariable Long userResonatorId,
            @RequestBody UpdateResonatorRequestDto data
    ) {
        resonatorService.updateResonator(userResonatorId, data);

        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponseDto.of("OK", "공명자 정보가 수정되었습니다."));
    }


    @DeleteMapping("")
    public ResponseEntity<ApiResponseDto<Void>> deleteResonator(
            @RequestBody DeleteResonatorRequestDto data
    ) {
        resonatorService.deleteResonator(data);

        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponseDto.of("OK", "공명자 정보가 삭제되었습니다."));
    }
}
