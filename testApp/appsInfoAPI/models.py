from django.db import models

class AppInfo(models.Model):
    app_id = models.CharField(max_length=255, primary_key=True)  
    app_name = models.CharField(max_length=255)  
    min_installs = models.BigIntegerField()  
    score = models.FloatField()  
    ratings = models.BigIntegerField()  
    reviews_count = models.BigIntegerField()
    updated = models.IntegerField()  
    version = models.CharField(max_length=255) 
    ad_supported = models.BooleanField()  

    class Meta:
        db_table = 'apps_info'

class smallApp(models.Model):
   app_id = models.CharField(max_length=255, primary_key=True)  


class smallerApp(models.Model):
    app_name = models.CharField(max_length=255)  
   
    

