package io.github.wavesync.repository;
import io.github.wavesync.entity.ResonatorMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;


@Repository
public interface ResonatorMasterRepository extends JpaRepository<ResonatorMaster, Long> {

    ResonatorMaster findByName(String name);
}
