from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Expense, Vehicle


def make_car(reg="AB12CDE", price="5000", **extra):
    return Vehicle.objects.create(
        registration=reg, make="Ford", model="Focus", year=2018,
        purchase_price=Decimal(price), purchase_date=date(2025, 1, 1), **extra)


class CalculationTests(TestCase):
    def test_profit_is_sale_minus_purchase_minus_expenses(self):
        car = make_car()
        Expense.objects.create(vehicle=car, description="Tyres", amount=Decimal("300"))
        Expense.objects.create(vehicle=car, description="Service", amount=Decimal("200"))
        car.status, car.sale_price = Vehicle.Status.SOLD, Decimal("6000")
        car.save()
        self.assertEqual(car.total_expenses, Decimal("500"))
        self.assertEqual(car.profit, Decimal("500"))

    def test_unsold_car_has_no_profit(self):
        self.assertIsNone(make_car().profit)

    def test_loss_is_negative(self):
        car = make_car(status=Vehicle.Status.SOLD, sale_price=Decimal("4000"))
        self.assertEqual(car.profit, Decimal("-1000"))


class ValidationTests(TestCase):
    def test_negative_purchase_price_rejected(self):
        car = Vehicle(registration="X1", make="A", model="B", year=2020,
                      purchase_price=Decimal("-1"), purchase_date=date(2025, 1, 1))
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_sold_car_needs_sale_price(self):
        car = Vehicle(registration="X2", make="A", model="B", year=2020,
                      purchase_price=Decimal("100"), purchase_date=date(2025, 1, 1),
                      status=Vehicle.Status.SOLD)
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_duplicate_registration_rejected(self):
        make_car(reg="DUP1")
        with self.assertRaises(ValidationError):
            Vehicle(registration="DUP1", make="A", model="B", year=2020,
                    purchase_price=Decimal("100"), purchase_date=date(2025, 1, 1)).full_clean()


class AccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("clerk", password="pass-12345")
        self.staff = User.objects.create_user("boss", password="pass-12345", is_staff=True)
        self.car = make_car()

    def test_anonymous_redirected_to_login(self):
        for name in ("dashboard", "vehicle_list", "vehicle_create"):
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 302)
            self.assertIn("/login/", resp["Location"])

    def test_non_staff_cannot_archive(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("vehicle_archive", args=[self.car.pk]))
        self.assertEqual(resp.status_code, 403)
        self.car.refresh_from_db()
        self.assertFalse(self.car.archived)

    def test_staff_can_archive(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("vehicle_archive", args=[self.car.pk]))
        self.car.refresh_from_db()
        self.assertTrue(self.car.archived)

    def test_non_staff_cannot_sell(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("vehicle_sell", args=[self.car.pk]))
        self.assertEqual(resp.status_code, 403)


class DashboardTests(TestCase):
    def test_stock_value_counts_only_available_cars(self):
        first = make_car("AA1", "1000")
        make_car("BB2", "2000")
        make_car("CC3", "9000", status=Vehicle.Status.SOLD, sale_price=Decimal("9500"))
        Expense.objects.create(vehicle=first, description="Valet", amount=Decimal("100"))
        user = get_user_model().objects.create_user("u", password="pass-12345")
        self.client.force_login(user)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.context["stock_value"], Decimal("3100"))
        self.assertEqual(resp.context["profit"], Decimal("500"))
class DaysInStockTests(TestCase):
    def test_sold_car_counts_days_from_purchase_to_sale(self):
        car = make_car(status=Vehicle.Status.SOLD, sale_price=Decimal("6000"),
                       sale_date=date(2025, 1, 31))
        self.assertEqual(car.days_in_stock, 30)