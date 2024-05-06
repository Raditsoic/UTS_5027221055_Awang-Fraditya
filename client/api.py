import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protobufs import recipe_recommendation_pb2
from transformers import pipeline

recipe_rec_model = pipeline("text2text-generation", model="flax-community/t5-recipe-generation")

def create_recipe(stub, ingredients):
    transformers_response = recipe_rec_model(ingredients)
    new_recipe = transformers_response[0]['generated_text']
    print(new_recipe)

    title_match = re.search(r"title: (.+?) ingredients:", new_recipe)
    title = title_match.group(1).strip() if title_match else ""

    ingredients_match = re.search(r"ingredients: (.+?) directions:", new_recipe)
    ingredients_str = ingredients_match.group(1).strip() if ingredients_match else ""

    directions_match = re.search(r"directions: (.+)", new_recipe)
    directions = directions_match.group(1).strip() if directions_match else ""

    # Format the ingredients string
    ingredients_list = re.split(r'(?<=\D)(?=\d)', ingredients_str)
    ingredients_string = ", ".join(ingredients_list)

    # Format the directions string
    steps_list = [step.strip() for step in directions.split(".")]
    steps_list = steps_list[:-1]
    steps_string = "; ".join(steps_list)
    
    recipe = recipe_recommendation_pb2.Recipe(
        title=title.capitalize(),
        ingredients=ingredients_string,
        steps=steps_string
    )
    print(recipe)
    request = recipe_recommendation_pb2.CreateRecipeRequest(recipe=recipe)
    response = stub.CreateRecipe(request)
    return response


def update_recipe(stub, recipe_id, new_title, new_ingredients, new_steps):
    updated_recipe = recipe_recommendation_pb2.Recipe(
        id=recipe_id,
        title=new_title,
        ingredients=new_ingredients,
        steps=new_steps
    )
    request = recipe_recommendation_pb2.UpdateRecipeRequest(id=recipe_id, recipe=updated_recipe)
    response = stub.UpdateRecipe(request)
    print("Updated recipe with ID:", response.recipe.id)

def delete_recipe(stub, recipe_id:str):
    request = recipe_recommendation_pb2.DeleteRecipeRequest(id=recipe_id)
    response = stub.DeleteRecipe(request)
    print(response.message)

def get_all_recipes(stub):
    request = recipe_recommendation_pb2.GetAllRecipesRequest()
    response = stub.GetAllRecipes(request)
    return response


