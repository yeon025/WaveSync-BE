package io.github.wavesync.repository;
import io.github.wavesync.entity.ResonatorMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;


@Repository
public interface ResonatorMasterRepository extends JpaRepository<ResonatorMaster, Long> {

    ResonatorMaster findByName(String name);

    @Query(value = """
        SELECT
            ur.id,
            m.name,
            m.rarity,
            m.release_version,
            m.thumbnail_image
        FROM resonator_master m
        LEFT JOIN user_resonators ur
            ON ur.resonator_master_id = m.id
           AND ur.is_deleted = false
        ORDER BY
            m.release_version DESC,
            m.name COLLATE "ko-KR-x-icu"
        """, nativeQuery = true)
    List<Object[]> findResonatorSummary();;
}
