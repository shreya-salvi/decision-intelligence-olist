with orders as (
    select * from {{ ref('stg_orders') }}
    where order_status = 'delivered'
    and order_delivered_customer_date is not null
    and order_estimated_delivery_date is not null
),

items as (
    select * from {{ ref('stg_order_items') }}
),

reviews as (
    select
        order_id,
        avg(review_score) as avg_review_score
    from {{ ref('stg_order_reviews') }}
    group by order_id
),

joined as (
    select
        i.seller_id,
        date_trunc('week', o.order_purchase_timestamp) as week,
        o.order_id,
        case
            when o.order_delivered_customer_date <= o.order_estimated_delivery_date
            then 1 else 0
        end as is_on_time,
        r.avg_review_score,
        i.price,
        i.freight_value
    from orders o
    join items i on o.order_id = i.order_id
    left join reviews r on o.order_id = r.order_id
)

select
    seller_id,
    week,
    count(distinct order_id)                    as total_orders,
    round(avg(is_on_time) * 100, 2)             as on_time_rate,
    round(avg(avg_review_score), 2)             as avg_review_score,
    round(avg(freight_value / nullif(price, 0)) * 100, 2) as freight_pct_of_price
from joined
group by seller_id, week
order by week, seller_id