from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserForm, ProfileForm, ProductForm, PhotoFormSet, ProductChannelFormSet, PromoPlanForm # , ProductKeywordFormSet, KeywordForm, ProductAccountLinkFormSet
from .models import CHANNELS, Brand, Category, Channel, Photo, ProductChannel, Profile, Product, PromoPlan, Subcategory #, Keyword
from django.urls import reverse
# from django.core.exceptions import ValidationError
from django.contrib import messages

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    products = profile.products.all()
    return render(request, 'client_profile/profile.html', {
        'profile': profile, 
        'user': request.user,  
        'products': products,
        'segment': 'client_profile'
    })

@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, profile=request.user.profile)
    return render(request, 'client_profile/product_detail.html', {'product': product})

# @login_required
# def product_create(request):
#     if request.method == 'POST':
#         product_form = ProductForm(request.POST)
#         account_link_formset = ProductAccountLinkFormSet(request.POST, prefix='accounts')
#         photo_formset = PhotoFormSet(request.POST, request.FILES, prefix='photos')

#         if all([product_form.is_valid(), account_link_formset.is_valid(), photo_formset.is_valid()]):
#             product = product_form.save(commit=False)
#             product.profile = request.user.profile
#             product.save()

        

#             # Handle account links
#             for form in account_link_formset.save(commit=False):
#                 form.product = product
#                 form.save()
#             account_link_formset.save_m2m()

#             # Handle photos
#             for form in photo_formset.save(commit=False):
#                 form.product = product
#                 form.save()
#             photo_formset.save_m2m()

#             return redirect('client_profile:profile_products')
#     else:
#         product_form = ProductForm()
#         account_link_formset = ProductAccountLinkFormSet(prefix='accounts')
#         photo_formset = PhotoFormSet(prefix='photos')

#     return render(request, 'client_profile/product_create.html', {
#         'product_form': product_form,
#         'account_link_formset': account_link_formset,
#         'photo_formset': photo_formset,
#         'segment': 'product_create',
#     })
@login_required
def product_create(request):
    channel_options = _get_channel_options()
    own_products = Product.objects.filter(profile=request.user.profile, is_competitor=False).order_by('product_name')
    taxonomy_options = _get_taxonomy_options()
    if request.method == 'POST':
        product_form = ProductForm(request.POST)

        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.profile = request.user.profile
            _apply_taxonomy_from_form(product, product_form)
            _normalize_product_by_type(product)
            product.save()
            _save_product_extras(product, request)
            return redirect('client_profile:profile_products')
    else:
        product_form = ProductForm()

    return render(request, 'client_profile/product_create.html', {
        'product_form': product_form,
        'channel_options': channel_options,
        'own_products': own_products,
        'taxonomy_options': taxonomy_options,
        'selected_channels': [],
        'selected_competitor_refs': [],
        'product': None,
        'segment': 'product_create',
    })


def _get_channel_options():
    logo_map = {
        'al_dawa': 'img/logos/Al-dawa_logo.png',
        'amazon_sa': 'img/logos/amazon-sa-logo.jpg',
        'nahdi': 'img/logos/Nahdi_logo.png',
        'nice_one': 'img/logos/NiceOne_logo.svg',
        'ana_ninja': 'img/logos/Ninja_logo.png',
        'noon_sa': 'img/logos/NoonSA_logo.svg',
    }
    preferred_keys = ['al_dawa', 'amazon_sa', 'nahdi', 'nice_one', 'ana_ninja', 'noon_sa']
    options = []
    for key in preferred_keys:
        Channel.objects.get_or_create(key=key)
        options.append({
            'key': key,
            'name': CHANNELS[key]['display_name'],
            'logo': logo_map[key],
            'url': CHANNELS[key]['website_url'],
        })
    return options


def _normalize_product_by_type(product):
    if product.is_competitor:
        product.description = ''
        product.brand = None
        product.category = None
        product.subcategory = None


def _get_taxonomy_options():
    return {
        'brands': Brand.objects.order_by('name').values_list('name', flat=True).distinct(),
        'categories': Category.objects.order_by('name').values_list('name', flat=True).distinct(),
        'subcategories': Subcategory.objects.order_by('name').values_list('name', flat=True).distinct(),
    }


def _clean_name(value):
    return (value or '').strip()


def _get_or_create_named(model, name, **extra_filters):
    existing = model.objects.filter(name__iexact=name, **extra_filters).first()
    if existing:
        return existing
    return model.objects.create(name=name, **extra_filters)


