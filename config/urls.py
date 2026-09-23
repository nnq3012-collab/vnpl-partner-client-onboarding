from django.contrib import admin
from django.urls import path

admin.site.site_header = "VNPL – Duyệt khách hàng & nhà cung cấp"
admin.site.site_title = "VNPL Onboarding"
admin.site.index_title = "Tạm thời, dùng đến khi Polaris CRM go-live"

urlpatterns = [path("", admin.site.urls)]
