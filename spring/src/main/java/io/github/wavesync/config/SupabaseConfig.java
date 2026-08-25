// MIGRATED to fastapi/app/services/supabase_storage_service.py (client 구성이 서비스 생성자로 흡수됨)
package io.github.wavesync.config;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.web.client.RestClient;


@Configuration
@Profile("prod")
public class SupabaseConfig {

    @Value("${supabase.url}")
    private String url;

    @Value("${supabase.service-key}")
    private String serviceKey;

    @Bean
    public RestClient supabaseRestClient() {
        return RestClient.builder()
                .baseUrl(url)
                .defaultHeader("apikey", serviceKey)
                .defaultHeader("Authorization", "Bearer " + serviceKey)
                .build();
    }
}
