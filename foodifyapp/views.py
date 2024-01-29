from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import get_language
from .forms import CreateUserForm
from foodifyapp.models import UserProfile, Menu, Restaurant, Statistics
from foodifyapp.food import *
import csv


# The below are codes for requesting web page from templates.
disliked_food_today = []
disliked_ingredient_today = []
disliked_restaurant_today = []

def homepage(request):
    return render(request, 'homepage.html')

def about(request):
    return redirect("/about/project")

def about_team(request):
    language = get_language()
    if language == "ko":
        return render(request, 'about_team_ko.html')
    else:
        return render(request, 'about_team_en.html')

def about_project(request):
    language = get_language()
    if language == "ko":
        return render(request, 'about_project_ko.html')
    else:
        return render(request, 'about_project_en.html')

class MyLoginView(LoginView):
    template_name = 'foodifyapp/login.html'

    
class MyLogoutView(LogoutView):
    next_page = reverse_lazy('/home')

def get_random_food_id():
    food_ids = Menu.objects.values_list('food_id', flat=True)
    return random.choice(food_ids)

def more(request):
    return render(request, 'more.html')

@login_required
def survey(request):
    food_id = get_random_food_id()
    url = "/survey/" + str(food_id)
    return redirect(url)

def user_profile_in_views(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return user_profile
     
@csrf_exempt
@login_required
def survey_food(request, survey_food_id):
    language = get_language()
    food = Menu.objects.get(food_id = survey_food_id)
    user_profile = UserProfile.objects.get(user=request.user)
    survey_count = user_profile.liked_food.count() + user_profile.disliked_food.count()
    context = {}
    context = {"food_name": food.menuName_ko, "food_description": "", "restaurant": food.restaurantName_ko, "location": food.location, "menu_type": food.menuType, "survey_count": survey_count}
    if language == "ko":
        context = {"food_name": food.menuName_ko, "food_description": "", "restaurant": food.restaurantName_ko, "location": food.location, "menu_type": food.menuType, "survey_count": survey_count}
    else:
        context = {"food_name": food.menuName_en1, "food_name_korean": food.menuName_ko, "food_description": food.menuName_en2, "restaurant": food.restaurantName_en, "location": food.location, "menu_type": food.menuType, "survey_count": survey_count}
    return render(request, 'survey.html', context)


@login_required
def survey_upload(request, survey_food_id, pref):
    food = Menu.objects.get(food_id = survey_food_id)
    user_profile = UserProfile.objects.get(user=request.user)
    user_salty = user_profile.salty
    user_sweet = user_profile.sweet
    user_spicy = user_profile.spicy
    if pref == "like":
        user_salty += 5 * food.salty
        user_sweet += 5 * food.sweet
        user_spicy += 5 * food.spicy
        user_profile.liked_food.add(food)
    elif pref == "dislike":
        user_salty -= 5 * food.salty
        user_sweet -= 5 * food.sweet
        user_spicy -= 5 * food.spicy
        user_profile.disliked_food.add(food)
    user_profile.salty = user_salty
    user_profile.sweet = user_sweet
    user_profile.spicy = user_spicy
    user_profile.save()
    survey_count = user_profile.liked_food.count() + user_profile.disliked_food.count()
    if survey_count >= 11:
        return redirect("/survey/spicy") #다음 survey (Vegeterian로 이동)
    else:
        return redirect("/survey")


def survey_info(request):
    return render(request, "survey_info.html") 

def terms(request):
    return render(request, "terms_and_conditions.html") 

def privacy(request):
    return render(request, "privacy_policy.html") 

def survey_spicy(request):
    context = {}
    return render(request, 'survey_spicy.html', context)

def survey_vegeterian(request):
    context = {}
    return render(request, 'survey_vegeterian.html', context)

def survey_islam(request):
    context = {}
    return render(request, 'survey_islam.html', context)

def survey_hindu(request):
    context = {}
    return render(request, 'survey_hindu.html', context)

def survey_spicy_max(request, max_spicy):
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.max_spicy = max_spicy
    user_profile.save()
    return redirect('/survey/vegeterian')

def survey_taboo_answer(request, taboo, answer):
    user_profile = UserProfile.objects.get(user=request.user)
    if taboo == "vegeterian":
        if answer == "yes":
            user_profile.vegetarian = 1
        elif answer == "no":
            user_profile.vegetarian = 0
        user_profile.save()
        return redirect('/survey/islam')
    elif taboo == "islam":
        if answer == "yes":
            user_profile.islam = 1
        elif answer == "no":
            user_profile.islam = 0
        user_profile.save()
        return redirect('/survey/hindu')
    elif taboo == "hindu":
        if answer == "yes":
            user_profile.hindu = 1
        elif answer == "no":
            user_profile.hindu = 0
        user_profile.save()
        return redirect('/survey/complete')

def survey_complete(request):
    context = {}
    return render(request, 'survey_complete.html', context)

def login_user(request): # 로그인 실패 시 알림 뜨는 기능을 추가해야 함.
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.liked_food.count() + user_profile.disliked_food.count() <= 10:
                    return redirect('/survey_info')
                else:
                    return redirect('/homeroom')
    else:
        form = AuthenticationForm()
        return redirect('/home')
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('/home')


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        # form = UserCreationForm(request.POST)
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()  # Save the user object
            # Create a UserProfile instance and associate it with the registered user
            user_profile = UserProfile.objects.create(
                user=user,
                username = user.username
            )
            user_profile.save()
            messages.success(request, "Register Success!")
            return redirect('/register_success')
        else:
            print("Error!") # Update 시 알림창 뜨게... 나중에 공부하도록 하자.
        
    context_data = {'form': form}
    return render(request, 'register.html', context_data)


def register_success(request):
    return render(request, 'register_success.html')
    
    
# @login_required # 로그인을 해야 방문할 수 있는 웹페이지라는 의미. 로그인을 하지 않은 채로 여기에 들어가면 로그인 페이지로 리다이렉트된다.
# def survey(request):
#     context = {}  
#     return render(request, 'survey.html', context)


@login_required
def homeroom(request):
    username = request.user.username
    context = {'username': username}  
    return render(request, 'homeroom.html', context)



@login_required
def answer(request, id): # ID는 campustown, triplestreet, anywhere 중 하나이다.
    if id == "campustown":
        place = "Campus Town"
    elif id == "triplestreet":
        place = "Triple Street"
    elif id == "anywhere":
        place = "Campus Town and Triple Street"
    got_username = request.user.username
    recommended_food = food( username = got_username) #아마도 파라미터가 더 추가되지 않을까 싶다. 이 코드 위에 model에서 가져온 사용자 데이터 및 음식 데이터를 가져와도 되고, 이 모든 과정을 food() 함수에서 처리해도 된다. 또는 food() 함수 안에 id()함수, foodList() 함수 등을 새로 만들어 그 함수 안에 기능을 집어넣는 방법도 있다. 
    context = {'id': id, 'food': recommended_food, 'place': place}  # place: 장소의 이름을 나타낸다. answer 페이지의 도입부에 사용된다.
    return render(request, 'answer.html', context)




def food_random(request): 
    user_profile = UserProfile.objects.get(user=request.user)
    food_parameter = {'recommendation_type':'random','user_profile':user_profile, "disliked_ingredient_today": disliked_ingredient_today, "disliked_food_today": disliked_food_today, "disliked_restaurant_today": disliked_restaurant_today}
    food_id = food(food_parameter)
    url = "/food_random/" + str(food_id)
    return redirect(url)
    

def food_random2(request, recommended_food_id):
    user_profile = UserProfile.objects.get(user=request.user)
    food_parameter = {'user_profile':user_profile, 'recommendation_type':'random', "disliked_ingredient_today": disliked_ingredient_today, "disliked_food_today": disliked_food_today, "disliked_restaurant_today": disliked_restaurant_today}
    context = get_food_by_id(recommended_food_id, food_parameter)
    context["like_url"] = "/more/" + str(recommended_food_id)
    context['dislike_url'] = "/dislike/random/" + str(recommended_food_id)
    return render(request, 'answer.html', context)


def recommend(request): 
    user_profile = UserProfile.objects.get(user=request.user)
    food_parameter = {'user_profile':user_profile, 'recommendation_type':'user_data', "disliked_ingredient_today": disliked_ingredient_today, "disliked_food_today": disliked_food_today, "disliked_restaurant_today": disliked_restaurant_today }
    food_id = food(food_parameter)
    if user_profile.liked_food.count() + user_profile.disliked_food.count() <= 10:
        return redirect('/survey_info')
    else:
        url = "/recommend/" + str(food_id)
        return redirect(url)


def recommend2(request, recommended_food_id):
    user_profile = UserProfile.objects.get(user=request.user)
    food_parameter = {'user_profile':user_profile, 'recommendation_type':'user_data', "disliked_ingredient_today": disliked_ingredient_today, "disliked_food_today": disliked_food_today, "disliked_restaurant_today": disliked_restaurant_today}
    context = get_food_by_id(recommended_food_id, food_parameter)
    context["like_url"] = "/more/" + str(recommended_food_id)
    context['dislike_url'] = "/dislike/recommend/" + str(recommended_food_id)
    return render(request, 'answer.html', context)

@login_required
def more(request, recommended_food_id): #지금은 user 정보 수정하고 정보 보여주는 게 같이 있는데, 이걸 분리할 필요도 있을 듯 (공유기능 등)
    food = Menu.objects.get(food_id = recommended_food_id)
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.salty += food.salty * 3
    user_profile.sweet += food.sweet * 3
    user_profile.spicy += food.spicy * 3
    food_parameter = {"recommendation_type": "None"}
    recommended_food_id = int(recommended_food_id)
    context = get_food_by_id(recommended_food_id, food_parameter)
    food = Menu.objects.get(food_id=recommended_food_id)
    language = get_language()
    if not language == "ko":
        context["restaurant"] = food.restaurantName_en + " (" + food.restaurantName_ko + ")"
    context["restaurant_searchterm"] = food.restaurantName_ko + " 송도"
    if food.restaurantName_ko in {"힘난다버거", "동대문엽기떡볶이", "본가", "유케야", "청기와감자탕"}: #송도 안에 여러 체인이 있는 경우에 대한 제외 처리 (캠타)
        context["restaurant_searchterm"] = food.restaurantName_ko + " 송도 캠퍼스타운"
    elif food.restaurantName_ko in {"노랑통닭 송도2호"}: #송도 붙이면 시청이 나오는 경우에 대한 예외 처리
        context["restaurant_searchterm"] = food.restaurantName_ko
    elif food.restaurantName_ko in {"피에프창", "올드타운 트리플스트리트점", "그믐족발 송도점", "스시로"}:
        context["restaurant_searchterm"] = "골프존파크 송도트리플스트리트점"
    # 카카오맵에 없는 식당의 경우, 개별적으로 가까운 다른 식당으로 지정함
    elif food.restaurantName_ko == "생고기대학교":
        context["restaurant_searchterm"] = "노랑통닭 송도2호" 
    elif food.restaurantName_ko == "청기와감자탕": #청기와감자탕 식당은 있지만, 송도 캠퍼스타운을 붙이면 오류가 뜸
        context["restaurant_searchterm"] = "송도과학로27번길 55 청기와감자탕 "
    elif food.restaurantName_ko == "스시로 송도점":
        context["restaurant_searchterm"] = "인천 연수구 송도과학로16번길 33-2 B"
    elif food.restaurantName_ko == "99왕돈까스 본점":
        context["restaurant_searchterm"] = "99왕돈까스 송도"
    elif food.restaurantName_ko == "동대문엽기떡볶이":
        context["restaurant_searchterm"] = "동대문엽기떡볶이 인천송도캠퍼스타운점"
    elif food.restaurantName_ko == "레드문":
        context["restaurant_searchterm"] = "레드문 송도캠퍼스타운점"
    elif food.restaurantName_ko == "마라공방 송도트리플스트리트점":
        context["restaurant_searchterm"] = "마라공방 송도점"
    elif food.restaurantName_ko == "마카오훠궈 송도 트리플스트리트 본점":
        context["restaurant_searchterm"] = "마카오훠궈 송도"
    elif food.restaurantName_ko == "문가네정육식당 인천송도점":
        context["restaurant_searchterm"] = "인더쥬"
    elif food.restaurantName_ko == "백옥양꼬치":
        context["restaurant_searchterm"] = "백옥양꼬치 송도트리플스트리트점"
    elif food.restaurantName_ko == "백채김치찌개":
        context["restaurant_searchterm"] = "백채김치찌개 송도캠퍼스타운점"
    elif food.restaurantName_ko == "빕스 프리미엄 송도점":
        context["restaurant_searchterm"] = "빕스 송도점"
    elif food.restaurantName_ko == "생고기대학교":
        context["restaurant_searchterm"] = "송도양꼬치 캠퍼스타운점"
    elif food.restaurantName_ko == "수해복마라탕":
        context["restaurant_searchterm"] = "수해복마라탕&샹궈 캠퍼스타운역"
    elif food.restaurantName_ko == "애술리퀸즈 송도트리플스트리트점":
        context["restaurant_searchterm"] = "애슐리퀸즈 송도트리플스트리트점"
    elif food.restaurantName_ko == "일품양평해장국 ":
        context["restaurant_searchterm"] = "일품양평해장국 송도캠퍼스타운점"
    elif food.restaurantName_ko == "장미꽃 떡볶이&라면 송도본점":
        context["restaurant_searchterm"] = "GS더프레시 송도캠퍼스점"
    elif food.restaurantName_ko == "저스트텐동 송도트리플스트리트점":
        context["restaurant_searchterm"] = "저스트텐동 송도트리플점"
    elif food.restaurantName_ko == "참피온 삼겹살 트리플 스트리트점":
        context["restaurant_searchterm"] = "골프존파크 송도트리플스트리트"
    elif food.restaurantName_ko == "참피온":
        context["restaurant_searchterm"] = "참피온삼겹살"
    elif food.restaurantName_ko == "청기와감자탕":
        context["restaurant_searchterm"] = "프랭크버거 송도캠퍼스타운역점"
    elif food.restaurantName_ko == "투다리":
        context["restaurant_searchterm"] = "투다리 캠퍼스타운점"
    elif food.restaurantName_ko == "포플러스 한우쌀국수 본점":
        context["restaurant_searchterm"] = "포플러스 한우쌀국수 송도점"
    elif food.restaurantName_ko == "호랭이곳간 본점":
        context["restaurant_searchterm"] = "호랭이곳간 송도"
    elif food.restaurantName_ko == "홍대돈부리 송도트리플스트리트점":
        context["restaurant_searchterm"] = "홍대돈부리 송도트리플점"
    elif food.restaurantName_ko == "화례무 송도트리플스트리트점":
        context["restaurant_searchterm"] = "화레무 송도트리플스트리트점"
    elif food.restaurantName_ko == "히노아지 송도트리플스트리트점":
        context["restaurant_searchterm"] = "히노아지 트리플스트리트"
    
    context["islam"] = "✅" if food.islam == 1 else "❌"
    context["hindu"] = "✅" if food.hindu == 1 else "❌"
    context["vegetarian"] = "✅" if food.vegetarian == 1 else "❌"
    context["main_ingredient"] = food.main_ingredient
    context["origin"] = food.origin
    context["price"] = food.price
    context['salty'] = food.salty
    context['sweet'] = food.sweet
    context['spicy'] = food.spicy
    return render(request, 'more.html', context)

def dislike(request, recommendation_type, recommended_food_id):
    food = Menu.objects.get(food_id = recommended_food_id)
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.salty -= food.salty
    user_profile.sweet -= food.sweet
    user_profile.spicy -= food.spicy
    user_profile.disliked_food.add(food)
    user_profile.save()
    #disliked_ingredient_today.append(food.main_ingredient)
    #disliked_food_today.append(food.food_id)
    #disliked_restaurant_today.append(food.restaurantName_ko)
    if recommendation_type == "recommend":
        return redirect("/recommend")
    elif recommendation_type == "random":
        return redirect("/food_random")


@staff_member_required
def model_upload(request):
    if request.method == "POST":
        with open("C:/Users/juhyu/foodify-platepal/foodifyapp/static/csv/food_db_231012.csv", encoding="utf-8") as f: # 이거랑 아래 거 둘 다 파일 이름 바꾸기!
            obj = csv.reader(f)
            csv_list = list(obj)
            for row in csv_list:
                menu = Menu(
                        restaurantName_ko = row[0],
                        restaurantName_en = row[1],
                        location = row[2],
                        menuName_ko =  row[3],
                        menuName_en1 = row[4],
                        menuName_en2 = row[5],
                        menuType_big = row[6],
                        menuType = row[7],
                        origin = row[8],
                        price = int(row[9])  if row[14] != '' else 0, 
                        salty = float(row[10]),
                        sweet = float(row[11]),
                        spicy = float(row[12]),
                        main_ingredient = row[13],
                        vegetarian = int(row[14]) if row[14] != '' else 0,
                        islam = int(row[15]) if row[15] != '' else 0,
                        hindu = int(row[16]) if row[16] != '' else 0,
                        rating = 0,
                        food_id = int(row[17])
                     )
                menu.save()
            context = {"success": "Success!"}
            return render(request, 'model_upload.html', context)  

    else:
        with open("C:/Users/juhyu/foodify-platepal/foodifyapp/static/csv/food_db_231012.csv", encoding="utf-8") as f:
            obj = csv.reader(f)
            csv_list = list(obj)
            context = {"value1": csv_list}
            # Menu.objects.all().delete()
            return render(request, 'model_upload.html', context)

@staff_member_required
def model_clear(request):
    Menu.objects.all().delete()
    return HttpResponse("Menu Model Cleared")


'''
@login_required
def search(request):
    context = {}  
    return render(request, 'login.html', context)
'''

def desire_flavor(request):
    return render(request, 'desire_choice_flavor.html')

def desire_origin(request, flavor):
    url_c = flavor + "/Chinese"
    url_k = flavor + "/Korean"
    url_j = flavor + "/Japanese"
    url_a = flavor + "/Asian"
    url_w = flavor + "/Western"
    context = {"c": url_c,"a": url_a,"k": url_k,"j": url_j,"w": url_w }
    return render(request, 'desire_choice_origin.html', context)

def desire_recommendation(request, flavor, origin):
    recommendation = find_food_id(origin, flavor)
    context = {"name_list": []}
    for id in recommendation:
        url = "/more/" + str(id)
        context["name_list"].append([ get_food_name_by_id(id), url  ])
        
    if len(context["name_list"]) == 0:
        context["na"] = "na"
    # return HttpResponse(context)
    return render(request, 'desire_name_list.html', context)