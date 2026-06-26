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
        select new io.github.wavesync.dto.response.ResonatorSummaryResponseDto(
            ur.id,
            m.name,
            m.rarity,
            m.releaseVersion,
            m.thumbnailImage
        )
        from ResonatorMaster m
        left join UserResonator ur
            on ur.resonatorMaster = m
           and ur.isDeleted = false
        order by m.releaseVersion desc, m.name asc
    """)
    List<ResonatorSummaryResponseDto> findResonatorSummary();
}
