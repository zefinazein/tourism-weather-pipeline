select id_provinsi, id_waktu, count(*)
from {{ ref('fact_kunjungan_pariwisata') }}
group by id_provinsi, id_waktu
having count(*) > 1