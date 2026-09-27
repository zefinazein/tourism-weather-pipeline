with master as (
    select * from {{ ref('int_master_join') }}
),
waktu as (
    select * from {{ ref('dim_waktu') }}
),
kategori as (
    select * from {{ ref('dim_kategori_cuaca') }}
),
provinsi as (
    select * from {{ ref('dim_provinsi') }}
)

select
    waktu.id_waktu,
    provinsi.id_provinsi,
    kategori.id_kategori as id_kategori_cuaca,
    master.jumlah_wisman,
    master.jumlah_wisnus,
    master.tpk,
    master.rlm,
    master.avg_suhu,
    master.total_curah_hujan,
    master.avg_skor_trends as skor_trends
from master
left join waktu
    on master.tahun = waktu.tahun and master.bulan = waktu.bulan
left join provinsi
    on master.nama_provinsi = provinsi.nama_provinsi
left join kategori
    on master.total_curah_hujan >= kategori.min_mm
    and master.total_curah_hujan < kategori.max_mm