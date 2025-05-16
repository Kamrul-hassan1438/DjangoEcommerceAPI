from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from Core.models import Order, Product
from .serializers import OrderCreateSerializer, OrderDetailSerializer, ProductSerializer
from Core.permissions import IsCustomer, IsAdminOrCustomer
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated, IsCustomer,IsAdminOrCustomer]



class CustomerOrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrCustomer]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'is_paid']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            queryset = Order.objects.all()
        elif user.role == 'customer':
            queryset = Order.objects.filter(customer=user)
        else:
            queryset = Order.objects.none()

        # Optimize database query with select_related and prefetch_related
        queryset = queryset.select_related('customer').prefetch_related('items__product__category')

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                # Validate date format (e.g., YYYY-MM-DD)
                timezone.datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(order_date__gte=start_date)  # Changed from created_at to order_date
            except ValueError:
                # Handle invalid date format (optional: raise error or ignore)
                pass

        if end_date:
            try:
                # Validate date format
                timezone.datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(order_date__lte=end_date)  # Changed from created_at to order_date
            except ValueError:
                # Handle invalid date format
                pass

        return queryset.order_by('-order_date')  # Changed from




class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []  
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.all().select_related('category', 'seller')

        # Filter by category_name (optional)
        category_name = self.request.query_params.get('category_name')
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        # Filter by stock availability (exclude out-of-stock products)
        stock_available = self.request.query_params.get('stock_available', 'true').lower()
        if stock_available == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)

        return queryset



