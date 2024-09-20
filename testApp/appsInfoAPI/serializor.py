from rest_framework import serializers
 

from .models import AppInfo,smallApp ,smallerApp

class InfoSerializor(serializers.ModelSerializer):
    app_name = serializers.CharField(required=True)
    app_id = serializers.CharField(required=True)
    class Meta:
        model = AppInfo
        fields = '__all__'

class smallSerial(serializers.ModelSerializer):
        app_id = serializers.CharField(required=True)  
        class Meta:
            model = smallApp
            fields = ['app_id']

class smallerApp(serializers.ModelSerializer):
        app_name = serializers.CharField(required=True)  
        class Meta:
            model = smallerApp
            fields = ['app_name']            

class UpdateAppSerializor(serializers.ModelSerializer):
    app_id = serializers.CharField(required=True)
    app_name = serializers.CharField(required=False)
    min_installs = serializers.IntegerField(required=False)
    score = serializers.FloatField(required=False)
    ratings = serializers.IntegerField(required=False)
    reviews_count = serializers.IntegerField(required=False)
    updated = serializers.IntegerField(required=False)
    version = serializers.CharField(required=False)
    ad_supported = serializers.BooleanField(required=False)            
    class Meta:
            model = AppInfo
            fields = '__all__'