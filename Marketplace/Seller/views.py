from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Core.permissions import IsAdminOrSeller
from rest_framework.permissions import IsAuthenticated, AllowAny
from Core.permissions import IsAdmin, IsSeller, IsProductOwnerOrAdmin, IsAdminOrSeller, IsAdminCustomerOrSellerForOrder, IsAdminOrSellerForOrderStatus
from Core.models import Product, Order, OrderItem
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer, OrderDetailSerializer, SellerOrderDetailSerializer, SalesHistorySerializer, OrderStatusUpdateSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('seller', 'category').order_by('id')
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrSeller()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('seller', 'category')
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.select_related('seller', 'category')
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    lookup_url_kwarg = 'pk'

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.select_related('seller', 'category')
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    lookup_url_kwarg = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Product is deleted"}, status=status.HTTP_200_OK)

class SellerInventoryView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_queryset(self):
        user = self.request.user
        if user.role not in ['admin', 'seller']:
            return Product.objects.none()
        queryset = Product.objects.select_related('seller', 'category').filter(seller=user)
        
        # Optional sorting
        sort_by = self.request.query_params.get('sort_by', 'name')
        if sort_by in ['name', 'price', 'stock_quantity', '-name', '-price', '-stock_quantity']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('name')
        
        return queryset





class SellerInventoryView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_queryset(self):
        user = self.request.user
        if user.role not in ['admin', 'seller']:
            return Product.objects.none()

        queryset = Product.objects.select_related('seller', 'category').filter(seller=user)

        sort_by = self.request.query_params.get('sort_by', 'name')
        valid_sort_fields = ['name', 'price', 'stock_quantity', '-name', '-price', '-stock_quantity']
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('name')

        return queryset


class SellerOrderListView(generics.ListAPIView):
    serializer_class = SellerOrderDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'is_paid']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            queryset = Order.objects.all()
        elif user.role == 'seller':
            # Sellers should only see orders containing their products
            queryset = Order.objects.filter(items__product__seller=user).distinct()
        else:
            return Order.objects.none()

        queryset = queryset.select_related('customer').prefetch_related('items__product__category')

        # Optional filters
        category_id = self.request.query_params.get('category_id')
        product_id = self.request.query_params.get('product_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if category_id:
            queryset = queryset.filter(items__product__category_id=category_id)
        if product_id:
            queryset = queryset.filter(items__product_id=product_id)
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)

        return queryset.order_by('-order_date')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['seller'] = self.request.user if self.request.user.role == 'seller' else None
        return context


class SellerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = SellerOrderDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminCustomerOrSellerForOrder]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Order.objects.select_related('customer').prefetch_related('items__product__category')
        elif user.role == 'seller':
            return Order.objects.filter(items__product__seller=user).select_related('customer').prefetch_related('items__product__category')
        return Order.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['seller'] = self.request.user if self.request.user.role == 'seller' else None
        return context



class OrderStatusUpdateView(APIView):
    permission_classes = [IsAdminOrSellerForOrderStatus]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Assuming 'status' is the field you want to update
        order.status = request.data.get("status", order.status)
        order.save()

        return Response(OrderStatusUpdateSerializer(order).data, status=status.HTTP_200_OK)


class SalesHistoryView(generics.ListAPIView):
    serializer_class = SalesHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            queryset = OrderItem.objects.select_related('order', 'product__category')
        elif user.role == 'seller':
            queryset = OrderItem.objects.select_related('order', 'product__category').filter(product__seller=user)
        else:
            return OrderItem.objects.none()

        category_id = self.request.query_params.get('category_id')
        product_id = self.request.query_params.get('product_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if category_id:
            queryset = queryset.filter(product__category_id=category_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if start_date:
            queryset = queryset.filter(order__order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order__order_date__lte=end_date)

        return queryset.order_by('-order__order_date')



