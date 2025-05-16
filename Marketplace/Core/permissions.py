from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff and request.user.role == 'admin'

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'


class IsProductOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            (request.user.role == 'admin' or
             (request.user.role == 'seller' and obj.seller == request.user))
        )


class IsAdminOrSeller(BasePermission):
    def has_permission(self, request, view):
        # Allow authenticated Admins or Sellers to access the endpoint
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.role == 'seller')

    def has_object_permission(self, request, view, obj):
        # Admins can update any product
        if request.user.role == 'admin':
            return True
        # Sellers can only update their own products
        if request.user.role == 'seller':
            return obj.seller == request.user
        return False

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'


class IsAdminOrCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'customer']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'customer':
            return obj.customer == request.user
        return False
    


class IsAdminCustomerOrSellerForOrder(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'customer', 'seller']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'customer':
            return obj.customer == request.user
        if request.user.role == 'seller':
            return obj.items.filter(product__seller=request.user).exists()
        return False



class IsAdminOrSellerForOrderStatus(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f"User Role: {request.user.role}, Order ID: {obj.id}")
        if request.user.role == 'admin':
            return True
        if request.user.role == 'seller':
            return obj.items.filter(product__seller=request.user).exists()
        return False

