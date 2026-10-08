from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ExpenseForm, SaleForm, VehicleForm
from .models import Vehicle


def staff_required(view):
    """Logged-in staff only. Anonymous users go to login, others get 403."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def form_page(request, form, title):
    return render(request, "inventory/form.html", {"form": form, "title": title})


@login_required
def dashboard(request):
    cars = Vehicle.objects.prefetch_related("expenses")
    available = [v for v in cars if v.status == Vehicle.Status.AVAILABLE and not v.archived]
    sold = [v for v in cars if v.status == Vehicle.Status.SOLD]
    return render(request, "inventory/dashboard.html", {
        "available_count": len(available),
        "sold_count": len(sold),
        "stock_value": sum((v.total_cost for v in available), Decimal("0")),
        "profit": sum((v.profit for v in sold), Decimal("0")),
    })


@login_required
def vehicle_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    archived = request.GET.get("archived") == "1"
    cars = Vehicle.objects.prefetch_related("expenses")
    if not archived:
        cars = cars.filter(archived=False)
    if status in Vehicle.Status.values:
        cars = cars.filter(status=status)
    if q:
        cars = cars.filter(Q(registration__icontains=q.replace(" ", ""))
                           | Q(make__icontains=q) | Q(model__icontains=q))
    return render(request, "inventory/list.html",
                  {"vehicles": cars, "q": q, "status": status, "archived": archived})


@login_required
def vehicle_detail(request, pk):
    car = get_object_or_404(Vehicle.objects.prefetch_related("expenses"), pk=pk)
    return render(request, "inventory/detail.html", {"v": car, "form": ExpenseForm()})


@login_required
def vehicle_create(request):
    form = VehicleForm(request.POST or None)
    if form.is_valid():
        car = form.save()
        messages.success(request, "Car added.")
        return redirect("vehicle_detail", pk=car.pk)
    return form_page(request, form, "Add a car")


@staff_required
def vehicle_edit(request, pk):
    car = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, instance=car)
    if form.is_valid():
        form.save()
        messages.success(request, "Car updated.")
        return redirect("vehicle_detail", pk=pk)
    return form_page(request, form, f"Edit {car.registration}")


@staff_required
@require_POST
def vehicle_archive(request, pk):
    car = get_object_or_404(Vehicle, pk=pk)
    car.archived = True
    car.save()
    messages.success(request, f"{car.registration} archived.")
    return redirect("vehicle_list")


@staff_required
def vehicle_sell(request, pk):
    car = get_object_or_404(Vehicle, pk=pk, status=Vehicle.Status.AVAILABLE)
    form = SaleForm(request.POST or None, instance=car)
    if form.is_valid():
        form.save()
        messages.success(request, "Marked as sold.")
        return redirect("vehicle_detail", pk=pk)
    return form_page(request, form, f"Sell {car.registration}")


@login_required
@require_POST
def expense_add(request, pk):
    car = get_object_or_404(Vehicle, pk=pk)
    form = ExpenseForm(request.POST)
    if car.status == Vehicle.Status.SOLD:
        messages.error(request, "Expenses cannot be added to a sold car.")
    elif form.is_valid():
        expense = form.save(commit=False)
        expense.vehicle = car
        expense.save()
        messages.success(request, "Expense added.")
    else:
        messages.error(request, "Check the expense details and try again.")
    return redirect("vehicle_detail", pk=pk)
