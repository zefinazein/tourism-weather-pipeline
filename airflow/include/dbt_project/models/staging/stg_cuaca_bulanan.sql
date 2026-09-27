with source as (
	select * from {{ source('raw', 'raw_openmeteo_cuaca') }}
),

filtered as (
	select * from source
	where suhu_max_c between -10 and 50
	      and suhu_min_c between -10 and 50
	      and curah_hujan_mm >= 0
),
mapped as (
	select 
		case kota
		when 'bali' then 'BALI'
		when 'yogyakarta' then 'DI YOGYAKARTA'
		when 'lombok' then 'NUSA TENGGARA BARAT'
		when 'palembang' then 'SUMATERA SELATAN'
		when 'surabaya' then 'JAWA TIMUR'
		else upper(kota)
	end as nama_provinsi,
		tanggal,
		curah_hujan_mm,
		suhu_max_c,
		suhu_min_c
	from filtered
)

select
	nama_provinsi,
	extract(year from cast(tanggal as date)) as tahun,
	extract(month from cast(tanggal as date)) as bulan,
    avg(suhu_max_c) as avg_suhu_max,
    avg(suhu_min_c) as avg_suhu_min,
    sum(curah_hujan_mm) as total_curah_hujan
from mapped
group by nama_provinsi, tahun, bulan