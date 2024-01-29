from django.contrib.auth.models import User
from foodifyapp.models import UserProfile, Menu
from django.utils.translation import get_language
from .utils import get_user_profile
from django.shortcuts import render
from random import sample
import random
import math

# user_profile = UserProfile.objects.get(user=request.user)
user_salty = UserProfile.salty
user_sweet = UserProfile.sweet
user_spicy = UserProfile.spicy
user_korean = UserProfile.Korean
user_chinese = UserProfile.Chinese
user_japanese = UserProfile.Japanese
user_asian = UserProfile.Asian
user_western= UserProfile.Western

def arctan(n):
    return math.atan(float(n)) * 3.18309886184

def get_user_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return {user_profile.salty, user_profile.sweet, user_profile.spicy}


def similarity(food_salty, food_sweet, food_spicy):
    global user_profile
    user_salty = user_profile.salty
    user_sweet = user_profile.sweet
    user_spicy = user_profile.spicy
    score = arctan(user_salty) * arctan(food_salty) + arctan(food_sweet) * arctan(user_sweet) + arctan(food_spicy) * arctan(user_spicy)
    return score 


def is_food_allowed(food, user_profile, disliked_today):
    return (
        (user_profile.vegetarian != 1 or food.vegetarian != 0) and
        (user_profile.islam != 1 or food.islam != 0) and
        (user_profile.hindu != 1 or food.hindu != 0) and # Taboo 검사
        float(food.spicy) <= float(user_profile.max_spicy) and # 매운 맛 최대치
        food.food_id not in disliked_today["food"] and 
        not (food.main_ingredient in disliked_today["ingredient"] and food.menuName_ko in disliked_today["restaurant"])
    )

def get_food_list(user_profile, disliked_today):
    global recommended_foods
    recommended_foods = list(filter(lambda food: is_food_allowed(food, user_profile, disliked_today), Menu.objects.all()))



#랜덤(notion 5번항목:완전무작위)으로 음식 10개 추천 (taboo 음식 제외해서 음식 10개 추천)
def recommend_food_random(user_profile, disliked_today):
    global recommended_foods
    get_food_list(user_profile, disliked_today)
    recommended_foods = sample(recommended_foods, min(len(recommended_foods), 10))
    return recommended_foods[random.randint(0, 9)].food_id





# 유저 정보 바탕으로 추천
def recommend_food_based_on_user_data(user_profile, disliked_today):
    global recommended_foods
    get_food_list(user_profile, disliked_today)
    
    '''
    user_preference = {'korean':UserProfile.Korean, 'chinese':UserProfile.Chinese,
                   'japanese':UserProfile.Japanese,'asian': UserProfile.Asian,
                   'western': UserProfile.Western}
    '''


    # 모든 음식에 대해 similarity 측정 (similarity() 함수 이용)
    food_scores = {}
    for food in recommended_foods:
        score = similarity(food.salty, food.sweet, food.spicy)
        food_id = food.food_id
        #if food.main_ingredient in disliked_today["ingredient"]:
            #score -= 20
        #if food.restaurantName_ko in disliked_today["restaurant"]:
            #score -= 20
        if food.price >= 20000:
            score -= 20
        score += random.randint(-20, 20)
        food_scores[food_id] = score
    disliked_foods = user_profile.disliked_food.all()
    liked_foods = user_profile.liked_food.all()
    for disliked_food in disliked_foods:
        if disliked_food.food_id in recommended_foods:
            food_scores[disliked_food.food_id] -= 10 # !! 점수는 나중에 조절하기 !!
    for liked_food in liked_foods:
        if liked_food.food_id in recommended_foods:
            food_scores[liked_food.food_id] += 30 # !! 점수는 나중에 조절하기 !!

    # 점수 순으로 정렬 
    sorted_food_scores = sorted(food_scores.items(), key=lambda x: x[1], reverse=True)

    # 상위 100개 추출 
    top_food_items = [item[0] for item in sorted_food_scores[:50]]

    # 그 중 하나 랜덤으로 뽑기
    recommended_food = random.choice(top_food_items)

    # return 하기
    return recommended_food #ID를 return 한다.



