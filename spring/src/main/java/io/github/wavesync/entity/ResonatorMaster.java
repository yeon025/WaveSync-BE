package io.github.wavesync.entity;
import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;
import lombok.*;



@Entity
@Table(name = "resonator_master")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class ResonatorMaster {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 20, unique = true)
    private String name;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Element element;

    @Column(nullable = false)
    private Integer rarity;

    @Column(nullable = false)
    private Integer hp;

    @Column(nullable = false)
    private Integer attack;

    @Column(nullable = false)
    private Integer defense;

    @Column(name = "release_version", nullable = false)
    private Integer releaseVersion;

    @Column(name = "thumbnail_image", nullable = false, length = 255)
    private String thumbnailImage;

    @Column(name = "standing_image", length = 255)
    private String standingImage;

    @OneToOne(mappedBy = "resonatorMaster")
    private ResonanceNodeMaster resonanceNodeMaster;

    @Builder.Default
    @OneToMany(mappedBy = "resonatorMaster")
    private List<UserResonator> userResonators = new ArrayList<>();
}