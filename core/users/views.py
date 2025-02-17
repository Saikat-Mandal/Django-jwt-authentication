from django.shortcuts import render
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt , datetime

class Register(APIView):
    def post(self , request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
class Login(APIView):
    def post(self , request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email = email).first()

        if user is None:
            raise AuthenticationFailed('User not found')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        
        payload = {
            'id' : user.id ,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat' : datetime.datetime.utcnow() 
        }

        token = jwt.encode(payload, "mylittlesecret" , algorithm="HS256" )

        response = Response()

        response.set_cookie(key='jwt' , value=token , httponly=True)

        response.data = {
            'jwt' : token
        }

        return response


class UserView(APIView):
    def get(self,request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("no token found")
        try:
          
           payload = jwt.decode(token, "mylittlesecret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
           raise AuthenticationFailed("unauthenticated")
        user = User.objects.filter(id = payload['id']).first()

        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class LogoutView(APIView):
    def get(self , request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message':'success'
        }  
        return response  