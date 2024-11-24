import re

def parse_discount_from_text(offer_text):
    """
    Extract discount values from the offer text and calculate the effective discount percentage.
    - For "X% off" or "Y% off for the second piece" patterns, calculate directly.
    - For "buy X, get Y free" patterns, calculate an equivalent percentage discount.
    """
    # Initial discount percentage
    discount_pct = 0

    # Pattern matching percentages and buy-get offers
    percent_off = re.findall(r"(\d+)% off", offer_text)

    buy_get_offer = re.search(r"buy (\d+) pieces and get (\d+)% off", offer_text, re.IGNORECASE)
    buy_x_get_y_free = re.search(r"buy (\d+) pieces for the price of (\d+)", offer_text, re.IGNORECASE)
    # Sum up all percentage discounts found
    if percent_off:
        # print('percent_off')
        discount_pct = sum(map(int, percent_off)) / len(percent_off)
        # print('discount_pct percent_off', discount_pct)

    # Handle "buy X get Y% off" case
    if buy_get_offer:
        # print('buy_get_offer')
        buy_qty = int(buy_get_offer.group(1))
        # print('buy_qty', buy_qty)
        discount_for_second = int(buy_get_offer.group(2))
        # print('discount_for_second', discount_for_second)
        discount_pct = (discount_for_second / buy_qty)
        # print('discount_pct buy_get_offer', discount_pct)

    # Handle "buy X for price of Y" case
    if buy_x_get_y_free:
        # print('buy_x_get_y_free')
        buy_qty = int(buy_x_get_y_free.group(1))
        # print('buy_qty', buy_qty)
        free_qty = int(buy_x_get_y_free.group(2))
        # print('free_qty', free_qty)
        discount_pct = (free_qty / buy_qty)*100
        # print('discount_pct buy_x_get_y_free', discount_pct)

    return discount_pct


# check1 = parse_discount_from_text("50% off")
# print(check1)

# check2 = parse_discount_from_text("Buy 2 pieces for the price of 1 piece only")
# print(check2)

# check3 = parse_discount_from_text("Buy 2 pieces and get 50% off on the second piece")
# print(check3)


# Buy 2 pieces for the price of 1 piece only
# Buy 2 pieces and get 50% off on the second piece
