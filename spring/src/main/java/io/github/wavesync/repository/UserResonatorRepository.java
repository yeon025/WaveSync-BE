package io.github.wavesync.repository;
import io.github.wavesync.entity.UserResonator;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;


@Repository
public interface UserResonatorRepository extends JpaRepository<UserResonator, Long> {

}
