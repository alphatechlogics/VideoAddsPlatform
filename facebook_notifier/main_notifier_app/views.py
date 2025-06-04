from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import FacebookNotification, Video, VideoCategory
import re
from django.http import JsonResponse
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.utils import timezone
from urllib.parse import urlparse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# FastAPI endpoint base URL
FASTAPI_BASE_URL = "http://localhost:8000"  # Adjust port if needed

@csrf_exempt  # Disable CSRF for API
def all_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user = authenticate(username=username, password=password)
            if user and user.is_staff:  # Only allow admin users
                notifications = FacebookNotification.objects.all().values("id", "user__username", "video_id")
                return JsonResponse({"status": "success", "data": list(notifications)}, safe=False)
            else:
                return JsonResponse({"status": "error", "message": "Invalid credentials or not an admin"}, status=403)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST requests allowed"}, status=405)




@csrf_exempt  # Disable CSRF for API calls
def update_last_checked(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            video_id = data.get("video_id")  # Get video_id from request

            # Authenticate the user
            user = authenticate(username=username, password=password)
            if not user or not user.is_staff:
                return JsonResponse({"status": "error", "message": "Invalid credentials or not an admin"}, status=403)

            # Find the record by video_id
            notification = FacebookNotification.objects.filter(video_id=video_id).first()
            if not notification:
                return JsonResponse({"status": "error", "message": "Video ID not found"}, status=404)

            # Update last_checked timestamp
            notification.last_checked = timezone.now()
            notification.save()

            return JsonResponse({"status": "success", "message": f"Updated last_checked for {video_id}"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST requests allowed"}, status=405)

def is_facebook_page(url):
    # Regular expression to match Facebook page URLs
    facebook_page_pattern = re.compile(
        r"^(?:https?:\/\/)?(?:www\.)?facebook\.com\/([a-zA-Z0-9.]+)\/?$"
    )

    # Check if the URL matches the Facebook page pattern
    if facebook_page_pattern.match(url):
        # Parse the URL to extract the domain and path
        parsed_url = urlparse(url)
        
        # Check if the domain is facebook.com and ensure the path is only a single segment (not empty)
        if parsed_url.netloc == "www.facebook.com" or parsed_url.netloc == "facebook.com":
            if len(parsed_url.path.strip('/').split('/')) == 1:  # Ensure it's only one segment (i.e., no extra paths)
                return True  # It's a valid Facebook page URL
            else:
                return False  # It's an invalid Facebook URL with extra paths
        else:
            return False  # It's not a valid Facebook URL

    return False  # If the URL doesn't match the Facebook page pattern

@login_required()
def home(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_link', '').strip()
        video_url=video_url.lower()
        print(video_url)
        # Validate the URL
        if not is_facebook_page(video_url):
            messages.error(request, 'Please enter a valid Facebook Page URL.')
            return redirect('home')
        
        # Save the URL and user to the database
        try:
            FacebookNotification.objects.create(
                user=request.user,  # Add the logged-in user
                video_id=video_url,  # Save the full URL (or extract video ID if needed)
            )
            messages.success(request, 'Facebook Page URL added successfully!')
        except Exception as e:
            print("Error")
            messages.error(request, f'An error occurred: {str(e)}')

        return redirect('home')

    return render(request, 'home.html')

@login_required
def my_links(request):
    # Fetch links submitted by the logged-in user
    user_links = FacebookNotification.objects.filter(user=request.user)

    return render(request, 'my_links.html', {'user_links': user_links})

@login_required()
def delete_link(request, link_id):
    # Fetch the link or return 404 if not found
    link = get_object_or_404(FacebookNotification, id=link_id, user=request.user)
    
    # Delete the link
    link.delete()
    messages.success(request, 'Link deleted successfully!')
    
    return redirect('my_links')

@api_view(['GET'])
def get_categories(request):
    """
    Get video categories from FastAPI endpoint
    """
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/api/categories")
        if response.status_code == 200:
            data = response.json()
            return Response({
                'status': 'success',
                'data': [{'id': cat, 'name': cat} for cat in data.get('categories', [])]
            })
        else:
            return Response({
                'status': 'error',
                'message': f'FastAPI returned status code {response.status_code}'
            }, status=response.status_code)
    except requests.RequestException as e:
        return Response({
            'status': 'error',
            'message': f'Failed to connect to FastAPI: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_unlisted(request):
    """
    Search unlisted videos from FastAPI endpoint
    """
    try:
        print("\n=== API Search Debug Info ===")
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        
        if not request.user.is_authenticated:
            print("User is not authenticated")
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Get search parameters
        keyword = request.GET.get('keyword', '').strip()
        channel_id = request.GET.get('channel_id', '').strip()
        category = request.GET.get('category', '').strip()

        print(f"Search parameters - Keyword: '{keyword}', Channel: '{channel_id}', Category: '{category}'")

        # Prepare query parameters for FastAPI request
        params = {
            'keyword': keyword,
            'channel_id': channel_id,
            'category': category
        }
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        
        # Make request to FastAPI endpoint
        response = requests.get(f"{FASTAPI_BASE_URL}/api/search-unlisted", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Received {len(data.get('videos', []))} videos from FastAPI")
            print("=== End API Search Debug Info ===\n")
            # Reformat the response to match expected structure
            return Response({
                'status': 'success',
                'data': data.get('videos', [])
            })
        else:
            print(f"FastAPI returned status code {response.status_code}")
            print("=== End API Search Debug Info ===\n")
            return Response({
                'status': 'error',
                'message': f'FastAPI returned status code {response.status_code}'
            }, status=response.status_code)

    except requests.RequestException as e:
        print(f"API Search error: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Failed to connect to FastAPI: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def format_number(number):
    """Format large numbers to K, M, B format"""
    if not isinstance(number, (int, float)):
        return '0'
    
    number = float(number)
    if number >= 1000000000:
        return f'{number/1000000000:.1f}B'
    if number >= 1000000:
        return f'{number/1000000:.1f}M'
    if number >= 1000:
        return f'{number/1000:.1f}K'
    return str(int(number))

@login_required
def search_videos(request):
    """
    Search videos with session authentication
    """
    try:
        keyword = request.GET.get('keyword', '').strip()
        channel_id = request.GET.get('channel_id', '').strip()
        category = request.GET.get('category', '').strip()
        
        # Prepare context with search parameters
        context = {
            'search_params': {
                'keyword': keyword,
                'channel_id': channel_id,
                'category': category,
            }
        }
        
        # Get categories from FastAPI
        try:
            categories_response = requests.get(f"{FASTAPI_BASE_URL}/api/categories")
            if categories_response.status_code == 200:
                categories_data = categories_response.json()
                context['categories'] = [(cat, cat) for cat in categories_data.get('categories', [])]
            else:
                messages.error(request, 'Failed to fetch categories')
                context['categories'] = []
        except requests.RequestException as e:
            messages.error(request, f'Failed to connect to categories API: {str(e)}')
            context['categories'] = []

        # If search parameters are provided, fetch videos
        if keyword or channel_id or category:
            try:
                # Prepare query parameters
                params = {k: v for k, v in context['search_params'].items() if v}
                
                # Make request to FastAPI search endpoint
                response = requests.get(f"{FASTAPI_BASE_URL}/api/search-unlisted", params=params)
                if response.status_code == 200:
                    data = response.json()
                    videos_list = data.get('videos', [])
                    
                    # Set up pagination
                    page = request.GET.get('page', 1)
                    paginator = Paginator(videos_list, 9)  # Show 9 videos per page (3x3 grid)
                    
                    try:
                        videos = paginator.page(page)
                    except PageNotAnInteger:
                        videos = paginator.page(1)
                    except EmptyPage:
                        videos = paginator.page(paginator.num_pages)
                    
                    context['videos'] = videos
                    print(f"Received {len(videos_list)} videos from FastAPI, showing page {page}")
                else:
                    error_msg = f'Search API returned status code {response.status_code}'
                    print(error_msg)
                    messages.error(request, error_msg)
                    context['error_message'] = error_msg
            except requests.RequestException as e:
                error_msg = f'Failed to connect to search API: {str(e)}'
                print(error_msg)
                messages.error(request, error_msg)
                context['error_message'] = error_msg
        
        return render(request, 'search.html', context)

    except Exception as e:
        messages.error(request, f'An error occurred while searching: {str(e)}')
        return redirect('home')