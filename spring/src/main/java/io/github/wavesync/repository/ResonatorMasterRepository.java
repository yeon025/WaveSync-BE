// MIGRATED to fastapi/app/repositories/resonator_master_repository.py
package io.github.wavesync.repository;
import io.github.wavesync.dto.response.ResonatorSummaryResponseDto;
import io.github.wavesync.entity.ResonatorMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;


@Repository
public interface ResonatorMasterRepository extends JpaRepository<ResonatorMaster, Long> {

    ResonatorMaster findByName(String name);

    @Query("""
    SELECT new io.github.wavesync.dto.response.ResonatorSummaryResponseDto(
        ur.id,
        m.name,
        m.rarity,
        m.releaseVersion,
        m.thumbnailImage
    )
    FROM ResonatorMaster m
    LEFT JOIN UserResonator ur
        ON ur.resonatorMaster = m
       AND ur.isDeleted = false
    """)
    List<ResonatorSummaryResponseDto> findResonatorSummary();

    boolean existsByName(String name);
}
