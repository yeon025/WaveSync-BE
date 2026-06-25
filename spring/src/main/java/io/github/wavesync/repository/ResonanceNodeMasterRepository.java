package io.github.wavesync.repository;
import io.github.wavesync.entity.ResonanceNodeMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;





@Repository
public interface ResonanceNodeMasterRepository extends JpaRepository<ResonanceNodeMaster, Long> {

    ResonanceNodeMaster findByResonatorMasterId(Long id);
}
