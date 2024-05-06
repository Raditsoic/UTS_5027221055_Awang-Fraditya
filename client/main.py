import grpc
import streamlit as st
import pandas as pd
import api
from protobufs import recipe_recommendation_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = recipe_recommendation_pb2_grpc.RecipeRecommendationStub(channel)

def add_ingre():
    st.session_state["ingredients"].append(new_ingredient)

st.title("Recipe App Recommendation")

if 'ingredients' not in st.session_state:
    st.session_state['ingredients'] = []

### Main Container
main_container = st.container()

main_container.header("Your Ingredient: ")
for ingredient in st.session_state.ingredients:
    main_container.write("- " + ingredient) 

new_ingredient = main_container.text_input("Input an Ingredient:")

add_ingredient = main_container.button("Add Ingredient", on_click=add_ingre)

if main_container.button("Add New Recipe"):
    ingredients = ", ".join(st.session_state['ingredients'])
    response = api.create_recipe(stub, ingredients)
    if not response:
      main_container.markdown("Ooopss!! Error while generating your recipe, try again please!")  
    st.session_state['ingredients'] = []
    st.rerun()


#Sidebar
sidebar_container = st.container()
if 'history' not in st.session_state:
    history = api.get_all_recipes(stub)
    recipes = []
    if history:
        for recipe_message in history.recipes:
            recipe_dict = {
                'ID': recipe_message.id,
                'Title': recipe_message.title,
                'Ingredients': recipe_message.ingredients,
                'Steps': recipe_message.steps
            }
            recipes.append(recipe_dict)
    st.session_state['history'] = recipes


selected_recipe = st.sidebar.selectbox(
    "Previous Recipes",
    [recipe["Title"] for recipe in st.session_state['history']]
)

if 'edit_form' not in st.session_state:
    st.session_state['edit_form'] = False
   
if st.session_state['edit_form']:
    new_ingredient = st.sidebar.text_input("Ingredients: ")
    new_steps = st.sidebar.text_input("Steps: ")
    
    if st.sidebar.button("Cancel"):
        st.session_state['edit_form'] = False
        st.rerun()
        
    if st.sidebar.button("Save"):
        for i, recipe in enumerate(st.session_state["history"]):
            if recipe["Title"] == selected_recipe:
                title=selected_recipe
                id=recipe['ID']
                api.update_recipe(stub, id, title, new_ingredient, new_steps)
                break 
        st.session_state['edit_form'] = False
        st.rerun()
else:
    for index, recipe in enumerate(st.session_state['history']):
        if recipe["Title"] == selected_recipe:
            st.sidebar.subheader("Ingredients: ")
            items = recipe["Ingredients"].split(", ")
            for item in items:
                st.sidebar.markdown(f"- {item.capitalize()}")
                
            st.sidebar.subheader("Steps: ")
            steps = recipe["Steps"].split("; ")
            for index, step in enumerate(steps, start=1):
                st.sidebar.markdown(f"{index}. {step.capitalize()}")

    if st.sidebar.button("Delete Recipe"):
        for i, recipe in enumerate(st.session_state["history"]):
            if recipe["Title"] == selected_recipe:
                del st.session_state["history"][i]
                api.delete_recipe(stub, recipe['ID'])
                break 
        st.rerun()
            
    if st.sidebar.button("Edit Recipe"):
        st.session_state['edit_form'] = True
        st.rerun()
        





