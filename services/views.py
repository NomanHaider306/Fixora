from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceCategory
from .forms import ServiceCategoryForm


@login_required
def category_list_admin(request):
    if not request.user.is_administrator:
        messages.error(request, "Access restricted to administrators.")
        return redirect('accounts:dashboard_redirect')
    categories = ServiceCategory.objects.all().order_by('name')
    return render(request, 'services/admin_category_list.html', {'categories': categories})


@login_required
def category_create_admin(request):
    if not request.user.is_administrator:
        messages.error(request, "Access restricted to administrators.")
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created successfully!")
            return redirect('services:category_list_admin')
    else:
        form = ServiceCategoryForm()
    return render(request, 'services/admin_category_form.html', {'form': form, 'title': 'Add New Category'})


@login_required
def category_update_admin(request, pk):
    if not request.user.is_administrator:
        messages.error(request, "Access restricted to administrators.")
        return redirect('accounts:dashboard_redirect')

    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect('services:category_list_admin')
    else:
        form = ServiceCategoryForm(instance=category)
    return render(request, 'services/admin_category_form.html', {'form': form, 'category': category, 'title': f'Edit Category: {category.name}'})


@login_required
def category_toggle_admin(request, pk):
    if not request.user.is_administrator:
        messages.error(request, "Access restricted to administrators.")
        return redirect('accounts:dashboard_redirect')

    category = get_object_or_404(ServiceCategory, pk=pk)
    category.is_active = not category.is_active
    category.save()
    status_str = "activated" if category.is_active else "deactivated"
    messages.success(request, f"Category '{category.name}' has been {status_str}.")
    return redirect('services:category_list_admin')


@login_required
def category_delete_admin(request, pk):
    if not request.user.is_administrator:
        messages.error(request, "Access restricted to administrators.")
        return redirect('accounts:dashboard_redirect')

    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        cat_name = category.name
        category.delete()
        messages.success(request, f"Category '{cat_name}' has been deleted.")
        return redirect('services:category_list_admin')
    return render(request, 'services/admin_category_confirm_delete.html', {'category': category})
