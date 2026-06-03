with source as (
    select * from read_csv_auto(
        'C:/Users/shrey/Desktop/projects/The Decision Intelligence/raw/olist_order_items_dataset.csv',
        header = true
    )
)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    cast(price as double) as price,
    cast(freight_value as double) as freight_value
from source
where order_id is not null