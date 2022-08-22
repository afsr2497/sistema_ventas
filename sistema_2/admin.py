from django.contrib import admin
from .models import FileUpload, userProfile, clients, products,services
# Register your models here.

admin.site.register(FileUpload)
admin.site.register(userProfile)
admin.site.register(clients)
admin.site.register(products)
admin.site.register(services)