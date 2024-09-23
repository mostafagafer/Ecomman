from django import template

register = template.Library()



@register.filter
def get_price_for_account(data, account):
    if not account:
        return None  # or some default value or message

    # Construct the field name based on the account
    account_price_field = f"{account.lower()}_price"
    
    # Retrieve the price from the data
    return data.get(account_price_field, None)



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item2(instance, field_name):
    return getattr(instance, field_name, None)


@register.filter
def replace(value, arg):
    old, new = arg.split(',')
    return value.replace(old, new)
