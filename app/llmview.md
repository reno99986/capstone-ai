
CREATE OR REPLACE VIEW usaha_llm AS
(
    SELECT
        'geotags'::text AS source,
        g.id AS usaha_id,
        g.id_user AS user_id,
        g.nama_usaha,
        g.nama_komersial_usaha,
        g.alamat,
        g.kd_prov::text AS kdprov,
        g.kd_kab::text AS kdkab,
        g.kd_kec::text AS kdkec,
        g.kd_desa::text AS kddesa,
        g.kd_sls::text AS kdsls,
        sm.nmprov,
        sm.nmkab,
        sm.nmkec,
        sm.nmdesa,
        sm.nmsls,
        g.kbli_section,
        g.kbli_code,
        kc.title AS kbli_title,
        kc.section_code,
        ks.section_name AS kbli_section_name,
        g.kategori,
        g.produk_utama,
        g.status,
        g.latitude,
        g.longitude,
        g.created_at,
        g.updated_at
    FROM geotags g
    LEFT JOIN sls_map sm
        ON g.kd_prov::text = sm.kdprov::text
       AND g.kd_kab::text = sm.kdkab::text
       AND g.kd_kec::text = sm.kdkec::text
       AND g.kd_desa::text = sm.kddesa::text
       AND g.kd_sls::text = sm.kdsls::text
    LEFT JOIN kbli_code kc
        ON g.kbli_code::text = kc.code::text
    LEFT JOIN kbli_section ks
        ON g.kbli_section = ks.section_code

    UNION ALL

    SELECT
        'prelist'::text AS source,
        gp.id AS usaha_id,
        gp.user_id,
        gp.nama_usaha,
        gp.nama_komersial AS nama_komersial_usaha,
        gp.alamat,
        gp.kd_prov::text AS kdprov,
        gp.kd_kab::text AS kdkab,
        gp.kd_kec::text AS kdkec,
        gp.kd_desa::text AS kddesa,
        gp.kd_sls::text AS kdsls,
        sm.nmprov,
        sm.nmkab,
        sm.nmkec,
        sm.nmdesa,
        sm.nmsls,
        gp.kbli_section,
        gp.kbli_code,
        kc.title AS kbli_title,
        kc.section_code,
        ks.section_name AS kbli_section_name,
        gp.kategori,
        gp.produk_utama,
        gp.status,
        gp.latitude,
        gp.longitude,
        gp.created_at,
        gp.updated_at
    FROM geotag_prelist gp
    LEFT JOIN sls_map sm
        ON gp.kd_prov::text = sm.kdprov::text
       AND gp.kd_kab::text = sm.kdkab::text
       AND gp.kd_kec::text = sm.kdkec::text
       AND gp.kd_desa::text = sm.kddesa::text
       AND gp.kd_sls::text = sm.kdsls::text
    LEFT JOIN kbli_code kc
        ON gp.kbli_code::text = kc.code::text
    LEFT JOIN kbli_section ks
        ON gp.kbli_section = ks.section_code
);
