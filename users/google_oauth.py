import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.auth import login
from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

class GoogleLoginAPIView(APIView):
    def post(self, request):

        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )


        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }

        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return Response(
                {'error': 'Invalid code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = response.json().get('access_token')


        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            return Response(
                {'error': 'Failed to get user info'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_data = userinfo_response.json()
        email = user_data.get('email')
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')


        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'registration_source': 'google',
                'is_active': True,
            }
        )


        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.registration_source = 'google'
            user.is_active = True
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)