package io.github.wavesync.repository;
import io.github.wavesync.entity.FinalStat;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;


@Repository
public interface FinalStatRepository extends JpaRepository<FinalStat, Long> {

}
