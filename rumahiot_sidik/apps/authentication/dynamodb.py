import boto3
from uuid import uuid4
from rumahiot_sidik.apps.authentication.utils import password_hasher
from boto3.dynamodb.conditions import Key
from rumahiot_sidik.settings import RUMAHIOT_USERS_TABLE,RUMAHIOT_REGION,RUMAHIOT_USERS_PROFILE_TABLE,DEFAULT_PROFILE_IMAGE_URL
from datetime import datetime

class SidikDynamoDB():

    # initiate the client
    def __init__(self):
        self.client = boto3.resource('dynamodb', region_name=RUMAHIOT_REGION)

    # get user account by email
    # input parameter : email(string)
    # return user [dict]
    def get_user_account_by_email(self,email):
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        # get user account
        response = table.scan(
            FilterExpression=Key('email').eq(email),
        )
        # please take the first element , (its shouldn't be possible though , just in case)
        # returning [uuid(string), email(string), password(string), last_login (string) -> utc timestamp] or [] if theres not match
        return response['Items']

    # email authentication
    # input parameter : email(string) , password(string)
    # returning : is_valid(boolean) , data(dict) , error_message(string)
    # todo : add last login
    def user_get_by_email(self,email, password):
        data = {}
        user = self.get_user_account_by_email(email)
        if len(user) != 1:
            # If returned data isnt normal (more than 1 email) -> shouldn't happen though
            data['is_valid'] = False
            data['user'] = None
            data['error_message'] = "Invalid email or password"
            return data
        else:
            if user[0]['password'] != password_hasher(user[0]['salt'], password):
                # if the password wasn't correct
                data['is_valid'] = False
                data['user'] = None
                data['error_message'] = "Invalid email or password"
                return data
            else:
                data['is_valid'] = True
                data['user'] = user[0]
                data['error_message'] = None
                return data

    # Create user and put the data in dynamodb
    # input parameter : email(string) , password(string)
    # returning : status(boolean)
    # todo check aws timezone
    def create_user_by_email(self,full_name, email, password):
        status = False
        # for password salt
        salt = uuid4().hex
        # for user uuid
        uuid = uuid4().hex
        # password
        hashed_password = password_hasher(salt, password)
        # check for account existance
        user = self.get_user_account_by_email(email)

        if len(user) != 0:
            status = False
        else:
            table = self.client.Table(RUMAHIOT_USERS_TABLE)
            response = table.put_item(
                Item={
                    'email': email,
                    'password': hashed_password,
                    'user_uuid': uuid,
                    'salt': salt,
                    'time_created': str(datetime.now().timestamp())
                }
            )

            # Put profile data
            table = self.client.Table(RUMAHIOT_USERS_PROFILE_TABLE)
            # define all profile field here , use '-' as business logic for none
            response = table.put_item(
                Item={
                    'user_uuid': uuid,
                    'full_name': full_name,
                    'profile_image': DEFAULT_PROFILE_IMAGE_URL,
                    'phone_number': '-',
                    'time_updated': str(datetime.now().timestamp())
                }
            )
            status = True
        return status
