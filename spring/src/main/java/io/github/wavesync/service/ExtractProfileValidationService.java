package io.github.wavesync.service;

import io.github.wavesync.dto.common.EchoDto;
import io.github.wavesync.dto.common.StatDto;
import io.github.wavesync.dto.response.ExtractProfileResponseDto;
import io.github.wavesync.entity.StatType;
import io.github.wavesync.entity.WeaponMaster;
import io.github.wavesync.exception.CustomException;
import io.github.wavesync.exception.ErrorCode;
import io.github.wavesync.repository.ResonatorMasterRepository;
import io.github.wavesync.repository.WeaponMasterRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExtractProfileValidationService {

    private final ResonatorMasterRepository resonatorMasterRepository;
    private final WeaponMasterRepository weaponMasterRepository;

    private static final Map<StatType, Set<BigDecimal>> VALID_SUB_VALUES = createValidSubValues();

    public String validate(ExtractProfileResponseDto dto) {
        validateResonator(dto.getResonatorName());

        String weaponName = validateWeapon(dto.getWeaponName());

        validateSubs(dto.getEchoes());

        return weaponName;
    }

    private void validateResonator(String resonatorName) {
        if (!resonatorMasterRepository.existsByName(resonatorName)) {
            log.warn("공명자 이름이 마스터 데이터에 존재하지 않습니다. resonatorName={}", resonatorName);
            throw new CustomException(ErrorCode.VALIDATION_FAILED);
        }
    }

    private String validateWeapon(String extractedName) {
        return weaponMasterRepository
                .findByNameWithoutSpaces(extractedName)
                .map(WeaponMaster::getName)
                .orElseThrow(() -> {
                    log.warn("무기 이름이 마스터 데이터에 존재하지 않습니다. weaponName={}", extractedName);
                    return new CustomException(ErrorCode.VALIDATION_FAILED);
                });
    }

    private void validateSubs(List<EchoDto> echoes) {
        for (int i = 0; i < echoes.size(); i++) {
            EchoDto echo = echoes.get(i);

            for (int j = 0; j < echo.getSubs().size(); j++) {
                StatDto sub = echo.getSubs().get(j);

                validateSubType(sub, i + 1, j + 1);
                validateSubValue(sub, i + 1, j + 1);
            }
        }
    }

    private void validateSubType(StatDto sub, int echoNumber, int subNumber) {
        if (sub.getType() == null || !VALID_SUB_VALUES.containsKey(sub.getType())) {
            log.warn(
                    "{}번 에코의 {}번 서브 속성 이름이 마스터 데이터에 존재하지 않습니다. subType={}",
                    echoNumber,
                    subNumber,
                    sub.getType()
            );
            throw new CustomException(ErrorCode.VALIDATION_FAILED);
        }
    }

    private void validateSubValue(StatDto sub, int echoNumber, int subNumber) {
        Set<BigDecimal> validValues = VALID_SUB_VALUES.get(sub.getType());

        if (sub.getValue() == null ||
                validValues.stream().noneMatch(validValue -> validValue.compareTo(sub.getValue()) == 0)) {

            log.warn(
                    "{}번 에코의 {}번 서브 속성 값이 마스터 데이터에 존재하지 않습니다. subValue={}",
                    echoNumber,
                    subNumber,
                    sub.getValue()
            );
            throw new CustomException(ErrorCode.VALIDATION_FAILED);
        }
    }

    private static Map<StatType, Set<BigDecimal>> createValidSubValues() {
        Map<StatType, Set<BigDecimal>> values = new EnumMap<>(StatType.class);

        values.put(StatType.CRITICAL_RATE, decimals("6.3", "6.9", "7.5", "8.1", "8.7", "9.3", "9.9", "10.5"));

        values.put(StatType.CRITICAL_DAMAGE, decimals("12.6", "13.8", "15.0", "16.2", "17.4", "18.6", "19.8", "21.0"));

        values.put(StatType.ENERGY_REGEN, decimals("6.8", "7.6", "8.4", "9.2", "10.0", "10.8", "11.6", "12.4"));

        values.put(StatType.DEFENSE_PERCENT, decimals("8.1", "9.0", "10.0", "10.9", "11.8", "12.8", "13.8", "14.7"));

        values.put(StatType.DEFENSE, decimals("40", "50", "60", "70"));

        values.put(StatType.ATTACK_PERCENT, decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6"));

        values.put(StatType.ATTACK, decimals("30", "40", "50", "60"));

        values.put(StatType.HP_PERCENT, decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6"));

        values.put(StatType.HP, decimals("320", "360", "390", "430", "470", "510", "540", "580"));

        Set<BigDecimal> damageBonusValues = decimals("6.4", "7.1", "7.9", "8.6", "9.4", "10.1", "10.9", "11.6");

        values.put(StatType.BASIC_ATTACK_DAMAGE_BONUS, damageBonusValues);

        values.put(StatType.HEAVY_ATTACK_DAMAGE_BONUS, damageBonusValues);

        values.put(StatType.RESONANCE_SKILL_DAMAGE_BONUS, damageBonusValues);

        values.put(StatType.RESONANCE_LIBERATION_DAMAGE_BONUS, damageBonusValues);

        return Collections.unmodifiableMap(values);
    }

    private static Set<BigDecimal> decimals(String... values) {
        return Set.of(Arrays.stream(values)
                .map(BigDecimal::new)
                .toArray(BigDecimal[]::new)
        );
    }
}