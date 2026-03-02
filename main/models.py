import os
import uuid
from django.db import models
from main.base_model import BaseModel
from main.storages import PrivateStorage, PublicStorage
from django_minio_backend import iso_date_prefix
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from ckeditor.fields import RichTextField
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    file = models.FileField(
        upload_to=iso_date_prefix,
        storage=PublicStorage(),
    )

    is_public = models.BooleanField(default=True)
    filesize = models.BigIntegerField(null=True, blank=True)
    original_name = models.CharField(max_length=255, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and not self.filesize:
            self.filesize = self.file.size
        if self.file and not self.original_name:
            self.original_name = self.file.name.split('/')[-1]

        if self.file:
            if self.is_public:
                self.file.storage = PublicStorage()
            else:
                self.file.storage = PrivateStorage()

            try:
                img = Image.open(self.file)
                if img.format.lower() in ['jpeg', 'jpg', 'png']:
                    output = BytesIO()
                    img = img.convert('RGB')
                    img.save(output, format='WEBP', quality=80)
                    output.seek(0)
                    name, _ = os.path.splitext(self.file.name)
                    self.file.save(f"{name}.webp", ContentFile(output.read()), save=False)
            except Exception:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_name}"

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-created_at']


class Category(BaseModel):
    name = models.CharField('Наименование', max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['created_at']


class ProductImage(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='attachments')
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} - {self.attachment.original_name}"


class Tag(BaseModel):
    name = models.CharField('Наименование', max_length=255, unique=True)

    class Meta():
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['created_at']

    def __str__(self):
        return self.name

class StickerType(BaseModel):
    name = models.CharField('Наименование', max_length=255)
    color = models.CharField('Цвет', max_length=255)

    class Meta():
        verbose_name = 'Тип стикера'
        verbose_name_plural = 'Тип стикеров'
        ordering = ['created_at']

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField('Наименование', max_length=255)
    articul = models.CharField('Артикул', null=True, blank=True, max_length=255)
    short_description = models.CharField('Короткое описание', max_length=255)
    price = models.CharField('Стоимость', max_length=100)
    username_tg = models.CharField('Телеграм логин', max_length=255)
    preview_fk = models.ForeignKey(
        Attachment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Превью'
    )
    content = RichTextField(verbose_name='Контент')
    sticker_type_fk =models.ForeignKey(StickerType, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField('Телефон', null=True, blank=True, max_length=255)
    categories = models.ManyToManyField(Category, blank=True, verbose_name='Категории')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Тэги')
    order = models.IntegerField('Сортировка', default=0)

    def get_tags(self):
        return self.tags.all()

    class Meta():
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['created_at']

    def __str__(self):
        return self.name


class TgUserAllow(BaseModel):
    telegram_id = models.BigIntegerField('telegram_id', default=0)

    class Meta():
        verbose_name = 'Разрешенный тг-юзер'
        verbose_name_plural = 'Разрешенные тг-юзеры'
        ordering = ['created_at']

    def __str__(self):
        return str(self.telegram_id)
