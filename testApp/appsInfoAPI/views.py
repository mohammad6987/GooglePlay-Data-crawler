from google_play_scraper import search
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .models import AppInfo
from .serializor import smallSerial,UpdateAppSerializor,smallerApp
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

@csrf_exempt
@api_view(['GET']) 
def list_apps(request):
        """
        Retrieve a list of apps with all of thier fields.
        you don't have to enter anything to request body or header.
        """
        if request.method != 'GET':
              return Response({'error': 'METHOD NOT ALLOWED'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        appsList = AppInfo.objects.all()
        serializer = UpdateAppSerializor(appsList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
@extend_schema(
    request={
        'application/json': smallerApp
    }
) 
@csrf_exempt
@api_view(['GET'])     
def get_by_name(request, appName):
        """"
        get info of a specific app if it's in the database.
        your request body must contain a json tag by name 'app_name' to work properly.
        Request Body:
        - app_name (string): The name of the app. (required)
        - app_id (string): The unique ID of the app. (required)
        """
        if request.method != 'GET':
             return Response({'error': 'METHOD NOT ALLOWED'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        try:
            obj = AppInfo.objects.get(app_name = appName)
            serializer = UpdateAppSerializor(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AppInfo.DoesNotExist:
            return Response({'error': 'App not found'}, status=status.HTTP_404_NOT_FOUND)
@extend_schema(
    request={
        'application/json': UpdateAppSerializor
    }
) 
@csrf_exempt
@api_view(['POST'])      
def create_app(request):
        """
        your request body must contain a json tag by name 'app_name' to work properly.
        the program searchs for the app name with most familarity to the name of app you send in you request.
        at first only app name and app id are insterd in the databse and after at most 1 hour , the info about this 
        app will be updated. also you can manually update values in update api.
        """
        if request.method != 'POST':
             return Response({'error': 'METHOD NOT ALLOWED'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        appName = request.data.get("app_name")
        appID, appName = is_app_available(appName)
        if AppInfo.objects.filter(app_id=appID).exists():
            return Response({'error': 'App already exists in the list!'}, status=status.HTTP_409_CONFLICT)
        
        if appID:    
            applet = AppInfo(app_id=appID, app_name=appName , min_installs = 0 , score = 0 ,ratings = 0 , reviews_count =0
                             ,updated = 0 ,  version = '1.0.0' ,ad_supported = False )
            applet.save()
            return Response({'message': f'App with id:{appID} added to list. Please wait unil next crawl or update data manually.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'There is no app with this name!'}, status=status.HTTP_404_NOT_FOUND)
@extend_schema(
    request={
        'application/json': smallSerial
    }
) 
@csrf_exempt
@api_view(['DELETE'])      
def remove_app(request):
        """"
        for this api , you must use 'app_id' to avoid conflict between apps,
        use 'app_id' as a json tag to remove an app form database. the removed app will not be crawled in the future.
        """
        if request.method != 'DELETE':
             return Response({'error': 'METHOD NOT ALLOWED'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        appID = request.data.get('app_id')
        if not appID:
            return Response({'error': 'App ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            app_to_delete = AppInfo.objects.get(app_id=appID)
            app_to_delete.delete()
            return Response({'message': f'App with id:{appID} has been removed.'}, status=status.HTTP_200_OK)
        except AppInfo.DoesNotExist:
            return Response({'error': 'App not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(
    request={
        'application/json': UpdateAppSerializor
    }
)        
@csrf_exempt
@api_view(['PUT'])    
def update_app(request):
        """
        you can update fields of an already registerd app with this api.\n
        this api is based on 'app_id' and find the app by this field so it can't be alterd.\n
        but other fields can be altered to desired values.\n
        you don't have to write every field , the fields that aren't present in the json tags
        will keep thier old values.\n
        the body can have these tags:\n
            app_id => used to find the app\n
            app_name => a string\n
            min_installs => a big integer\n
            score => a float between 0 and 5\n
            ratings => count of people who rated this app\n
            reviews_count => count of people who write a review for this app\n
            updated => count of people who updated this app\n
            version => it is obvoius\n
            ad_supported => the app annoys you with adds or not\n
        """
        if request.method != 'PUT':
             return Response({'error': 'METHOD NOT ALLOWED'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
        
        appID = data.get('app_id')

        if not appID:
            return JsonResponse({'error': 'App ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = AppInfo.objects.get(app_id=appID)
        except AppInfo.DoesNotExist:
            return JsonResponse({'error': 'No app found with the given ID.'}, status=status.HTTP_404_NOT_FOUND)
        try:
        # Update fields with data from request body
            obj.app_name = data.get('app_name', obj.app_name)
            obj.min_installs = data.get('min_installs', obj.min_installs)
            obj.score = data.get('score', obj.score)
            obj.ratings = data.get('ratings', obj.ratings)
            obj.reviews_count = data.get('reviewscount', obj.reviews_count)
            obj.updated = data.get('updated', obj.updated)
            obj.version = data.get('version', obj.version)
            obj.ad_supported = data.get('ad_supported', obj.ad_supported)
            obj.save()
            return JsonResponse({'message': 'App information updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def is_app_available(app_name):
    try:
        results = search(
            app_name,
            lang='en',
            country='us',
            n_hits=5,
        )
        for app in results:
            if app_name.lower() in app['title'].lower():
                return (app['appId'],app['title'])
        
        print(f"App '{app_name}' is not available on Google Play Store.")
        return (None,None)
    except Exception as e:
        print(f"Error occurred: {e}")
        return (None,None)

    

