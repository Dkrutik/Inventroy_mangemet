from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Item
from .serializers import ItemSerializer
import redis
import time
# Initialize Redis
r = redis.Redis(host='localhost', port=6379, db=0)

class ItemListCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        # Check cache first
        start_time = time.time()
        cached_item = r.get(f'item_{item_id}')
        redis_get_time = time.time() - start_time
        if cached_item:
            print(f"Redis GET took: {redis_get_time:.6f} seconds")
            return Response(eval(cached_item), status=status.HTTP_200_OK)
        try:
            item = Item.objects.get(pk=item_id)
            serializer = ItemSerializer(item)
            r.set(f'item_{item_id}', str(serializer.data))  # Cache the data
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, item_id):
        try:
            item = Item.objects.get(pk=item_id)
            serializer = ItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, item_id):
        try:
            item = Item.objects.get(pk=item_id)
            item.delete()
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
