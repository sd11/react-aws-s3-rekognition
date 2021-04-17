from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib
from botocore.vendored import requests

print('Loading function')

rekognition = boto3.client('rekognition')
s3 = boto3.resource("s3")


# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response


def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})

    # Sample code to write response to DynamoDB table 'MyTable' with 'PK' as Primary Key.
    # Note: role used for executing this Lambda function should have write access to the table.
    #table = boto3.resource('dynamodb').Table('MyTable')
    #labels = [{'Confidence': Decimal(str(label_prediction['Confidence'])), 'Name': label_prediction['Name']} for label_prediction in response['Labels']]
    #table.put_item(Item={'PK': key, 'Labels': labels})
    return response


def index_faces(bucket, key):
    # Note: Collection has to be created upfront. Use CreateCollection API to create a collecion.
    #rekognition.create_collection(CollectionId='BLUEPRINT_COLLECTION')
    response = rekognition.index_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}}, CollectionId="BLUEPRINT_COLLECTION")
    return response

def find_recipes(ingredients):
    payload = {
        'ingredients': ingredients,
        'number': 2,
        'ranking': '1',
        'apiKey': '8bce36150747496f98b2c81860545458'
    }
    recipes = requests.get('https://api.spoonacular.com/recipes/findByIngredients', params=payload)
    return recipes.json()


# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        # Calls rekognition DetectFaces API to detect faces in S3 object
        #response = detect_faces(bucket, key)

        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)

        # Calls rekognition IndexFaces API to detect faces in S3 object and index faces into specified collection
        #response = index_faces(bucket, key)

        # Print response to console.
        print('Detected labels for ' + key)
        print()
        ingredients = ""
        for label in response['Labels']:
            encodedName = label['Name'].encode('utf-8')

            if len(ingredients):
                ingredients = ingredients + ", " + encodedName
            else:
                ingredients = encodedName

            # print ("Label: " + label['Name'])
            # print ("Confidence: " + str(label['Confidence']))
            # print ("Instances:")
            #for instance in label['Instances']:
            #     print ("  Bounding box")
            #     print ("    Top: " + str(instance['BoundingBox']['Top']))
            #     print ("    Left: " + str(instance['BoundingBox']['Left']))
            #     print ("    Width: " +  str(instance['BoundingBox']['Width']))
            #     print ("    Height: " +  str(instance['BoundingBox']['Height']))
            #     print ("  Confidence: " + str(instance['Confidence']))
            #     print()

            # print ("Parents:")
            # for parent in label['Parents']:
            #     print ("   " + parent['Name'])
            # print ("----------")
            # print ()

        recipes = find_recipes(ingredients)
        #return recipes
        #print(ingredients)
        #print(recipes)

        recipeResponse = []
        for recipe in recipes:
            recipeIngredients = []
            for usedIngredient in recipe['usedIngredients']:
                recipeIngredients.append({
                    'name': usedIngredient['name'],
                    'servingSize': str(usedIngredient['amount']) + ' ' + usedIngredient['unit']
                })

            recipeResponse.append({
                'title': recipe['title'],
                'image': recipe['image'],
                'ingredients': recipeIngredients
            })

        responseData = { 'ingredients': ingredients, 'recipes': recipeResponse }

        if responseData:
            print(s3)
            obj = s3.Object('groupneuralnetworkrecipebucket1','recipes.json')
            obj.put(Body=json.dumps(responseData))

        return responseData
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
