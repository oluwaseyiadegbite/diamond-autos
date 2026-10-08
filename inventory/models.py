from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        SOLD = "sold", "Sold"

    registration = models.CharField(max_length=10, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField()
    colour = models.CharField(max_length=30, blank=True)
    mileage = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    purchase_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.01"))])
    sale_date = models.DateField(null=True, blank=True)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.registration} {self.make} {self.model}"

    def save(self, *args, **kwargs):
        self.registration = self.registration.replace(" ", "").upper()
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}
        if self.year and not 1950 <= self.year <= timezone.localdate().year + 1:
            errors["year"] = "Enter a realistic year."
        if self.status == self.Status.SOLD:
            if self.sale_price is None:
                errors["sale_price"] = "A sale price is required for sold cars."
            if self.sale_date and self.purchase_date and self.sale_date < self.purchase_date:
                errors["sale_date"] = "Sale date cannot be before the purchase date."
        if errors:
            raise ValidationError(errors)
    @property
    def days_in_stock(self):
        if self.status == self.Status.SOLD and self.sale_date:
            end = self.sale_date
        else:
            end = timezone.localdate()
        return (end - self.purchase_date).days
    @property
    def total_expenses(self):
        return sum((e.amount for e in self.expenses.all()), Decimal("0"))

    @property
    def total_cost(self):
        return self.purchase_price + self.total_expenses

    @property
    def profit(self):
        """sale price - purchase price - recorded expenses (None until sold)."""
        if self.status != self.Status.SOLD or self.sale_price is None:
            return None
        return self.sale_price - self.purchase_price - self.total_expenses


class Expense(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="expenses")
    description = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.description}: {self.amount}"
