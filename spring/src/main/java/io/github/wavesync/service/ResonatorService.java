// MIGRATED to fastapi/app/services/resonator_service.py
package io.github.wavesync.service;
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

import java.text.Collator;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;


@Slf4j
@Service
@RequiredArgsConstructor
public class ResonatorService {

    private final ObjectStorageService objectStorageService;
    private final FastApiClient fastApiClient;
    private final ExtractProfileValidationService extractProfileValidationService;
    private final SpecCalculationService specCalculationService;
    private final ResonatorMasterRepository resonatorMasterRepository;
    private final WeaponMasterRepository weaponMasterRepository;
    private final FinalStatRepository finalStatRepository;
    private final UserResonatorRepository userResonatorRepository;
    private final UserResonanceNodeRepository userResonanceNodeRepository;
    private final UserEchoRepository userEchoRepository;
    private final UserEchoSubRepository userEchoSubRepository;
    private static final Collator KOREAN_COLLATOR = Collator.getInstance(Locale.KOREAN);


    @Transactional
    public CreateResonatorResponseDto createResonator(MultipartFile resonatorProfile) {

        // 공명자 프로필 이미지 저장
        String profileUrl = objectStorageService.uploadProfileImage(resonatorProfile);
        log.debug("{} 저장을 완료했습니다.", profileUrl);
        
        // 이미지 경로를 ExtractProfileRequestDto로 감쌈
        ExtractProfileRequestDto request = new ExtractProfileRequestDto(profileUrl);

        // fastAPI 호출
        log.info("fastApi 요청을 시작합니다.");
        long start = System.currentTimeMillis();
        ApiResponseDto<ExtractProfileResponseDto> response = fastApiClient.extractImage(request);
        log.info("fastApi 요청이 완료되었습니다. | time={}ms", System.currentTimeMillis() - start);

        // Dto에서 data만 추출
        ExtractProfileResponseDto extractedTexts = response.getData();

        // 검증 로직
        String validatedWeaponName = extractProfileValidationService.validate(extractedTexts);

        // 이름을 기준으로 DB 조회
        ResonatorMaster rm = resonatorMasterRepository.findByName(extractedTexts.getResonatorName());

        WeaponMaster wm = weaponMasterRepository.findByName(validatedWeaponName);

        ResonanceNodeMaster rnm = rm.getResonanceNodeMaster();
        log.debug("추출된 데이터로 데이터베이스 조회를 완료했습니다.");

        // 저장 전에 동일한 공명자는 삭제
        List<Long> targetId = userResonatorRepository.findIdsByResonatorName(extractedTexts.getResonatorName());

        if (!CollectionUtils.isEmpty(targetId)) {
            log.debug("조회한 id: {}", targetId);

            delete(targetId);

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

        // 노드를 dto로 변환
        List<ResonanceNodeDto> nodes = userResonanceNodes.stream()
                .map(node -> ResonanceNodeDto.from(node, rnm))
                .toList();

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

            // 양방향 연관관계 설정
            savedUserResonator.getUserEchoes().add(userEcho);

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

        // UserEcho, UserEchoSub 저장
        userEchoRepository.saveAll(userEchoes);

        userEchoSubRepository.saveAll(userEchoSubs);

        // 최종 스펙 계산
        FinalStat finalStat = specCalculationService.calculateFinalStat(savedUserResonator, nodes);

        // 최종 스펙을 DB에 저장
        finalStatRepository.save(finalStat);
        log.debug("최종 스펙을 데이터베이스에 저장했습니다.");

        return CreateResonatorResponseDto.from(rm);
    }



    @Transactional(readOnly = true)
    public List<ResonatorSummaryResponseDto> getResonatorSummary() {

        List<ResonatorSummaryResponseDto> resonators = resonatorMasterRepository.findResonatorSummary();

        resonators.sort(
                Comparator.comparing(ResonatorSummaryResponseDto::getReleaseVersion)
                        .reversed()
                        .thenComparing(ResonatorSummaryResponseDto::getResonatorName, KOREAN_COLLATOR)
        );

        resonators.forEach(resonator ->
                resonator.setThumbnailImageUrl(objectStorageService.createUrl(resonator.getThumbnailImageUrl()))
        );

        return resonators;
    }



    @Transactional(readOnly = true)
    public ResonatorDetailResponseDto getResonatorDetail(Long userResonatorId) {

        // id로 userResonator 조회
        UserResonator userResonator = userResonatorRepository.findById(userResonatorId)
                .orElseThrow(() -> new CustomException(ErrorCode.RESONATOR_NOT_FOUND));

        // 이미지를 전체 경로로 변환
        String standingImage = objectStorageService.createUrl(userResonator.getResonatorMaster().getStandingImage());
        String weaponImage = objectStorageService.createUrl(userResonator.getWeaponMaster().getImage());

        // dto 생성
        WeaponDetailDto weapon = WeaponDetailDto.from(userResonator, weaponImage);
        ResonatorStatDto stat = ResonatorStatDto.from(userResonator.getFinalStat());

        return ResonatorDetailResponseDto.from(userResonator, standingImage, weapon, stat);
    }



    @Transactional(readOnly = true)
    public ResonatorSettingResponseDto getResonatorSetting(Long userResonatorId) {

        // 공명자 조회
        UserResonator userResonator = userResonatorRepository.findById(userResonatorId)
                .orElseThrow(() -> new CustomException(ErrorCode.RESONATOR_NOT_FOUND));
        log.debug("공명자 조회를 완료했습니다.");

        // 공명자 아이디로 노드 조회
        ResonanceNodeMaster nodeMaster = userResonator.getResonatorMaster().getResonanceNodeMaster();
        log.debug("공명 노드 조회를 완료했습니다.");

        // 조회한 노드를 dto로 변환
        List<ResonanceNodeDto> nodes = userResonator.getUserResonanceNodes().stream()
                .map(node -> ResonanceNodeDto.from(node, nodeMaster))
                .toList();
        log.debug("조회한 공명 노드를 dto로 변환했습니다.");

        // 이미지를 전체 경로로 변환
        String weaponImage = objectStorageService.createUrl(userResonator.getWeaponMaster().getImage());
        log.debug("이미지를 전체 경로로 변환했습니다.");

        // 공명자 아이디로 무기 조회 후 dto로 변환
        WeaponSettingDto weapon = WeaponSettingDto.from(userResonator, weaponImage);
        log.debug("무기 조회 후 dto로 변환했습니다.");

        return ResonatorSettingResponseDto.from(nodes, weapon);
    }



    @Transactional
    public void updateResonator(Long userResonatorId, UpdateResonatorRequestDto data) {

        // id로 userResonator 조회
        UserResonator userResonator = userResonatorRepository.findByIdForUpdate(userResonatorId)
                .orElseThrow(() -> new CustomException(ErrorCode.RESONATOR_NOT_FOUND));

        Set<StatType> requiredType = new HashSet<>();

        // 10개의 공명 노드에서 모든 StatType 수집
        data.getNodes().stream()
                .map(ResonanceNodeDto::getStat)
                .filter(Objects::nonNull)
                .map(StatDto::getType)
                .filter(Objects::nonNull)
                .forEach(requiredType::add);

        // 무기의 재련 옵션 추가
        StatType refineType = userResonator.getWeaponMaster().getRefineType();
        if (refineType != null) { requiredType.add(refineType); }

        // 스펙 재계산
        specCalculationService.reCalculateFinalStat(requiredType, userResonator, data.getNodes(), data.getWeaponRefineLevel());

        // 무기 재련 레벨 변경
        userResonator.setRefineLevel(data.getWeaponRefineLevel());

        // 요청으로 들어온 공명 노드를 위치 기준으로 Map 생성
        Map<String, ResonanceNodeDto> nodeMap = data.getNodes().stream()
                .collect(Collectors.toMap(
                        node -> node.getBranchPosition() + "_" + node.getNodePosition(),
                        Function.identity()
                ));

        // 공명 노드 활성화 상태 변경
        for (UserResonanceNode node : userResonator.getUserResonanceNodes()) {
            String key = node.getBranchPosition() + "_" + node.getNodePosition();

            ResonanceNodeDto dto = nodeMap.get(key);
            node.setIsActive(dto.getActive());
        }
    }



    @Transactional
    public void deleteResonator(DeleteResonatorRequestDto data) {
        List<Long> ids = data.getUserResonatorIds();

        delete(ids);
    }



    private void delete(List<Long> targetId) {
        // user_resonators (soft delete)
        userResonatorRepository.softDeleteByIds(targetId);

        // user_resonance_nodes (soft delete)
        userResonanceNodeRepository.softDeleteByUserResonatorIds(targetId);

        // user_echo (soft delete)
        userEchoRepository.softDeleteByUserResonatorIds(targetId);

        // user_echo_sub (soft delete)
        userEchoSubRepository.softDeleteByUserResonatorIds(targetId);

        // final_stat (hard delete)
        finalStatRepository.deleteByUserResonatorIds(targetId);
    }
}
