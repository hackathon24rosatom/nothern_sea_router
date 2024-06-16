from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name=_('Ник')
    )
    first_name = models.CharField(
        max_length=30,
        validators=[RegexValidator(
            regex=r'^[\w -]*$',
            message=_('Недопустимые символы в имени'),
            code='invalid_firstname'
        )],
        verbose_name=_('Имя')
    )
    last_name = models.CharField(
        max_length=30,
        validators=[RegexValidator(
            regex=r'^[\w -]*$',
            message=_('Недопустимые символы в имени'),
            code='invalid_lastname'
        )],
        verbose_name=_('Фамилия')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('Эл.почта')
    )

    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name'
    ]
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.get_username()


class Company(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name=_('Название')
    )
    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ('name',)


class Staff(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='staff',
        verbose_name=_('Сотрудник')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company',
        verbose_name=_('Компания')
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='Guarantee of unique place of work',
                fields=['user', 'company'],
            ),
            # models.CheckConstraint(
            #     name='Prevention of self subscription',
            #     check=~models.Q(user=models.F('author'))
            # )
        ]
        verbose_name = 'Персонал компании'
        verbose_name_plural = 'Персонал компании'
        ordering = ('company', 'user')

    def __str__(self):
        return f'{self.user} является сотрудником {self.company}'
