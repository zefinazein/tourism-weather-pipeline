with source as (
	select * from {{ source('raw', 'raw_google_trends') }}
),

filtered as (
    select * from source where tanggal is not null
),

unpivoted as (
    select
        tanggal,
        nama_provinsi,
        skor_trends
    from filtered
    unpivot (
        skor_trends for nama_provinsi in (
            wisata_bali as 'BALI',
            wisata_yogyakarta as 'DI YOGYAKARTA',
            wisata_lombok as 'NUSA TENGGARA BARAT',
            wisata_palembang as 'SUMATERA SELATAN',
            wisata_surabaya as 'JAWA TIMUR'
        )
    )
)

select
    nama_provinsi,
    extract(year from cast(tanggal as date)) as tahun,
    extract(month from cast(tanggal as date)) as bulan,
    avg(skor_trends) as avg_skor_trends
from unpivoted
group by nama_provinsi, tahun, bulan