#사용자가 지정해서 필터링 후 음식 10개 추천
#옵션(notion 2번항목:옵션선택)으로 음식 10개 추천
#request에서 사용자 선택한거를 적용
def recommend_option_foods(request):
    if request.method == 'POST':
        selected_features_location = request.POST.getlist('feature_location')
        selected_features_origin = request.POST.getlist('feature_origin')
        selected_features_price = request.POST.getlist('feature_price')
        selected_features_salty = request.POST.getlist('feature_salty')
        selected_features_sweet = request.POST.getlist('feature_sweet')
        selected_features_spicy = request.POST.getlist('feature_spicy')
        selected_features_main_ingredient = request.POST.getlist('feature_main_ingredient')
        selected_features_menutype = request.POST.getlist('feature_menutype')

        recommended_menus = Menu.objects.filter(
            location__in=selected_features_location,
            origin__in=selected_features_origin,
            price__in=selected_features_price,
            salty__in=selected_features_salty,
            sweet__in=selected_features_sweet,
            spicy__in=selected_features_spicy,
            main_ingredient__in=selected_features_main_ingredient,
            menutype__in=selected_features_menutype
        ).distinct()[:100000]

        # 중복 없이 10개의 메뉴를 랜덤하게 선택
        recommended_menus = sample(list(recommended_menus), min(len(recommended_menus), 10))

        context = {
            'recommended_menus': recommended_menus
        }
        return render(request, 'recommendations.html', context)
    return render(request, 'menu_selection.html')

#사용자에게 선택할 수 있는 특성들을 입력받는 화면은 menu_selection.html 템플릿 파일에 구현 필요

#사용자 데이터와 음식 데이터의 유사도 측정하는 벡터를 사용해서 추천(notion 1번 하위 항목)
# 노션에 있는 arctan보면 치역이 -5부터 5이고 DB팀 표 보면 맛 정도가 1~4까지 있던데 이거 값도 
# 조정 한 번 해야할 듯 일단은 k랑 m을 상수 1로 두고 할게

def food(food_parameter):
    disliked_today = {"ingredient": food_parameter["disliked_ingredient_today"],
                      "food": food_parameter["disliked_food_today"],
                      "restaurant": food_parameter["disliked_restaurant_today"]}
    recommended_food_id = 0
    if food_parameter["user_profile"] != None: #user profile이 존재한다면 이를 global 변수에 저장
        global user_profile
        user_profile = food_parameter["user_profile"]
    if food_parameter["recommendation_type"] == "random":
        recommended_food_id = recommend_food_random(food_parameter["user_profile"], disliked_today) #food_id를 반환함
    elif food_parameter["recommendation_type"] == "user_data":
        recommended_food_id = recommend_food_based_on_user_data(food_parameter["user_profile"], disliked_today)
    return recommended_food_id

def get_food_by_id(recommended_food_id, food_parameter):
    food = Menu.objects.get(food_id=recommended_food_id)
    language = get_language()
    if language == "ko":
        context = {"food_name": food.menuName_ko, "food_name_korean": food.menuName_ko, "food_description": "", "restaurant": food.restaurantName_ko, "location": food.location, "menu_type": food.menuType}
    else:
        context = {"food_name": food.menuName_en1, "food_name_korean": food.menuName_ko, "food_description": food.menuName_en2, "restaurant": food.restaurantName_en,"location": food.location, "menu_type": food.menuType}
    if food_parameter["recommendation_type"] == "random" and language == "ko":
        context["recommendation_type"] = "무작위 추첨"
    elif food_parameter["recommendation_type"] == "random" and language == "en":
        context["recommendation_type"] = "Complete Random"
    elif food_parameter["recommendation_type"] == "user_data" and language == "ko":
        context["recommendation_type"] = "Foodify 음식 추천"
    elif food_parameter["recommendation_type"] == "user_data" and language == "en":
        context["recommendation_type"] = "Recommended Just for You"   
    return context

