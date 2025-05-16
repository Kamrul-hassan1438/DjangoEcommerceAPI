from rest_framework import serializers
from Core.models import User, SellerProfile,Category
from django.db import transaction

class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'contact_number', 'address']
        read_only_fields = ['created_at', 'updated_at']

class UserListSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='seller_profile.shop_name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'shop_name']

class UserDetailSerializer(serializers.ModelSerializer):
    seller_profile = SellerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_staff', 'is_superuser', 'is_active', 'seller_profile']

class UserUpdateSerializer(serializers.ModelSerializer):
    seller_profile = SellerProfileSerializer(required=False, allow_null=True)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'seller_profile']
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'is_active']

    def validate_email(self, value):
        # Check for duplicate email, excluding the current user
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_role(self, value):
        # Only allow valid roles
        if value not in dict(User.ROLE_CHOICES).keys():
            raise serializers.ValidationError("Invalid role.")
        return value

    def validate_seller_profile(self, value):
        role = self.initial_data.get('role', self.instance.role if self.instance else None)
        if role == 'seller' and not value:
            raise serializers.ValidationError("Seller profile is required for seller role.")
        if role != 'seller' and value:
            raise serializers.ValidationError("Seller profile is only allowed for seller role.")
        return value

    def validate(self, attrs):
        seller_profile_data = attrs.get('seller_profile')
        if seller_profile_data and 'shop_name' in seller_profile_data:
            shop_name = seller_profile_data['shop_name']
            if SellerProfile.objects.exclude(user=self.instance).filter(shop_name=shop_name).exists():
                raise serializers.ValidationError({"seller_profile": {"shop_name": "This shop name is already taken."}})
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        seller_profile_data = validated_data.pop('seller_profile', None)

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.save()  
        if instance.role == 'seller' and seller_profile_data:
            seller_profile, _ = SellerProfile.objects.get_or_create(user=instance)
            seller_profile.shop_name = seller_profile_data.get('shop_name', seller_profile.shop_name)
            seller_profile.contact_number = seller_profile_data.get('contact_number', seller_profile.contact_number)
            seller_profile.address = seller_profile_data.get('address', seller_profile.address)
            seller_profile.save()
        elif instance.role != 'seller':
            # Delete SellerProfile if role is changed from seller
            SellerProfile.objects.filter(user=instance).delete()

        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value
    
    