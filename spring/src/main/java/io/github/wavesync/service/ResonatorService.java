package io.github.wavesync.service;
import io.github.wavesync.dto.request.DeleteResonatorRequestDto;
import io.github.wavesync.dto.request.UpdateResonatorRequestDto;
import io.github.wavesync.dto.response.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;


@Service
@RequiredArgsConstructor
public class ResonatorService {



    public CreateResonatorResponseDto createResonator(MultipartFile resonatorProfile) {

        return null;
    }


    public ResonatorSummaryResponseDto getResonatorSummary() {

        return null;
    }


    public ResonatorDetailResponseDto getResonatorDetail(Long userResonatorId) {

        return null;
    }


    public void updateResonator(Long userResonatorId, UpdateResonatorRequestDto data) {

    }

    public void deleteResonator(DeleteResonatorRequestDto data) {

    }
}