def _apply_taxonomy_from_form(product, form):
    if product.is_competitor:
        return

    brand_name = _clean_name(form.cleaned_data.get('brand_name'))
    category_name = _clean_name(form.cleaned_data.get('category_name'))
    subcategory_name = _clean_name(form.cleaned_data.get('subcategory_name'))

    product.brand = _get_or_create_named(Brand, brand_name) if brand_name else None
    product.category = _get_or_create_named(Category, category_name) if category_name else None
    product.subcategory = (
        _get_or_create_named(Subcategory, subcategory_name, category=product.category)
        if subcategory_name and product.category
        else None
    )


def _save_product_extras(product, request):
    selected_channel_keys = request.POST.getlist('channels')
    ProductChannel.objects.filter(product=product).exclude(channel__key__in=selected_channel_keys).delete()
    for key in selected_channel_keys:
        channel = Channel.objects.get(key=key)
        ProductChannel.objects.update_or_create(
            product=product,
            channel=channel,
            defaults={'is_enabled': True, 'search_name': product.product_name},
        )

    if product.is_competitor:
        product.photos.all().delete()
        reference_ids = request.POST.getlist('competitor_references')
        references = Product.objects.filter(profile=product.profile, is_competitor=False, id__in=reference_ids)
        product.competitor_references.set(references)
    else:
        product.competitor_references.clear()
        image = request.FILES.get('product_photo')
        if image:
            product.photos.all().delete()
            Photo.objects.create(product=product, image=image)


@login_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id, profile=request.user.profile)
    channel_options = _get_channel_options()
    own_products = Product.objects.filter(profile=request.user.profile, is_competitor=False).exclude(id=product.id).order_by('product_name')
    selected_channels = list(product.channels.values_list('key', flat=True))
    selected_competitor_refs = list(product.competitor_references.values_list('id', flat=True))
    taxonomy_options = _get_taxonomy_options()

    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            _apply_taxonomy_from_form(product, product_form)
            _normalize_product_by_type(product)
            product.save()
            _save_product_extras(product, request)
            return redirect('client_profile:profile_products')
    else:
        product_form = ProductForm(instance=product)

    return render(request, 'client_profile/product_edit.html', {
        'product': product,
        'product_form': product_form,
        'channel_options': channel_options,
        'own_products': own_products,
        'taxonomy_options': taxonomy_options,
        'selected_channels': selected_channels,
        'selected_competitor_refs': selected_competitor_refs,
        'segment': 'product_edit',
    })


@login_required
def product_delete(request, id):
    product = get_object_or_404(Product, id=id, profile=request.user.profile)
    if request.method == 'POST':
        product_name = product.product_name
        product.delete()
        messages.success(request, f'{product_name} deleted successfully.')
    return redirect('client_profile:profile_products')


# @login_required
# def product_edit(request, id):
#     product = get_object_or_404(Product, id=id, profile=request.user.profile)

#     if request.method == 'POST':
#         product_form = ProductForm(request.POST, instance=product)
#         account_link_formset = ProductAccountLinkFormSet(request.POST, instance=product)
#         photo_formset = PhotoFormSet(request.POST, request.FILES, instance=product)

#         if product_form.is_valid() and account_link_formset.is_valid() and photo_formset.is_valid():
#             try:
#                 product = product_form.save(commit=False)
#                 product.save()

#                 # Handle account links
#                 for account_link in account_link_formset.save(commit=False):
#                     if 'remove-account-0' in request.POST:
#                         account_link.delete()
#                     else:
#                         account_link.product = product
#                         account_link.save()
#                 account_link_formset.save_m2m()

#                 # Handle photos
#                 for photo in photo_formset.save(commit=False):
#                     if 'remove-photo-0' in request.POST:
#                         photo.delete()
#                     else:
#                         photo.product = product
#                         photo.save()
#                 photo_formset.save_m2m()

#                 return redirect('client_profile:profile_products')
#             except Exception as e:
#                 print(e)
#                 return render(request, 'client_profile/product_edit.html', {
#                     'product': product,
#                     'product_form': product_form,
#                     'account_link_formset': account_link_formset,
#                     'photo_formset': photo_formset,
#                 })
#     else:
#         product_form = ProductForm(instance=product)
#         account_link_formset = ProductAccountLinkFormSet(instance=product)
#         photo_formset = PhotoFormSet(instance=product)

