with bps as (
    select * from {{ ref('stg_bps_kunjungan') }}
),
cuaca as (
    select * from {{ ref('stg_cuaca_bulanan') }}
),
trends as (
    select * from {{ ref('stg_trends_bulanan') }}
)

select  
    bps.nama_provinsi,
    bps.tahun,
    bps.bulan,
    bps.jumlah_wisman,
    bps.jumlah_wisnus,
    bps.tpk,
    bps.rlm,
    cuaca.avg_suhu_max,
    cuaca.avg_suhu_min,
    cuaca.total_curah_hujan,
    trends.avg_skor_trends,
    (cuaca.avg_suhu_max + cuaca.avg_suhu_min) / 2 as avg_suhu
from bps
left join cuaca on bps.nama_provinsi = cuaca.nama_provinsi
                and bps.tahun = cuaca.tahun
                and bps.bulan = cuaca.bulan
left join trends on bps.nama_provinsi = trends.nama_provinsi
                and bps.tahun = trends.tahun
                and bps.bulan = trends.bulan
