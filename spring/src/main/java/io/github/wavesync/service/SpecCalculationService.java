package io.github.wavesync.service;
import io.github.wavesync.dto.common.EchoDto;
import io.github.wavesync.dto.common.StatDto;
import io.github.wavesync.entity.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class SpecCalculationService {


    private record EchoStat(BigDecimal percent, BigDecimal flat) {
    }

    private boolean isElementDamageType(StatType statType) {
        return statType == StatType.GLACIO_DAMAGE_BONUS
                || statType == StatType.FUSION_DAMAGE_BONUS
                || statType == StatType.CONDUCTO_DAMAGE_BONUS
                || statType == StatType.AERO_DAMAGE_BONUS
                || statType == StatType.SPECTRA_DAMAGE_BONUS
                || statType == StatType.HAVOC_DAMAGE_BONUS;
    }

    private boolean isBasicOrHeavyDamageType(StatType statType) {
        return statType == StatType.BASIC_ATTACK_DAMAGE_BONUS
                || statType == StatType.HEAVY_ATTACK_DAMAGE_BONUS;
    }

    // 에코에서 획득한 백분율 스탯과 고정 스탯을 합산
    private EchoStat getEchoStat(
            List<EchoDto> echoes, StatType percentType, StatType flatType
    ) {
        BigDecimal percent = BigDecimal.ZERO;
        BigDecimal flat = BigDecimal.ZERO;

        for (EchoDto echo : echoes) {

            // 메인 옵션의 백분율 스탯 합산
            if (percentType == echo.getMain().getType()) {
                percent = percent.add(echo.getMain().getValue());
            }

            // 보조 옵션의 고정 스탯 합산
            if (flatType == echo.getSecondary().getType()) {
                flat = flat.add(echo.getSecondary().getValue());
            }

            // 서브 옵션의 백분율 스탯 및 고정 스탯 합산
            for (StatDto sub : echo.getSubs()) {

                if (sub.getType() == percentType) {
                    percent = percent.add(sub.getValue());
                }

                if (sub.getType() == flatType) {
                    flat = flat.add(sub.getValue());
                }
            }
        }

        return new EchoStat(percent, flat);
    }

    // 무기 및 공명 노드에서 획득한 백분율 스탯 합산
    private BigDecimal getStatPercent(
            WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo, StatType statType
    ) {
        BigDecimal percent = BigDecimal.ZERO;

        // 무기 주 옵션
        if (weaponInfo.getMainType() == statType) {
            percent = percent.add(weaponInfo.getMainValue());
        }

        // 무기 재련 옵션
        if (weaponInfo.getRefineType() == statType) {
            percent = percent.add(BigDecimal.valueOf(weaponInfo.getRefine1Value()));
        }

        // 전체 속성 피해 보너스
        if (isElementDamageType(statType)
                && weaponInfo.getRefineType() == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS) {

            percent = percent.add(BigDecimal.valueOf(weaponInfo.getRefine1Value()));
        }

        // 일반 공격 + 강공격 피해 보너스
        if (isBasicOrHeavyDamageType(statType)
                && weaponInfo.getRefineType() == StatType.BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS) {

            percent = percent.add(BigDecimal.valueOf(weaponInfo.getRefine1Value()));
        }

        // 외부 노드 (상단 2개, 중단 2개)
        if (nodeInfo.getOuterNodeType() == statType) {
            percent = percent.add(nodeInfo.getOuterTopNodeValue().multiply(BigDecimal.valueOf(2)));
            percent = percent.add(nodeInfo.getOuterMiddleNodeValue().multiply(BigDecimal.valueOf(2)));
        }

        // 내부 노드 (상단 2개, 중단 2개)
        if (nodeInfo.getInnerNodeType() == statType) {
            percent = percent.add(nodeInfo.getInnerTopNodeValue().multiply(BigDecimal.valueOf(2)));
            percent = percent.add(nodeInfo.getInnerMiddleNodeValue().multiply(BigDecimal.valueOf(2)));
        }

        return percent;
    }


    private Integer calculateStat(
            Integer baseStat, List<EchoDto> echoes, WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo,
            StatType percentStatType, StatType echoPercentType, StatType echoFlatType
    ) {
        final BigDecimal HUNDRED = BigDecimal.valueOf(100);

        log.debug("baseStat: {}", baseStat);

        // 무기 + 공명 노드에서 획득한 백분율 스탯
        BigDecimal statPercent = getStatPercent(weaponInfo, nodeInfo, percentStatType);
        log.debug("statPercent: {}%", statPercent);

        // 에코에서 획득한 백분율 스탯과 고정 스탯
        EchoStat echoStat = getEchoStat(echoes, echoPercentType, echoFlatType);

        // 에코 백분율을 소수로 변환 (22 -> 0.22)
        BigDecimal echoPercentRate = echoStat.percent().divide(HUNDRED);

        // 에코 스탯 계산
        // 에코 스탯 = 기초 스탯 × 에코 백분율 + 에코 고정 스탯
        Integer totalEchoStat = BigDecimal.valueOf(baseStat)
                                .multiply(echoPercentRate)
                                .add(echoStat.flat())
                                .intValue();
        log.debug("echoFlat: {}", echoStat.flat());
        log.debug("echoPercentRate: {}%", echoPercentRate);
        log.debug("totalEchoStat: {}", totalEchoStat);

        // 백분율 스탯을 소수로 변환 (30 -> 0.30)
        BigDecimal statRate = statPercent.divide(HUNDRED);

        // 최종 스탯 계산
        // 최종 스탯 = 기초 스탯 × (1 + 백분율 스탯) + 에코 스탯
        return BigDecimal.valueOf(baseStat)
                .multiply(BigDecimal.ONE.add(statRate))
                .add(BigDecimal.valueOf(totalEchoStat))
                .intValue();
    }


    public Integer calculateHp(
            List<EchoDto> echoes, ResonatorMaster resonatorInfo, WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo
    ) {
        log.debug("HP 계산을 시작합니다.");

        return calculateStat(
                resonatorInfo.getHp(), echoes, weaponInfo, nodeInfo,
                StatType.HP_PERCENT, StatType.HP_PERCENT, StatType.HP
        );
    }


    public Integer calculateAttack(
            List<EchoDto> echoes, ResonatorMaster resonatorInfo, WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo
    ) {
        log.debug("공격력 계산을 시작합니다.");

        return calculateStat(
                resonatorInfo.getAttack() + weaponInfo.getAttackValue(),
                echoes, weaponInfo, nodeInfo,
                StatType.ATTACK_PERCENT, StatType.ATTACK_PERCENT, StatType.ATTACK
        );
    }


    public Integer calculateDefense(
            List<EchoDto> echoes, ResonatorMaster resonatorInfo, WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo
    ) {
        log.debug("방어력 계산을 시작합니다.");

        return calculateStat(
                resonatorInfo.getDefense(), echoes, weaponInfo, nodeInfo,
                StatType.DEFENSE_PERCENT, StatType.DEFENSE_PERCENT, StatType.DEFENSE
        );
    }


    public BigDecimal calculatePercentStat(
            BigDecimal baseValue, List<EchoDto> echoes, WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo, StatType statType
    ) {
        // 기본 수치(예: 치명타 확률 5%, 치명타 피해 150%)
        BigDecimal result = baseValue;

        // 무기 및 공명 노드에서 획득한 스탯 합산
        result = result.add(getStatPercent(weaponInfo, nodeInfo, statType));

        // 에코 메인 옵션, 보조 옵션, 서브 옵션에서 획득한 스탯 합산
        for (EchoDto echo : echoes) {

            if (echo.getMain().getType() == statType) {
                result = result.add(echo.getMain().getValue());
            }

            if (echo.getSecondary().getType() == statType) {
                result = result.add(echo.getSecondary().getValue());
            }

            for (StatDto sub : echo.getSubs()) {
                if (sub.getType() == statType) {
                    result = result.add(sub.getValue());
                }
            }
        }

        return result;
    }


    public FinalStat calculateFinalStat(
            UserResonator savedUserResonator, List<EchoDto> echoes, ResonatorMaster resonatorInfo, WeaponMaster weaponInfo, ResonanceNodeMaster nodeInfo
    ) {
        return FinalStat.builder()
                .hp(calculateHp(echoes, resonatorInfo, weaponInfo, nodeInfo))
                .attack(calculateAttack(echoes, resonatorInfo, weaponInfo, nodeInfo))
                .defense(calculateDefense(echoes, resonatorInfo, weaponInfo, nodeInfo))
                .energyRegen(calculatePercentStat(
                        BigDecimal.valueOf(100), echoes, weaponInfo, nodeInfo, StatType.ENERGY_REGEN
                ))
                .criticalRate(calculatePercentStat(
                        BigDecimal.valueOf(5), echoes, weaponInfo, nodeInfo, StatType.CRITICAL_RATE
                ))
                .criticalDamage(calculatePercentStat(
                        BigDecimal.valueOf(150), echoes, weaponInfo, nodeInfo, StatType.CRITICAL_DAMAGE
                ))
                .resonanceSkillDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.RESONANCE_SKILL_DAMAGE_BONUS
                ))
                .basicAttackDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.BASIC_ATTACK_DAMAGE_BONUS
                ))
                .heavyAttackDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.HEAVY_ATTACK_DAMAGE_BONUS
                ))
                .resonanceLiberationDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.RESONANCE_LIBERATION_DAMAGE_BONUS
                ))
                .glacioDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.GLACIO_DAMAGE_BONUS
                ))
                .fusionDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.FUSION_DAMAGE_BONUS
                ))
                .conductoDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.CONDUCTO_DAMAGE_BONUS
                ))
                .aeroDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.AERO_DAMAGE_BONUS
                ))
                .spectraDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.SPECTRA_DAMAGE_BONUS
                ))
                .havocDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.HAVOC_DAMAGE_BONUS
                ))
                .healingBonus(calculatePercentStat(
                        BigDecimal.ZERO, echoes, weaponInfo, nodeInfo, StatType.HEALING_BONUS
                ))
                .userResonator(savedUserResonator)
                .build();
    }
}