#     return render(request, 'client_profile/product_edit.html', {
#         'product': product,
#         'product_form': product_form,
#         'account_link_formset': account_link_formset,
#         'photo_formset': photo_formset,
#     })


# @login_required
# def product_edit(request, id):
#     product = get_object_or_404(Product, id=id, profile=request.user.profile)

#     if request.method == 'POST':
#         product_form = ProductForm(request.POST, instance=product)
#         account_link_formset = ProductAccountLinkFormSet(request.POST, instance=product)
#         photo_formset = PhotoFormSet(request.POST, request.FILES, instance=product)

#         if product_form.is_valid() and account_link_formset.is_valid() and photo_formset.is_valid():
#             try:
#                 product = product_form.save()

#                 # Handle account links
#                 for account_link in account_link_formset.save(commit=False):
#                     if 'remove-account-0' in request.POST:
#                         account_link.delete()
#                     else:
#                         account_link.product = product
#                         account_link.save()
#                 account_link_formset.save_m2m()

#                 # Handle photos
#                 for photo in photo_formset.save(commit=False):
#                     if 'remove-photo-0' in request.POST:
#                         photo.delete()
#                     else:
#                         photo.product = product
#                         photo.save()
#                 photo_formset.save_m2m()


#                 # Handle keywords using formset
#                 keyword_formset = ProductKeywordFormSet(request.POST, instance=product)
#                 for form in keyword_formset:
#                     if form.is_valid():
#                         form.instance.save()  # Directly save each valid keyword instance

#                 return redirect('client_profile:profile_products')
#             except Exception as e:
#                 print(e)
#                 return render(request, 'client_profile/product_edit.html', {
#                     'product': product,
#                     'product_form': product_form,
#                     'account_link_formset': account_link_formset,
#                     'photo_formset': photo_formset,
#                 })
#     else:
#         product_form = ProductForm(instance=product)
#         account_link_formset = ProductKeywordFormSet(instance=product)
#         photo_formset = PhotoFormSet(instance=product)

#     return render(request, 'client_profile/product_edit.html', {
#         'product': product,
#         'product_form': product_form,
#         'account_link_formset': account_link_formset,
#         'photo_formset': photo_formset,
#     })



@login_required
def profile_products(request):
    profile = Profile.objects.get(user=request.user)
    products = profile.products.all()
    my_products = products.filter(is_competitor=False).order_by('product_name')
    competitor_products = products.filter(is_competitor=True).order_by('product_name')
    context = {
        'profile': profile,
        'products': products,
        'my_products': my_products,
        'competitor_products': competitor_products,
        'segment': 'profile_products'
    }
    return render(request, 'client_profile/profile_products.html', context)


@login_required
def profile_edit(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        userform = UserForm(request.POST, instance=request.user)
        profileform = ProfileForm(request.POST, request.FILES, instance=profile)
        if userform.is_valid() and profileform.is_valid():
            userform.save()
            profileform.save()
            return redirect(reverse('client_profile:profile_view'))
    else:
        userform = UserForm(instance=request.user)
        profileform = ProfileForm(instance=profile)

    return render(request, 'client_profile/profile_edit.html', {'userform': userform, 'profileform': profileform})



# Promo manager
@login_required
def promo_plan_list(request):
    # Get all promo plans for the current user's profile
    promo_plans = PromoPlan.objects.filter(product__profile__user=request.user)

    context = {
        'promo_plans': promo_plans,
        'segment': 'promo_plan_lists'
    }
    return render(request, 'client_profile/promo_plan_list.html', context)



@login_required
def create_or_edit_promo_plan(request, pk=None):
    if pk:
        promo_plan = get_object_or_404(PromoPlan, pk=pk)
        if promo_plan.profile.user != request.user:
            return redirect('client_profile:promo_plan_list')
    else:
        promo_plan = PromoPlan(profile=request.user.profile)

    if request.method == 'POST':
        form = PromoPlanForm(request.POST, instance=promo_plan, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('client_profile:promo_plan_list')
    else:
        form = PromoPlanForm(instance=promo_plan, user=request.user)

    return render(request, 'client_profile/promo_plan_form.html', {'form': form})


def remove_promo_plan(request, pk):
    promo_plan = get_object_or_404(PromoPlan, pk=pk)
    promo_plan.delete()
    messages.success(request, 'Promo plan removed successfully.')
    return redirect('client_profile:promo_plan_list')
