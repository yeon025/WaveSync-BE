package io.github.wavesync.repository;
import io.github.wavesync.entity.UserResonanceNode;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;


@Repository
public interface UserResonanceNodeRepository extends JpaRepository<UserResonanceNode, Long> {

    @Modifying
    @Query("""
        update UserResonanceNode urn
        set urn.isDeleted = true
        where urn.userResonator.id in :ids
          and urn.isDeleted = false
    """)
    void softDeleteByUserResonatorIds(@Param("ids") List<Long> ids);

    @Query("""
        select urn
        from UserResonanceNode urn
        where urn.userResonator.id = :userResonatorId
          and urn.isDeleted = false
        order by urn.branchPosition, urn.nodePosition
    """)
    List<UserResonanceNode> findAllByUserResonatorId(Long userResonatorId);
}
