from django.contrib import admin
from .models import FileUpload, userProfile, clients, products,services, divisionCosto, departamentoCosto, categoriaCosto
# Register your models here.

admin.site.register(FileUpload)
admin.site.register(userProfile)
admin.site.register(clients)
admin.site.register(products)
admin.site.register(services)
admin.site.register(divisionCosto)
admin.site.register(departamentoCosto)
admin.site.register(categoriaCosto)