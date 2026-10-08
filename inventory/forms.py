from django import forms

from .models import Expense, Vehicle

DATE = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["registration", "make", "model", "year", "colour",
                  "mileage", "purchase_price", "purchase_date"]
        widgets = {"purchase_date": DATE}


class SaleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["sale_price", "sale_date"]
        widgets = {"sale_date": DATE}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sale_price"].required = True
        self.fields["sale_date"].required = True

    def clean_sale_date(self):
        date = self.cleaned_data["sale_date"]
        if date < self.instance.purchase_date:
            raise forms.ValidationError("Sale date cannot be before the purchase date.")
        return date

    def save(self, commit=True):
        self.instance.status = Vehicle.Status.SOLD
        return super().save(commit)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["description", "amount", "date"]
        widgets = {"date": DATE}
