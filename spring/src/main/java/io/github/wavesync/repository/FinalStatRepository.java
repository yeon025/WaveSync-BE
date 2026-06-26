package io.github.wavesync.repository;
import io.github.wavesync.entity.FinalStat;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;



@Repository
public interface FinalStatRepository extends JpaRepository<FinalStat, Long> {

    @Modifying
    @Query("""
        delete from FinalStat fs
        where fs.userResonator.id in :ids
    """)
    void deleteByUserResonatorIds(@Param("ids") List<Long> ids);
}
