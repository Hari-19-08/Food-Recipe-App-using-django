from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Recipe, Rating, Comment, UserProfile
from .forms import ProfileForm  # Adjust this import based on your form structure
from django.db.models import Avg
from django.contrib.auth.models import User



# Home page view
def home(request):
    queryset = Recipe.objects.all()[:4]  # Fetch the first 4 recipes
    context = {'recipes': queryset}
    return render(request, "index.html", context)

# View list of recipes
def view_recipe_list(request):
    recipes = Recipe.objects.all()
    context = {'recipes': recipes}
    return render(request, 'recipes/recipe_list.html', context)

# Add a recipe (requires login)
@login_required
def add_recipe(request):
    if request.method == 'POST':
        data = request.POST
        recipe_image = request.FILES.get('recipe_image')

        Recipe.objects.create(
            user=request.user,
            recipe_image=recipe_image,
            recipe_name=data.get('recipe_name'),
            recipe_ingridents=data.get('recipe_ingridents'),
            recipe_description=data.get('recipe_description'),
            instructions=data.get('instructions'),
            cooking_time=data.get('cooking_time'),
        )
        return redirect('/addrecipe')
    return render(request, "addrecipe.html")

# View recipe detail and handle ratings/comments
def recipe_detail(request, id):
    queryset = get_object_or_404(Recipe, id=id)
    ingredients = queryset.recipe_ingridents.split('\n')
    instructions = queryset.instructions.split('.')

    # Handle POST request for rating and commenting
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Rating
            score = request.POST.get('score')
            if score:
                score = int(score)
                existing_rating, _ = Rating.objects.update_or_create(
                    user=request.user,
                    recipe_name=queryset,
                    defaults={'score': score}
                )

            # Comment
            content = request.POST.get('content')
            if content:
                Comment.objects.create(user=request.user, recipe_name=queryset, content=content)
        else:
            messages.error(request, 'Please login to rate or comment.')

        return redirect("recipe_detail", id=id)

    comments = Comment.objects.filter(recipe_name=queryset).order_by('-created_at')
    average_rating = Rating.objects.filter(recipe_name=queryset).aggregate(Avg('score'))['score__avg'] or 0
    rating_range = range(1, 6)  # Define the rating range (1-5)

    context = {
        'recipes': queryset,
        'ingredients': ingredients,
        'instructions': instructions,
        'average_rating': average_rating,
        'rating_range': rating_range,
        'comments': comments,
    }

    return render(request, "recipedetail.html", context)

# View all recipes by latest creation
def viewrecipe(request):
    queryset = Recipe.objects.order_by('-created_at')
    context = {'recipes': queryset}
    return render(request, "view.html", context)

# Delete a recipe (requires login)
@login_required
def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if recipe.user == request.user:  # Ensure only the owner can delete
        recipe.delete()
    return redirect('/viewrecipe')

# Update a recipe (requires login)
@login_required  
def update_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if recipe.user != request.user:
        return redirect('/viewrecipe')  # Prevent others from updating

    if request.method == 'POST':
        data = request.POST
        recipe.recipe_name = data.get('recipe_name')
        recipe.recipe_description = data.get('recipe_description')
        recipe.recipe_ingridents = data.get('recipe_ingridents')
        recipe.instructions = data.get('instructions')
        recipe.cooking_time = data.get('cooking_time')

        recipe_image = request.FILES.get('recipe_image')
        if recipe_image:
            recipe.recipe_image = recipe_image

        recipe.save()
        return redirect('/viewrecipe/')

    context = {'recipe': recipe}
    return render(request, "update_recipe.html", context)

# User authentication
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password')
            return redirect('/login_page/')
        else:
            login(request, user)
            return redirect('/viewrecipe/')
    return render(request, "login_page.html")

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('/register')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        messages.success(request, 'Account created successfully')
        return redirect('/login_page/')
    return render(request, "register.html")

# Logout the user
@login_required
def log_out(request):
    logout(request)
    return redirect('/login_page')

# Search functionality
def search(request):
    queryset = Recipe.objects.order_by('-created_at')
    if request.GET.get('search'):
        queryset = queryset.filter(recipe_name__icontains=request.GET.get('search'))
    context = {'recipes': queryset}
    return render(request, "search.html", context)

# View and create user profile
@login_required
def profile(request, id):
    user = get_object_or_404(User, id=id)
    user_recipes = Recipe.objects.filter(user=user)
    recipe_count = user_recipes.count()

    try:
        userdetails = UserProfile.objects.get(user=user)
        context = {'user': user, 'recipes': user_recipes, 'userdetails': userdetails, 'recipe_count': recipe_count}
    except UserProfile.DoesNotExist:
        return redirect("/create_profile/")

    return render(request, "profile.html", context)

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a new UserProfile instance and associate it with the current user
            user_profile = form.save(commit=False)
            user_profile.user = request.user  # Link profile to the current user
            user_profile.save()
            messages.success(request, "Profile created successfully!")
            return redirect('profile', id=request.user.id)  # Redirect to the profile page
    else:
        form = ProfileForm()  # Create an empty form for GET requests

    return render(request, 'create_profile.html', {'form': form})




@login_required
def update_profile(request, id):
    user_profile = get_object_or_404(UserProfile, id=id)
    if request.method == 'POST':
        bio = request.POST.get('bio')
        dob = request.POST.get('dob')
        profile_pic = request.FILES.get('profile_pic')

        user_profile.bio = bio
        user_profile.dob = dob
        if profile_pic:
            user_profile.profile_pic = profile_pic

        user_profile.save()
        return redirect('profile', id=request.user.id)

    context = {'userprofile': user_profile}
    return render(request, "updateprofile.html", context)