def get_food_name_by_id(id):
    food = Menu.objects.get(food_id=id)
    if food.menuName_en2 != "":
        result = [food.menuName_ko, food.menuName_en2]
    else:
        result = [food.menuName_ko, food.menuName_en1]
    return result


#사용자 데이터에 감점과 가점
# k는 가중치, 얼마나 가중할지는 나중에 설정

def update_user_profile(user_profile, menu):
        k= 0.5
        user_profile = UserProfile.objects.all()
        menu = Menu.objects.all()
    # 사용자 선호도에 로그 함수를 적용한 후 가점 값 계산
        #맛
        user_preference = user_profile.salty 
        score_change = menu.salty 
        if score_change > user_preference:
            user_profile.salty += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
        elif score_change < user_preference:
            user_profile.salty -= math.log(user_preference + 1) * abs(score_change)
        elif score_change == user_preference:
            pass
        # 사용자 선호도에 상한선을 적용 (우선 -10~10으로 설정. 추후 수정)
        max_preference = 10
        min_preference = -10
        if user_preference > max_preference:
            user_preference = max_preference
        elif user_preference < min_preference:
            user_preference = min_preference
        user_profile.salty=user_preference
        user_profile.save()


        user_preference = user_profile.sweet
        score_change = menu.sweet
        if score_change > user_preference:
            user_profile.sweet += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
        elif score_change < user_preference:
            user_profile.sweet -= math.log(user_preference + 1) * abs(score_change)
        elif score_change == user_preference:
            pass
        max_preference = 10
        min_preference = -10
        if user_preference > max_preference:
            user_preference = max_preference
        elif user_preference < min_preference:
            user_preference = min_preference
        user_profile.sweet=user_preference
        user_profile.save()

        user_preference = user_profile.spicy
        score_change = menu.spicy
        if score_change > user_preference:
            user_profile.spicy += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
        elif score_change < user_preference:
            user_profile.spicy -= math.log(user_preference + 1) * abs(score_change)
        elif score_change == user_preference:
            pass
        max_preference = 10
        min_preference = -10
        if user_preference > max_preference:
            user_preference = max_preference
        elif user_preference < min_preference:
            user_preference = min_preference
        user_profile.spicy=user_preference
        user_profile.save()

    #종류
        user_preference = user_profile.Korean
        if menu.origin == "Korean":
            if score_change > user_preference:
                user_profile.Korean += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
            elif score_change < user_preference:
                user_profile.Korean -= math.log(user_preference + 1) * abs(score_change)
            elif score_change == user_preference:
                pass
            max_preference = 10
            min_preference = -10
            if user_preference > max_preference:
                user_preference = max_preference
            elif user_preference < min_preference:
                user_preference = min_preference
            user_profile.Korean=user_preference
            user_profile.save()
        else:
            pass


        user_preference = user_profile.Chinese
        if menu.origin == "Chinese":
            if score_change > user_preference:
                user_profile.Chinese += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
            elif score_change < user_preference:
                user_profile.Chinese -= math.log(user_preference + 1) * abs(score_change)
            elif score_change == user_preference:
                pass
            max_preference = 10
            min_preference = -10
            if user_preference > max_preference:
                user_preference = max_preference
            elif user_preference < min_preference:
                user_preference = min_preference
            user_profile.Chinese=user_preference
            user_profile.save()
        else:
            pass

        user_preference = user_profile.Japanese
        if menu.origin == "Japanese":
            if score_change > user_preference:
                user_profile.Japanese += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
            elif score_change < user_preference:
                user_profile.Japanese -= math.log(user_preference + 1) * abs(score_change)
            elif score_change == user_preference:
                pass
            max_preference = 10
            min_preference = -10
            if user_preference > max_preference:
                user_preference = max_preference
            elif user_preference < min_preference:
                user_preference = min_preference
            user_profile.Japanese=user_preference
            user_profile.save()
        else:
            pass
        
        user_preference = user_profile.Western
        if menu.origin == "Western":
            if score_change > user_preference:
                user_profile.Western += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
            elif score_change < user_preference:
                user_profile.Western -= math.log(user_preference + 1) * abs(score_change)
            elif score_change == user_preference:
                pass
            max_preference = 10
            min_preference = -10
            if user_preference > max_preference:
                user_preference = max_preference
            elif user_preference < min_preference:
                user_preference = min_preference
            user_profile.Western=user_preference
            user_profile.save()
        else:
            pass

        user_preference = user_profile.Asian
        if menu.origin == "Asian":
            if score_change > user_preference:
                user_profile.Asian += math.log(user_preference + 1) * score_change
            #1을 더해서 0이 안나오게 조정+가점감점이 선호도가 높아지거나 낮아질수록 적어지게 만듦!
            elif score_change < user_preference:
                user_profile.Asian -= math.log(user_preference + 1) * abs(score_change)
            elif score_change == user_preference:
                pass
            max_preference = 10
            min_preference = -10
            if user_preference > max_preference:
                user_preference = max_preference
            elif user_preference < min_preference:
                user_preference = min_preference
            user_profile.Asian=user_preference
            user_profile.save()
        else:
            pass

        return True


