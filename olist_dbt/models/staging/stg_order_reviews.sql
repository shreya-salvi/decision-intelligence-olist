with source as (
    select * from read_csv_auto(
        'C:/Users/shrey/Desktop/projects/The Decision Intelligence/raw/olist_order_reviews_dataset.csv',
        header = true
    )
)

select
    review_id,
    order_id,
    cast(review_score as integer) as review_score
from source
where order_id is not null