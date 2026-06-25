package io.github.wavesync.service;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.wavesync.client.FastApiClient;
import io.github.wavesync.dto.request.*;
import io.github.wavesync.dto.response.*;
import io.github.wavesync.entity.*;
import io.github.wavesync.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;


@Slf4j
@Service
@RequiredArgsConstructor
public class ResonatorService {

    private final ObjectStorageService objectStorageService;
    private final FastApiClient fastApiClient;
    private final ObjectMapper objectMapper;
    private final SpecCalculationService specCalculationService;
    private final ResonatorMasterRepository resonatorMasterRepository;
    private final WeaponMasterRepository weaponMasterRepository;
    private final ResonanceNodeMasterRepository resonanceNodeMasterRepository;
    private final FinalStatRepository finalStatRepository;
    private final UserResonatorRepository userResonatorRepository;

    public CreateResonatorResponseDto createResonator(MultipartFile resonatorProfile) {

        // 공명자 프로필 이미지 저장
        String profileUrl = objectStorageService.uploadProfileImage(resonatorProfile);
        log.info("{} 저장을 완료했습니다.", profileUrl);
        
        // 이미지 경로를 ExtractProfileRequestDto로 감쌈
        ExtractProfileRequestDto request = new ExtractProfileRequestDto(profileUrl);

        // fastAPI 호출
        log.info("fastApi 요청을 시작합니다.");
        ApiResponseDto<ExtractProfileResponseDto> response = fastApiClient.extractImage(request);
        ExtractProfileResponseDto extractedTexts = response.getData();
        try {
            log.info(objectMapper.writeValueAsString(extractedTexts));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }

        // 이름을 기준으로 DB 조회
        ResonatorMaster resonatorInfo = resonatorMasterRepository.findByName(extractedTexts.getResonatorName());
        WeaponMaster weaponInfo = weaponMasterRepository.findByName(extractedTexts.getWeaponName());
        ResonanceNodeMaster nodeInfo = resonanceNodeMasterRepository.findByResonatorMasterId(resonatorInfo.getId());
        log.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.");

        // DB 저장을 위한 UserResonator 객체 생성
        UserResonator userResonator = UserResonator.builder()
                .resonanceChainLevel(extractedTexts.getResonanceChainLevel())
                .refineLevel(1)
                .resonatorMaster(resonatorInfo)
                .weaponMaster(weaponInfo)
                .build();

        // user_resonators에 저장
        UserResonator savedUserResonator = userResonatorRepository.save(userResonator);

        // 최종 스펙 계산
        FinalStat finalStat = specCalculationService.calculateFinalStat(savedUserResonator, extractedTexts.getEchoes(), resonatorInfo, weaponInfo, nodeInfo);
        log.debug("HP: {}, 공격력: {}, 방어력: {}, 공명 효율: {}, 크리티컬: {}, 크리티컬 피해: {}",
                finalStat.getHp(), finalStat.getAttack(), finalStat.getDefense(), finalStat.getEnergyRegen(), finalStat.getCriticalRate(), finalStat.getCriticalDamage());

        // 최종 스펙을 DB에 저장
        finalStatRepository.save(finalStat);
        log.debug("최종 스펙을 데이터베이스에 저장했습니다.");

        return CreateResonatorResponseDto.from(resonatorInfo);
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
