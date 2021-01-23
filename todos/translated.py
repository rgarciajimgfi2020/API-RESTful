import os
import json

from todos import decimalencoder
import boto3

dynamodb = boto3.resource('dynamodb')


def get(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event.get('pathParameters').get('id')
        }
    )

    item = result.get('Item')
    text = item.get('text')

    target_language = event.get('pathParameters').get('language')
    comprehend = boto3.client('comprehend')
    source_language = comprehend.detect_dominant_language(Text=text).get('Languages')[0].get('LanguageCode')

    translator = boto3.client('translate')
    translation = translator.translate_text(
        Text=text,
        TerminologyNames=[],
        SourceLanguageCode=source_language,
        TargetLanguageCode=target_language
    )
    translated_text = translation.get('TranslatedText')
    item.update({'text': translated_text})

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(item,
                           cls=decimalencoder.DecimalEncoder)
    }

    return response