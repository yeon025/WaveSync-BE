package io.github.wavesync.repository;
import io.github.wavesync.entity.WeaponMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.Optional;


@Repository
public interface WeaponMasterRepository extends JpaRepository<WeaponMaster, Long> {

    WeaponMaster findByName(String name);

    @Query("""
        SELECT w
        FROM WeaponMaster w
        WHERE REPLACE(w.name, ' ', '') = :name
    """)
    Optional<WeaponMaster> findByNameWithoutSpaces(@Param("name") String name);
}
