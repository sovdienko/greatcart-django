from django import forms

from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter Passowrd"})
    )
    confirmed_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Passowrd"})
    )

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Last Name"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Enter Phone Number"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email Address"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirmed_password = cleaned_data.get("confirmed_password")

        if password != confirmed_password:
            raise forms.ValidationError("Password does not match!")