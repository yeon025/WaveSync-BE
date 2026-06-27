package io.github.wavesync.repository;
import io.github.wavesync.entity.WeaponMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;



@Repository
public interface WeaponMasterRepository extends JpaRepository<WeaponMaster, Long> {

    WeaponMaster findByName(String name);
}
