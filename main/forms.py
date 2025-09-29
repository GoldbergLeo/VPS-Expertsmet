from django import forms
from .models import Subscription

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'blog__subscribe-input',
                'placeholder': 'Ваша почта',
                'required': 'required'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Проверим, не подписан ли уже такой email
        if Subscription.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже подписан на рассылку.")
        return email

class CalculatorForm(forms.Form):
    PROJECT_TYPE_CHOICES = [
        ('residential', 'Жилое строительство'),
        ('commercial', 'Коммерческое строительство'),
        ('industrial', 'Промышленное строительство'),
        ('infrastructure', 'Инфраструктурные объекты'),
        ('reconstruction', 'Реконструкция'),
    ]
    
    COMPLEXITY_CHOICES = [
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
    ]
    
    URGENCY_CHOICES = [
        ('standard', 'Стандартно (5-7 дней)'),
        ('expedited', 'Ускоренно (2-3 дня)'),
        ('urgent', 'Срочно (1 день)'),
    ]
    
    SERVICES_CHOICES = [
        ('design', 'Проектирование'),
        ('estimate', 'Составление сметы'),
        ('expertise', 'Экспертиза'),
        ('verification', 'Проверка сметы'),
        ('optimization', 'Оптимизация'),
        ('consultation', 'Консультации'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя',
            'required': 'required'
        }),
        label='Имя'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш email',
            'required': 'required'
        }),
        label='Email'
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш телефон'
        }),
        label='Телефон',
        required=False
    )
    
    project_type = forms.ChoiceField(
        choices=PROJECT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'project-type'
        }),
        label='Тип проекта'
    )
    
    area = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Площадь в м²',
            'id': 'area',
            'required': 'required'
        }),
        label='Площадь (м²)'
    )
    
    complexity = forms.ChoiceField(
        choices=COMPLEXITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'complexity'
        }),
        label='Сложность проекта'
    )
    
    services = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Требуемые услуги'
    )
    
    urgency = forms.ChoiceField(
        choices=URGENCY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'urgency'
        }),
        label='Срочность'
    )
    
    additional_info = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Дополнительная информация о проекте'
        }),
        label='Дополнительная информация',
        required=False
    )
    
    estimated_cost = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.HiddenInput(attrs={
            'id': 'estimated-cost'
        }),
        label='Расчетная стоимость',
        required=False
    )

class QuickContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'quick-contact-input',
            'placeholder': 'Ваше имя',
            'required': 'required'
        }),
        label='Имя'
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'quick-contact-input',
            'placeholder': 'Ваш телефон',
            'required': 'required'
        }),
        label='Телефон'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'quick-contact-textarea',
            'placeholder': 'Краткое описание вашего проекта',
            'rows': 3,
            'required': 'required'
        }),
        label='Сообщение'
    )