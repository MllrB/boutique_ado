import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=60, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    street_address1 = models.CharField(max_length=180, null=False, blank=False)
    street_address2 = models.CharField(max_length=180, null=True, blank=True)
    street_address3 = models.CharField(max_length=180, null=True, blank=True)
    town_or_city = models.CharField(max_length=180, null=True, blank=True)
    county = models.CharField(max_length=180, null=True, blank=True)
    post_code = models.CharField(max_length=8, null=True, blank=True)
    country = models.CharField(max_length=180, null=False, blank=False)
    order_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        """ Generate a random, unique order number using UUID """
        
        return uuid.uuid4().hex.upper()
    
    def update_total(self):
        """
        Update grandtotal each time a line item is added
        accounting for delivery costs
        """

        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0
        
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Overide the original save method to set the order number
        if it doesn't already exist.
        """

        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.order_number
    


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Overide the original save method to set the lineitem total
        and updat the order total.
        """

        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU: {self.product.sku} in Order No. {self.order.order_number}'
    