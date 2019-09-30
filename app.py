import boto3
import base64
from botocore.exceptions import ClientError
import asana
import json
import pytz
from datetime import date, timedelta, datetime




def get_secret():

    secret_name = "asana-social-schedule"
    region_name = "us-east-2"
    secret="temp"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # Get secret
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        # Decrypts secret
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return json.loads(secret)


def createTask(event, context):
    today = datetime.now(pytz.timezone('US/Eastern'))

    start = today + timedelta(days=7)
    two_weeks = today + timedelta(days=21)

    token_dict = get_secret()
    token = token_dict.get('personal_token')
    client = asana.Client.access_token(token)
    client.LOG_ASANA_CHANGE_WARNINGS = False


    client.options['client_name'] = "asana-social-schedule"

    user_gid = {
        'adrian' : '1131062864194735',
        'junninho' : '1001152498318728'
    }

    project_gid = "1142170150042313"

    tasks = client.tasks.find_all({'project': project_gid}, page_size = 100)
    
    # print(tasks)

    try:
        last_id = next(x for x in tasks)
        last = client.tasks.find_by_id(last_id.get('gid'))

        last_assignee = last.get('assignee').get('gid')
    except:
        last_assignee = user_gid.get('junninho')
    
    next_assignee = ""

    print(last_assignee)

    if last_assignee == user_gid.get('adrian'):
        next_assignee = user_gid.get('junninho')
    else:
        next_assignee = user_gid.get('adrian')

    

    client.tasks.create({
        'projects' : project_gid,
        'assignee' : next_assignee,
        'followers' : last_assignee,
        'name' : 'Schedule posts for ' + start.strftime("%B %d, %Y") + " to " + two_weeks.strftime("%B %d, %Y"),
        'due_on': str(today + timedelta(days=5))
        })

    return {
        'statusCode' : 200,
        'body' : json.dumps("Complete")
    }