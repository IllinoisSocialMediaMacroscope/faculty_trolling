from django import forms

class UserRegistrationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    username = forms.CharField(
        required = True,
        label = 'Username',
        max_length = 32
    )

    email = forms.CharField(
        required = True,
        label = 'Email',
        max_length = 32
    )

    password = forms.CharField(
        required = True,
        label = 'Password',
        max_length = 32,
        widget = forms.PasswordInput()
    )

    password2 = forms.CharField(
        required=True,
        label='Repeat Password',
        max_length=32,
        widget=forms.PasswordInput()
    )