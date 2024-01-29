from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Restaurant(models.Model):
    restaurantName_ko = models.CharField(max_length=100)
    restaurantName_en = models.CharField(max_length=100)
    location = models.CharField(max_length=100) #Campus Town, Triple Street or Others(해경...?)
    address = models.CharField(max_length=500)
    direction_link = models.CharField(max_length=500)
    
    def __str__(self):
        return self.restaurantName_ko


class Menu(models.Model):
    restaurantName_ko = models.CharField(max_length=100)
    restaurantName_en = models.CharField(max_length=100)
    location = models.CharField(max_length=100) #Campus Town, Triple Street or Others(해경...?)
    menuName_ko = models.CharField(max_length=100) # 메뉴의 이름
    menuName_en1 = models.CharField(max_length=100, default="")
    menuName_en2 = models.CharField(max_length=100, default="", null=True, blank=True)
    menuType_big = models.CharField(max_length=100, default="NA") # 메뉴 대분류
    menuType = models.CharField(max_length=100) # 메뉴의 분류. 김밥/비빔밥/돈까스 이렇게..s
    # menuTypeCode = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)
    price = models.IntegerField(default=0, null=True, blank=True)
    salty = models.FloatField(null=True, blank=True, default=0)
    sweet = models.FloatField(null=True, blank=True, default=0)
    spicy = models.FloatField(null=True, blank=True, default=0)
    category = models.CharField(max_length = 100, default="No category yet", blank=True)
    main_ingredient = models.CharField(max_length=100, default="")
    vegetarian = models.IntegerField(default=0)
    islam = models.IntegerField(default=0)
    hindu = models.IntegerField(default=0)
    rating = models.FloatField(null=True, default=0)
    food_id = models.IntegerField(default=0, null=True)
    
    def __str__(self):
        return self.menuName_ko

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.TextField(default="No_username", blank=True)
    liked_food = models.ManyToManyField(Menu, related_name='liked_food', blank=True)
    disliked_food = models.ManyToManyField(Menu, related_name='disliked_food', blank=True)
    salty = models.FloatField(default=0)
    sweet = models.FloatField(default=0)
    spicy = models.FloatField(default=0)
    Asian = models.FloatField(default=0)
    Chinese= models.FloatField(default=0)
    Korean = models.FloatField(default=0)
    Japanese = models.FloatField(default=0)
    Western = models.FloatField(default=0)
    max_spicy = models.IntegerField(default=5)
    vegetarian = models.IntegerField(default=0) # 채식주의자라면 1, 아니라면 0
    islam = models.IntegerField(default=0) # 이슬람이면 1, 아니면 0
    hindu = models.IntegerField(default=0) # 힌두인이면 1, 아니면 0
    
    def __str__(self):
        return self.user.username

class Statistics(models.Model):
    number_of_recommendations = models.IntegerField()