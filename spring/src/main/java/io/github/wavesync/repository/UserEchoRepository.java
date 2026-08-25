// MIGRATED to fastapi/app/repositories/user_echo_repository.py
package io.github.wavesync.repository;
import io.github.wavesync.entity.UserEcho;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;


@Repository
public interface UserEchoRepository extends JpaRepository<UserEcho, Long> {

    @Modifying
    @Query("""
        update UserEcho ue
        set ue.isDeleted = true
        where ue.userResonator.id in :ids
          and ue.isDeleted = false
    """)
    void softDeleteByUserResonatorIds(@Param("ids") List<Long> ids);
}
