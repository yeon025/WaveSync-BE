// MIGRATED to fastapi/app/repositories/user_echo_sub_repository.py
package io.github.wavesync.repository;
import io.github.wavesync.entity.UserEchoSub;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;


@Repository
public interface UserEchoSubRepository extends JpaRepository<UserEchoSub, Long> {

    @Modifying
    @Query("""
        update UserEchoSub ues
        set ues.isDeleted = true
        where ues.userEcho.userResonator.id in :ids
          and ues.isDeleted = false
    """)
    void softDeleteByUserResonatorIds(@Param("ids") List<Long> ids);
}
