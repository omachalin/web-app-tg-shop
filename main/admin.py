from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Product, Attachment, Category, ProductImage, TgUserAllow, Tag, StickerType
import django.db.models as models
from django.urls import path
from django.http import HttpResponseRedirect
import csv, io


@admin.register(StickerType)
class StickerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('preview_image', 'order', 'attachment')
    readonly_fields = ('preview_image',)
    autocomplete_fields = ['attachment']

    def preview_image(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.pk or not obj.attachment or not obj.attachment.file:
            return "—"

        url = obj.attachment.file.url
        if url.lower().endswith(('.mp4', '.webm')):
            return mark_safe("""
                <div style="height:120px; width:160px; background:#333; color:#fff;
                            display:flex; align-items:center; justify-content:center;
                            border-radius:8px;">
                    VIDEO
                </div>
                """)


        return format_html(
            '<img src="{}" style="height:120px;object-fit:cover;border-radius:8px;">',
            url
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'short_description', 'price', 'username_tg', 'order', 'created_at')
    search_fields = ('name', 'username_tg', 'phone')
    filter_horizontal = ('categories', 'tags',)
    autocomplete_fields = ('preview_fk', 'sticker_type_fk',)
    change_list_template = "admin/main/product/change_list.html"

    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            return self.import_csv(request)
        return super().changelist_view(request, extra_context)

    def import_csv(self, request, queryset=None):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            file_bytes = request.FILES['csv_file'].read()
            try:
                content = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                content = file_bytes.decode('cp1251')

            reader = csv.DictReader(io.StringIO(content), delimiter=';')

            created_count = 0
            updated_count = 0

            for row in reader:
                articul = row.get('articul', '').strip()
                name = row.get('name', '').strip()
                short_description = row.get('short_description', '').strip()
                username_tg = row.get('username_tg', '').strip()
                phone = row.get('phone', '').strip()
                price = row.get('price', '').strip()
                content_field = row.get('content', '').strip()
                categories_csv = row.get('categories', '').strip()
                tags_csv = row.get('tags', '').strip()
                sticker = row.get('sticker', '').strip()
                order = row.get('order', '').strip()

                product, created = Product.objects.update_or_create(
                    articul=articul or None,
                    defaults={
                        'name': name,
                        'short_description': short_description,
                        'price': price,
                        'username_tg': username_tg,
                        'phone': phone,
                        'content': content_field,
                        'sticker': sticker,
                        'order': int(order),
                    }
                )

                created_count += int(created)
                updated_count += int(not created)

                product.categories.clear()
                for cat_name in categories_csv.split(','):
                    cat_name = cat_name.strip()
                    if cat_name:
                        cat, _ = Category.objects.get_or_create(
                            name__iexact=cat_name,
                            defaults={'name': cat_name}
                        )
                        product.categories.add(cat)

                product.tags.clear()
                for tag_name in tags_csv.split(','):
                    tag_name = tag_name.strip()
                    if tag_name:
                        tag, _ = Tag.objects.get_or_create(
                            name__iexact=tag_name,
                            defaults={'name': tag_name}
                        )
                        product.tags.add(tag)

            messages.success(request, f'Импорт завершен: создано {created_count}, обновлено {updated_count}')
            return HttpResponseRedirect(request.get_full_path())

        messages.error(request, 'Файл CSV не выбран или неверный метод запроса.')
        return HttpResponseRedirect(request.get_full_path())


    def get_fieldsets(self, request, obj=None):
        fields = [
            f.name for f in self.model._meta.fields
            if f.editable
        ] + [
            m.name for m in self.model._meta.many_to_many
        ]

        return (
            (None, {'fields': fields}),
            ('Множественная загрузка', {
                'fields': (),
                'description': mark_safe("""
                    <input type="file" name="extra_images" multiple accept="image/*,video/*"
                        style="padding:20px;border:3px dashed #666;width:auto;">
                """)
            }),
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.is_multipart = lambda *args, **kwargs: True
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        files = request.FILES.getlist('extra_images')

        if not files:
            return

        max_order = ProductImage.objects.filter(product=obj).aggregate(
            m=models.Max('order')
        )['m'] or 0

        for i, uploaded_file in enumerate(files, start=1):
            attachment = Attachment.objects.create(
                file=uploaded_file,
                original_name=uploaded_file.name,
                is_public=True
            )

            ProductImage.objects.create(
                product=obj,
                attachment=attachment,
                order=max_order + i
            )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'preview_fk', 'sticker_type_fk'
        ).prefetch_related('categories', 'attachments__attachment', 'tags')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'filesize_formatted', 'is_public', 'created_at')
    search_fields = ('original_name',)
    readonly_fields = ('filesize', 'original_name')

    def filesize_formatted(self, obj):
        if not obj.filesize:
            return "-"
        size = obj.filesize
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(TgUserAllow)
class TgUserAllowAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'updated_at', 'created_at')
    search_fields = ('telegram_id',)
