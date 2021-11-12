from django.contrib import admin
from boards.models import Board, Section, Sticker
# Register your models here.


class BoardAdmin(admin.ModelAdmin):
    pass


class SectionAdmin(admin.ModelAdmin):
    pass


class StickerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Board, BoardAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Sticker, StickerAdmin)
