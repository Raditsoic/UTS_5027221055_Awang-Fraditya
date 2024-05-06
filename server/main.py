import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc, pymongo
from concurrent import futures
from protobufs import recipe_recommendation_pb2_grpc, recipe_recommendation_pb2
from bson import ObjectId


class RecipeRecommendation(recipe_recommendation_pb2_grpc.RecipeRecommendationServicer):
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client['ETS-Recipe']
        self.collection = self.db['Recipe']
        
    def GetAllRecipes(self, request, context):
        recipes = []
        for doc in self.collection.find():
            recipe = recipe_recommendation_pb2.Recipe(
                id=str(doc.get('_id')),
                title=doc.get('title', ""),
                ingredients=doc.get('ingredients', ""),
                steps=doc.get('steps', "")
            )
            recipes.append(recipe)
            
        return recipe_recommendation_pb2.GetAllRecipesResponse(recipes=recipes)
    
    def CreateRecipe(self, request, context):
        new_recipe = {
            'title': request.recipe.title,
            'ingredients': request.recipe.ingredients,
            'steps': request.recipe.steps
        }
        result = self.collection.insert_one(new_recipe)
        if result.inserted_id:
             inserted_recipe = self.collection.find_one({'_id': result.inserted_id})
        if inserted_recipe:
            created_recipe = recipe_recommendation_pb2.Recipe(
                title=inserted_recipe.get('title', ""),
                ingredients=inserted_recipe.get('ingredients', ""),
                steps=inserted_recipe.get('steps', "")
            )
            print("Created recipe:", created_recipe)
            return recipe_recommendation_pb2.CreateRecipeResponse(recipe=created_recipe)
        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to create recipe.")
            return recipe_recommendation_pb2.CreateRecipeResponse()
    
    def UpdateRecipe(self, request, context):
        filter_query = {'_id': ObjectId(request.id)}
        update_query = {
            '$set': {
                'title': request.recipe.title,
                'ingredients': request.recipe.ingredients,
                'steps': request.recipe.steps
            }
        }
        result = self.collection.update_one(filter_query, update_query)
        if result.modified_count > 0:
            updated_recipe = recipe_recommendation_pb2.Recipe(
                id=request.id,
                title=request.recipe.title,
                ingredients=request.recipe.ingredients,
                steps=request.recipe.steps
            )
            return recipe_recommendation_pb2.UpdateRecipeResponse(recipe=updated_recipe)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Recipe not found.")
            return recipe_recommendation_pb2.UpdateRecipeResponse()
    
    def DeleteRecipe(self, request, context):
        filter_query = {'_id': ObjectId(request.id)}
        result = self.collection.delete_one(filter_query)
        if result.deleted_count > 0:
            return recipe_recommendation_pb2.DeleteRecipeResponse(message="Recipe deleted successfully.")
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Recipe not found.")
            return recipe_recommendation_pb2.DeleteRecipeResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recipe_recommendation_pb2_grpc.add_RecipeRecommendationServicer_to_server(RecipeRecommendation(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    
    serve()