with source as (
    select * from read_csv_auto(
        'C:/Users/shrey/Desktop/projects/The Decision Intelligence/raw/olist_sellers_dataset.csv',
        header = true
    )
)

select
    seller_id,
    seller_city,
    seller_state
from source
where seller_id is not null