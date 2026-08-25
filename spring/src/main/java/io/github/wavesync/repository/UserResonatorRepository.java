// MIGRATED to fastapi/app/repositories/user_resonator_repository.py
package io.github.wavesync.repository;
import io.github.wavesync.entity.UserResonator;
import org.jetbrains.annotations.NotNull;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;


@Repository
public interface UserResonatorRepository extends JpaRepository<UserResonator, Long> {

    @Modifying
    @Query("""
        select ur.id
        from UserResonator ur
        where ur.resonatorMaster.name = :name
          and ur.isDeleted = false
    """)
    List<Long> findIdsByResonatorName(@Param("name") String name);


    @Modifying
    @Query("""
        update UserResonator ur
        set ur.isDeleted = true
        where ur.id in :ids
          and ur.isDeleted = false
    """)
    void softDeleteByIds(@Param("ids") List<Long> ids);


    @NotNull
    @Query("""
        select ur
        from UserResonator ur
        join fetch ur.resonatorMaster
        join fetch ur.weaponMaster
        join fetch ur.finalStat
        where ur.id = :userResonatorId
          and ur.isDeleted = false
    """)
    Optional<UserResonator> findById(@NotNull Long userResonatorId);

    @Query("SELECT DISTINCT ur FROM UserResonator ur " +
            "JOIN FETCH ur.resonatorMaster " +
            "JOIN FETCH ur.weaponMaster " +
            "JOIN FETCH ur.finalStat " +
            "LEFT JOIN FETCH ur.userEchoes " +
            "WHERE ur.id = :userResonatorId AND ur.isDeleted = false")
    Optional<UserResonator> findByIdForUpdate(Long userResonatorId);
}
