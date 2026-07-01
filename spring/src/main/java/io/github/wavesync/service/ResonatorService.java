package io.github.wavesync.service;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.wavesync.client.FastApiClient;
import io.github.wavesync.dto.common.*;
import io.github.wavesync.dto.request.*;
import io.github.wavesync.dto.response.*;
import io.github.wavesync.entity.*;
import io.github.wavesync.exception.*;
import io.github.wavesync.repository.*;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;
import org.springframework.web.multipart.MultipartFile;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;


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
    private final UserResonanceNodeRepository userResonanceNodeRepository;
    private final UserEchoRepository userEchoRepository;
    private final UserEchoSubRepository userEchoSubRepository;


    @Transactional
    public CreateResonatorResponseDto createResonator(MultipartFile resonatorProfile) {

        // 공명자 프로필 이미지 저장
        String profileUrl = objectStorageService.uploadProfileImage(resonatorProfile);
        log.debug("{} 저장을 완료했습니다.", profileUrl);
        
        // 이미지 경로를 ExtractProfileRequestDto로 감쌈
        ExtractProfileRequestDto request = new ExtractProfileRequestDto(profileUrl);

        // fastAPI 호출
        log.info("fastApi 요청을 시작합니다.");
        ApiResponseDto<ExtractProfileResponseDto> response = fastApiClient.extractImage(request);
        log.info("fastApi 요청이 완료되었습니다.");

        // Dto에서 data만 추출
        ExtractProfileResponseDto extractedTexts = response.getData();

        // 이름을 기준으로 DB 조회
        ResonatorMaster rm = resonatorMasterRepository.findByName(extractedTexts.getResonatorName());
        WeaponMaster wm = weaponMasterRepository.findByName(extractedTexts.getWeaponName());
        ResonanceNodeMaster rnm = resonanceNodeMasterRepository.findByResonatorMasterId(rm.getId());
        log.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.");

        // 저장 전에 동일한 공명자는 삭제
        List<Long> targetId = userResonatorRepository.findIdsByResonatorName(extractedTexts.getResonatorName());

        if (!CollectionUtils.isEmpty(targetId)) {
            log.debug("조회한 id: {}", targetId);

            userResonatorRepository.softDeleteByIds(targetId);
            userResonanceNodeRepository.softDeleteByUserResonatorIds(targetId);
            userEchoRepository.softDeleteByUserResonatorIds(targetId);
            userEchoSubRepository.softDeleteByUserResonatorIds(targetId);
            finalStatRepository.deleteByUserResonatorIds(targetId);

            log.debug("동일한 공명자 정보를 삭제했습니다.");
        }

        // UserResonator 객체 생성 후 저장
        UserResonator userResonator = UserResonator.builder()
                .resonanceChainLevel(extractedTexts.getResonanceChainLevel())
                .refineLevel(1)
                .resonatorMaster(rm)
                .weaponMaster(wm)
                .build();
        UserResonator savedUserResonator = userResonatorRepository.save(userResonator);

        // UserResonanceNode 객체 생성 후 저장
        List<UserResonanceNode> userResonanceNodes = new ArrayList<>();

        for (BranchPosition branchPosition : BranchPosition.values()) {
            for (NodePosition nodePosition : NodePosition.values()) {
                userResonanceNodes.add(
                        UserResonanceNode.builder()
                                .branchPosition(branchPosition)
                                .nodePosition(nodePosition)
                                .userResonator(userResonator)
                                .build()
                );
            }
        }
        userResonanceNodeRepository.saveAll(userResonanceNodes);

        // Echo 객체 생성
        List<UserEcho> userEchoes = new ArrayList<>();
        List<UserEchoSub> userEchoSubs = new ArrayList<>();

        for (EchoDto echo : extractedTexts.getEchoes()) {

            UserEcho userEcho = UserEcho.builder()
                    .mainType(echo.getMain().getType())
                    .mainValue(echo.getMain().getValue())
                    .secondaryType(echo.getSecondary().getType())
                    .secondaryValue(echo.getSecondary().getValue().intValue())
                    .userResonator(userResonator)
                    .build();

            userEchoes.add(userEcho);

            for (StatDto sub : echo.getSubs()) {

                UserEchoSub userEchoSub = UserEchoSub.builder()
                        .type(sub.getType())
                        .value(sub.getValue())
                        .userEcho(userEcho)
                        .build();

                // 양방향 연관관계 설정
                userEcho.getUserEchoSubs().add(userEchoSub);

                userEchoSubs.add(userEchoSub);
            }
        }

        // UserEcho 5개 저장
        List<UserEcho> savedUserEchoes = userEchoRepository.saveAll(userEchoes);

        // UserEchoSub 25개 저장
        userEchoSubRepository.saveAll(userEchoSubs);

        // 최종 스펙 계산
        FinalStat finalStat = specCalculationService.calculateFinalStat(savedUserResonator, savedUserEchoes, rm, wm, rnm);

        // 최종 스펙을 DB에 저장
        finalStatRepository.save(finalStat);
        log.debug("최종 스펙을 데이터베이스에 저장했습니다.");

        return CreateResonatorResponseDto.from(rm);
    }



    @Transactional(readOnly = true)
    public List<ResonatorSummaryResponseDto> getResonatorSummary() {

        return resonatorMasterRepository.findResonatorSummary()
                .stream()
                .map(row -> new ResonatorSummaryResponseDto(
                        row[0] == null ? null : ((Number) row[0]).longValue(),
                        (String) row[1],
                        ((Number) row[2]).intValue(),
                        ((Number) row[3]).intValue(),
                        (String) row[4]
                ))
                .toList();
    }



    @Transactional(readOnly = true)
    public ResonatorDetailResponseDto getResonatorDetail(Long userResonatorId) {

        // id로 userResonator 조회
        UserResonator userResonator = userResonatorRepository.findDetailById(userResonatorId)
                .orElseThrow(() -> new CustomException(ErrorCode.RESONATOR_NOT_FOUND));

        // dto 생성
        WeaponDetailDto weapon = WeaponDetailDto.from(userResonator);
        ResonatorStatDto stat = ResonatorStatDto.from(userResonator.getFinalStat());

        return ResonatorDetailResponseDto.from(userResonator, weapon, stat);
    }



    @Transactional(readOnly = true)
    public ResonatorSettingResponseDto getResonatorSetting(Long userResonatorId) {

        // 공명자 조회
        UserResonator userResonator = userResonatorRepository.findById(userResonatorId)
                .orElseThrow(() -> new CustomException(ErrorCode.RESONATOR_NOT_FOUND));

        // 공명자 아이디로 노드 조회
        ResonanceNodeMaster nodeMaster = resonanceNodeMasterRepository.findByResonatorMasterId(userResonator.getResonatorMaster().getId());

        // 조회한 노드를 dto로 변환
        List<ResonanceNodeDto> nodes = userResonator.getUserResonanceNode().stream()
                .map(node -> ResonanceNodeDto.from(node, nodeMaster))
                .toList();

        // 공명자 아이디로 무기 조회 후 dto로 변환
        WeaponSettingDto weapon = WeaponSettingDto.from(userResonator);

        return ResonatorSettingResponseDto.from(nodes, weapon);
    }



    @Transactional
    public void updateResonator(Long userResonatorId, UpdateResonatorRequestDto data) {

    }



    @Transactional
    public void deleteResonator(DeleteResonatorRequestDto data) {
        List<Long> ids = data.getUserResonatorIds();

        // user_resonators (soft delete)
        userResonatorRepository.softDeleteByIds(ids);

        // user_resonance_nodes (soft delete)
        userResonanceNodeRepository.softDeleteByUserResonatorIds(ids);

        // user_echo (soft delete)
        userEchoRepository.softDeleteByUserResonatorIds(ids);

        // user_echo_sub (soft delete)
        userEchoSubRepository.softDeleteByUserResonatorIds(ids);

        // final_stat (hard delete)
        finalStatRepository.deleteByUserResonatorIds(ids);
    }
}
