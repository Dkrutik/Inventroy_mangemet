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
import logging
# Initialize Redis
logger = logging.getLogger('inventory')  # or use 'django' for general logging

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
        logger.debug(f"GET request for item {item_id}")
        start_time = time.time()
        cached_item = r.get(f'item_{item_id}')
        redis_get_time = time.time() - start_time
        if cached_item:
            print(f"Redis GET took: {redis_get_time:.6f} seconds")
            logger.info(f"Item {item_id} retrieved from cache")
            return Response(eval(cached_item), status=status.HTTP_200_OK)
        try:
            item = Item.objects.get(pk=item_id)
            serializer = ItemSerializer(item)
            logger.info(f"Item {item_id} retrieved from database")
            r.set(f'item_{item_id}', str(serializer.data))  # Cache the data
            return Response(serializer.data)
        except Item.DoesNotExist:
            logger.error(f"Item {item_id} not found")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, item_id):
        logger.debug(f"PUT request to update item {item_id}")
        try:
            item = Item.objects.get(pk=item_id)
            serializer = ItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Item {item_id} updated successfully")
                return Response(serializer.data)
            logger.error(f"Failed to update item {item_id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            logger.error(f"Item {item_id} not found for update")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, item_id):
        logger.debug(f"DELETE request for item {item_id}")
        try:
            item = Item.objects.get(pk=item_id)
            item.delete()
            logger.info(f"Item {item_id} deleted successfully")
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            logger.error(f"Item {item_id} not found for deletion")
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
