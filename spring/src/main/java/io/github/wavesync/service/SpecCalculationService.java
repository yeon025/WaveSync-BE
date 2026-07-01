package io.github.wavesync.service;
import io.github.wavesync.dto.common.EchoDto;
import io.github.wavesync.dto.common.StatDto;
import io.github.wavesync.entity.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.List;
import java.util.function.Consumer;

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
    private EchoStat getEchoStat(List<UserEcho> echoes, StatType percentType, StatType flatType) {
        BigDecimal percent = BigDecimal.ZERO;
        BigDecimal flat = BigDecimal.ZERO;

        for (UserEcho echo : echoes) {

            // 메인 옵션의 백분율 스탯 합산
            if (echo.getMainType() == percentType) {
                percent = percent.add(echo.getMainValue());
            }

            // 보조 옵션의 고정 스탯 합산
            if (echo.getSecondaryType() == flatType) {
                flat = flat.add(BigDecimal.valueOf(echo.getSecondaryValue()));
            }

            // 서브 옵션의 백분율 스탯 및 고정 스탯 합산
            for (UserEchoSub sub : echo.getUserEchoSubs()) {
                if (sub.getType() == percentType) { percent = percent.add(sub.getValue()); }

                if (sub.getType() == flatType) { flat = flat.add(sub.getValue()); }
            }
        }

        return new EchoStat(percent, flat);
    }



    // 무기에서 획득한 백분율 스탯 합산
    private BigDecimal getWeaponStatPercent(
            WeaponMaster weaponMaster, StatType statType, Integer weaponRefineLevel
    ) {
        BigDecimal percent = BigDecimal.ZERO;

        BigDecimal refineValue = switch (weaponRefineLevel) {
            case 1 -> weaponMaster.getRefine1Value();
            case 2 -> weaponMaster.getRefine2Value();
            case 3 -> weaponMaster.getRefine3Value();
            case 4 -> weaponMaster.getRefine4Value();
            case 5 -> weaponMaster.getRefine5Value();
            default -> throw new IllegalArgumentException("잘못된 무기 레벨입니다.");
        };

        // 무기 주 옵션
        if (weaponMaster.getMainType() == statType) {
            percent = percent.add(weaponMaster.getMainValue());
        }

        // 무기 재련 옵션
        if (weaponMaster.getRefineType() == statType) {
            percent = percent.add(refineValue);
        }

        // 전체 속성 피해 보너스
        if (isElementDamageType(statType)
                && weaponMaster.getRefineType() == StatType.ALL_ATTRIBUTE_DAMAGE_BONUS) {

            percent = percent.add(refineValue);
        }

        // 일반 공격 + 강공격 피해 보너스
        if (isBasicOrHeavyDamageType(statType)
                && weaponMaster.getRefineType() == StatType.BASIC_AND_HEAVY_ATTACK_DAMAGE_BONUS) {

            percent = percent.add(refineValue);
        }

        return percent;
    }


    // 공명 노드에서 획득한 백분율 스탯 합산
    private BigDecimal getNodeStatPercent(
            ResonanceNodeMaster nodeMaster, StatType statType
    ) {
        BigDecimal percent = BigDecimal.ZERO;

        // 외부 노드 (상단 2개, 중단 2개)
        if (nodeMaster.getOuterNodeType() == statType) {
            percent = percent.add(nodeMaster.getOuterTopNodeValue().multiply(BigDecimal.valueOf(2)));
            percent = percent.add(nodeMaster.getOuterMiddleNodeValue().multiply(BigDecimal.valueOf(2)));
        }

        // 내부 노드 (상단 2개, 중단 2개)
        if (nodeMaster.getInnerNodeType() == statType) {
            percent = percent.add(nodeMaster.getInnerTopNodeValue().multiply(BigDecimal.valueOf(2)));
            percent = percent.add(nodeMaster.getInnerMiddleNodeValue().multiply(BigDecimal.valueOf(2)));
        }

        return percent;
    }


    private Integer calculateStat(
            Integer baseStat, List<UserEcho> echoes, WeaponMaster weaponMaster, ResonanceNodeMaster nodeMaster,
            StatType percentStatType, StatType echoFlatType, Integer weaponRefineLevel
    ) {
        final BigDecimal HUNDRED = BigDecimal.valueOf(100);

        log.debug("baseStat: {}", baseStat);

        // 무기에서 획득한 백분율 스탯
        BigDecimal weaponStatPercent = getWeaponStatPercent(weaponMaster, percentStatType, weaponRefineLevel);

        // 공명 노드에서 획득한 백분율 스탯
        BigDecimal nodeStatPercent = getNodeStatPercent(nodeMaster, percentStatType);

        // 무기와 공명 노드의 백분율 스탯 합산
        BigDecimal statPercent = weaponStatPercent.add(nodeStatPercent);

        // 에코에서 획득한 백분율 스탯과 고정 스탯
        EchoStat echoStat = getEchoStat(echoes, percentStatType, echoFlatType);

        // 에코 백분율을 소수로 변환 (22 -> 0.22)
        BigDecimal echoPercentRate = echoStat.percent().divide(HUNDRED);

        // 에코 스탯 계산
        // 에코 스탯 = 기초 스탯 × 에코 백분율 + 에코 고정 스탯
        Integer totalEchoStat = BigDecimal.valueOf(baseStat)
                                .multiply(echoPercentRate)
                                .add(echoStat.flat())
                                .intValue();
        log.debug("echoFlat: {}", echoStat.flat());
        log.debug("echoPercentRate: {}%", echoStat.percent());
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
            List<UserEcho> echoes, ResonatorMaster resonatorMaster,
            WeaponMaster weaponMaster, ResonanceNodeMaster nodeMaster, Integer weaponRefineLevel
    ) {
        log.debug("HP 계산을 시작합니다.");

        return calculateStat(
                resonatorMaster.getHp(), echoes, weaponMaster, nodeMaster,
                StatType.HP_PERCENT, StatType.HP, weaponRefineLevel
        );
    }


    public Integer calculateAttack(
            List<UserEcho> echoes, ResonatorMaster resonatorMaster,
            WeaponMaster weaponMaster, ResonanceNodeMaster nodeMaster, Integer weaponRefineLevel
    ) {
        log.debug("공격력 계산을 시작합니다.");

        return calculateStat(
                resonatorMaster.getAttack() + weaponMaster.getAttackValue(),
                echoes, weaponMaster, nodeMaster, StatType.ATTACK_PERCENT, StatType.ATTACK, weaponRefineLevel
        );
    }


    public Integer calculateDefense(
            List<UserEcho> echoes, ResonatorMaster resonatorMaster,
            WeaponMaster weaponMaster, ResonanceNodeMaster nodeMaster, Integer weaponRefineLevel
    ) {
        log.debug("방어력 계산을 시작합니다.");

        return calculateStat(
                resonatorMaster.getDefense(), echoes, weaponMaster, nodeMaster,
                StatType.DEFENSE_PERCENT, StatType.DEFENSE, weaponRefineLevel
        );
    }


    public BigDecimal calculatePercentStat(
            BigDecimal baseValue, List<UserEcho> echoes, WeaponMaster weaponMaster, ResonanceNodeMaster nodeMaster, StatType statType, Integer refineLevel
    ) {
        // 기본 수치(예: 치명타 확률 5%, 치명타 피해 150%)
        BigDecimal result = baseValue;

        // 무기에서 획득한 백분율 스탯
        BigDecimal weaponStatPercent = getWeaponStatPercent(weaponMaster, statType, refineLevel);

        // 공명 노드에서 획득한 백분율 스탯
        BigDecimal nodeStatPercent = getNodeStatPercent(nodeMaster, statType);

        // 무기와 공명 노드의 백분율 스탯 합산
        BigDecimal statPercent = weaponStatPercent.add(nodeStatPercent);

        // 에코 메인 옵션, 서브 옵션에서 획득한 스탯 합산
        for (UserEcho echo : echoes) {

            if (echo.getMainType() == statType) {
                result = result.add(echo.getMainValue());
            }

            for (UserEchoSub sub : echo.getUserEchoSubs()) {
                if (sub.getType() == statType) {
                    result = result.add(sub.getValue());
                }
            }
        }
        log.debug("{} 최종 스탯 합산 : {}%", statType, result);

        return result;
    }


    public FinalStat calculateFinalStat(
            UserResonator userResonator, List<UserEcho> userEchoes,
            ResonatorMaster resonatorMaster, WeaponMaster weaponMaster, ResonanceNodeMaster nodeMaster
    ) {
        return FinalStat.builder()
                .hp(calculateHp(userEchoes, resonatorMaster, weaponMaster, nodeMaster, 1))
                .attack(calculateAttack(userEchoes, resonatorMaster, weaponMaster, nodeMaster, 1))
                .defense(calculateDefense(userEchoes, resonatorMaster, weaponMaster, nodeMaster, 1))
                .energyRegen(calculatePercentStat(
                        BigDecimal.valueOf(100), userEchoes, weaponMaster, nodeMaster, StatType.ENERGY_REGEN, 1
                ))
                .criticalRate(calculatePercentStat(
                        BigDecimal.valueOf(5), userEchoes, weaponMaster, nodeMaster, StatType.CRITICAL_RATE, 1
                ))
                .criticalDamage(calculatePercentStat(
                        BigDecimal.valueOf(150), userEchoes, weaponMaster, nodeMaster, StatType.CRITICAL_DAMAGE, 1
                ))
                .resonanceSkillDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.RESONANCE_SKILL_DAMAGE_BONUS, 1
                ))
                .basicAttackDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.BASIC_ATTACK_DAMAGE_BONUS, 1
                ))
                .heavyAttackDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.HEAVY_ATTACK_DAMAGE_BONUS, 1
                ))
                .resonanceLiberationDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.RESONANCE_LIBERATION_DAMAGE_BONUS, 1
                ))
                .glacioDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.GLACIO_DAMAGE_BONUS, 1
                ))
                .fusionDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.FUSION_DAMAGE_BONUS, 1
                ))
                .conductoDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.CONDUCTO_DAMAGE_BONUS, 1
                ))
                .aeroDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.AERO_DAMAGE_BONUS, 1
                ))
                .spectraDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.SPECTRA_DAMAGE_BONUS, 1
                ))
                .havocDamageBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.HAVOC_DAMAGE_BONUS, 1
                ))
                .healingBonus(calculatePercentStat(
                        BigDecimal.ZERO, userEchoes, weaponMaster, nodeMaster, StatType.HEALING_BONUS, 1
                ))
                .userResonator(userResonator)
                .build();
    }
}
