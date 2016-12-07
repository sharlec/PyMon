from django.contrib import admin
from monitcollector.models import *

admin.site.register([Network,Server,Service,Process,System,Platform])