# 리스트 형태로 얘가 선택한 것들이 나온거지. 

def find_food_id(origin, flavor):
    # 결과를 저장할 빈 목록을 생성
    find_food_id = []
    menu_items=Menu.objects.all()
    # 메뉴 항목 목록을 반복
    for menu_item in menu_items:
        # 각 메뉴 항목의 origin 및 flavor를 검사
        if menu_item.origin == origin:
            if flavor == "sweet" and menu_item.sweet>=3:
                find_food_id.append(menu_item.food_id)
            elif flavor == "spicy" and menu_item.spicy>=3:
                find_food_id.append(menu_item.food_id)
            elif flavor == "salty" and menu_item.salty>=3:
                find_food_id.append(menu_item.food_id)

    # 결과 목록 반환
    return find_food_id

'''
def recommend_foods(request):
    if request.method == 'POST':
        recommendation_type = request.POST.get('recommendation_type')

        if recommendation_type == 'User Data Based Recommendation':
            k = 1
            user_vector = [UserProfile.objects.first().spicy, UserProfile.objects.first().sweet, UserProfile.objects.first().salty]
            recommended_foods = []

            user_vector_min = [user - k for user in user_vector]
            user_vector_max = [user + k for user in user_vector]

            for food in Menu.objects.all():
                food_vector = [food.spicy, food.sweet, food.salty]
                similarity = calculate_similarity(user_vector, food_vector)

                if all(user_min <= food_value <= user_max for user_min, food_value, user_max in zip(user_vector_min, food_vector, user_vector_max)):
                    recommended_foods.append((food, similarity))

            recommended_foods = sorted(recommended_foods, key=lambda x: x[1], reverse=True)[:10]

        elif recommendation_type == 'Changed User Data Based Recommendation':
            user_spicy = float(request.POST.get('user_spicy'))
            user_sweet = float(request.POST.get('user_sweet'))
            user_salty = float(request.POST.get('user_salty'))
            k = 1

            user_vector = [UserProfile.objects.first().spicy + user_spicy, 
                           UserProfile.objects.first().sweet + user_sweet,
                           UserProfile.objects.first().salty + user_salty]

            recommended_foods = []

            user_vector_min = [user - k for user in user_vector]
            user_vector_max = [user + k for user in user_vector]
            
            for food in Menu.objects.all():
                food_vector = [food.spicy, food.sweet, food.salty]
                similarity = similarity(user_vector, food_vector)

                if all(user_min <= food_value <= user_max for user_min, food_value, user_max in zip(user_vector_min, food_vector, user_vector_max)):
                    recommended_foods.append((food, similarity))

            recommended_foods = sorted(recommended_foods, key=lambda x: x[1], reverse=True)[:10]

        context = {
            'recommended_foods': recommended_foods
        }
        return render(request, 'recommendations.html', context)

    return render(request, 'user_input.html')
'''
