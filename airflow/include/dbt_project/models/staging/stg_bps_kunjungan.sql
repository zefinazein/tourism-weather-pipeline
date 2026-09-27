with source as (
    select * from {{ source('raw', 'raw_bps_kunjungan') }}
)

select
    upper(trim(provinsi)) as nama_provinsi,
    tahun,
    bulan,
    jumlah_wisman,
    jumlah_wisnus,
    tpk,
    rlm
from source
where jumlah_wisman is not null and jumlah_wisman >= 0