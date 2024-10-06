from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserForm, ProfileForm, ProductForm, PhotoFormSet, ProductAccountLinkFormSet, ProductAccountIdLinkFormSet, PromoPlanForm # , ProductKeywordFormSet, KeywordForm
from .models import Profile, Product, PromoPlan #, Keyword
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
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        account_link_formset = ProductAccountLinkFormSet(request.POST, prefix='accounts')
        account_id_link_formset = ProductAccountIdLinkFormSet(request.POST, prefix='account_ids')  # New formset
        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix='photos')

        if all([product_form.is_valid(), account_link_formset.is_valid(), account_id_link_formset.is_valid(), photo_formset.is_valid()]):  # Updated validation
            product = product_form.save(commit=False)
            product.profile = request.user.profile
            product.save()

            # Handle account links
            for form in account_link_formset.save(commit=False):
                form.product = product
                form.save()
            account_link_formset.save_m2m()

            # Handle account id links (New block)
            for form in account_id_link_formset.save(commit=False):
                form.product = product
                form.save()
            account_id_link_formset.save_m2m()

            # Handle photos
            for form in photo_formset.save(commit=False):
                form.product = product
                form.save()
            photo_formset.save_m2m()

            return redirect('client_profile:profile_products')
    else:
        product_form = ProductForm()
        account_link_formset = ProductAccountLinkFormSet(prefix='accounts')
        account_id_link_formset = ProductAccountIdLinkFormSet(prefix='account_ids')  # New formset
        photo_formset = PhotoFormSet(prefix='photos')

    return render(request, 'client_profile/product_create.html', {
        'product_form': product_form,
        'account_link_formset': account_link_formset,
        'account_id_link_formset': account_id_link_formset,  # Pass the new formset to the template
        'photo_formset': photo_formset,
        'segment': 'product_create',
    })


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
    context = {
        'profile': profile,
        'products': products,
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
