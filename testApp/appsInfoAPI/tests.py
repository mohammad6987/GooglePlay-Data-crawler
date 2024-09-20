from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import AppInfo
import json
from django.test import Client
class AppInfoTests(TestCase):
    def setUp(self):
        self.create_url = '/apps/create'  
        self.update_url = '/apps/update'
        self.delete_url = '/apps/delete'
        self.get_by_name_url = '/apps/getApp/{appName}'
        self.list_apps_url = '/apps'
        self.client = Client()
        self.app_data = {
            'app_id': 'org.telegram.messenger',
            'app_name': 'Telegram'
        }
        
    def test_list_apps(self):
        response = self.client.get('/apps',{})
        self.assertEqual(response.status_code , status.HTTP_200_OK)
        self.assertIsNotNone(response.content.decode('utf-8'))
    

    def incorrect_method_list_apps(self):
        response = self.client.post('/apps',{})
        self.assertEqual(response.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put('/apps',{})
        self.assertEqual(response.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete('/apps',{})
        self.assertEqual(response.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_get_by_name(self):
        applet = AppInfo(app_id='org.telegram.messenger', app_name='Telegram' , min_installs = 0 , score = 0 ,ratings = 0 , reviews_count =0
                             ,updated = 0 ,  version = '1.0.0' ,ad_supported = False )
        applet.save()
        response = self.client.get('/apps/getApp/Telegram')
        self.assertEqual(response.status_code , status.HTTP_200_OK)
        json_response = response.json()
        self.assertIn('app_id', json_response)
        self.assertIn('app_name', json_response)
        self.assertIn('min_installs', json_response)
        self.assertIn('score', json_response)
        self.assertIn('ratings', json_response)
        self.assertIn('reviews_count', json_response)
        self.assertIn('updated', json_response)
        self.assertIn('version', json_response)
        self.assertIn('ad_supported', json_response)
        applet.delete()

    def invalid_get_by_name(self):
        response = self.client.get('/apps/getApp/xxxxxxxxx')
        self.assertEqual(response.status_code , status.HTTP_404_NOT_FOUND)


    def test_create_app(self):
        data = {
            'app_name' : 'Arknights',
            'min_installs' : 1000
        }
        response = self.client.post(self.create_url , data , content_type='application/json')
        self.assertEqual(response.status_code  , status.HTTP_201_CREATED)
        self.assertTrue(AppInfo.objects.filter(app_name='Arknights').exists())
        AppInfo.objects.filter(app_name = 'Arknights').delete()


    def test_create_app_already_exists(self):
        data = {
            'app_name' : 'Instagram',
            'min_installs' : 0
        }
        response = self.client.post(self.create_url , data , content_type='application/json')
        self.assertEqual(response.status_code  , status.HTTP_201_CREATED)

    def create_non_existing_app(self):
        data = {
            'app_name' : ';;;;;;;;;;;;;;;;'
        }
        response = self.client.post(self.create_url , data , content_type='application/json')
        self.assertEqual(response.status_code  , status.HTTP_404_NOT_FOUND)


    def test_remove_app(self):
        data = {
            'app_name' : 'Arknights'
        }
        response = self.client.post(self.create_url , data , content_type='application/json')
        app_instance = AppInfo.objects.filter(app_name='Arknights').first()
        if app_instance:
            app_id = app_instance.app_id
            data = {
                'app_id' : app_id
            }
            response = self.client.delete(self.delete_url , data , content_type='application/json')
            self.assertEqual(response.status_code , status.HTTP_200_OK)

    def test_remove_app_not_found(self):
        data = {
                'app_id' : 'jvfdbjbtngjhlr'
            }
        response = self.client.delete(self.delete_url , data , content_type='application/json')
        self.assertEqual(response.status_code , status.HTTP_404_NOT_FOUND)

    def no_appID_delete_request(self):
        data = {
                'app_name' : 'Facebook'
            }
        response = self.client.delete(self.delete_url , data , content_type='application/json')
        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(AppInfo.objects.filter(app_name = 'Facebook').first())

    def test_update_app(self):
        applet = AppInfo(app_id='org.telegram.messenger', app_name='Telegram' , min_installs = 0 , score = 0 ,ratings = 0 , reviews_count =0
                             ,updated = 0 ,  version = '1.0.0' ,ad_supported = False )
        applet.save()
        updated_data = {
            'app_id': 'org.telegram.messenger',
            'app_name': 'Updated Telegram',
            'score': 4.5
        }
        response = self.client.put(self.update_url , updated_data , content_type='application/json')
        self.assertEqual(response.status_code , status.HTTP_200_OK)
        instance = AppInfo.objects.filter(app_id = updated_data['app_id']).first()
        self.assertEqual(instance.app_name , updated_data['app_name'])
        self.assertEqual(instance.score , updated_data['score'])
        applet.delete()

    def test_invalid_json_in_update(self):
        updated_data = {
            'x': 'Updated Telegram',
            'y': 4.5
        }
        response = self.client.put(self.update_url , updated_data , content_type='application/json')
        self.assertEqual(response.json().get('error') , 'App ID is required.')


