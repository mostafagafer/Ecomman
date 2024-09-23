# from decimal import Decimal, ROUND_HALF_UP

# def calculate_pds(set_price, store_prices):
#     if not store_prices:
#         return 0
#     # Calculate average deviation with precise rounding
#     average_deviation = sum(abs(Decimal(price) - Decimal(set_price)) for price in store_prices) / len(store_prices)
#     pds = (1 - (average_deviation / Decimal(set_price))) * 100
#     # Round PDS to two decimal places
#     pds = pds.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     return float(pds)


# def calculate_pcs(set_price, store_prices, acceptable_range_percentage=10):
#     if not store_prices:
#         return 0
#     acceptable_range = set_price * (acceptable_range_percentage / 100)
#     compliant_stores = sum(1 for price in store_prices if set_price - acceptable_range <= price <= set_price + acceptable_range)
#     total_stores = len(store_prices)
#     pcs = (compliant_stores / total_stores) * 100
#     return pcs
