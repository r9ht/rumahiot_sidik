from datetime import datetime
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key

from rumahiot_sidik.apps.authentication.utils import SidikUtils
from rumahiot_sidik.settings import RUMAHIOT_USERS_TABLE, RUMAHIOT_REGION, RUMAHIOT_USERS_PROFILE_TABLE, \
    DEFAULT_PROFILE_IMAGE_URL


class SidikDynamoDB:

    # initiate the client
    def __init__(self):
        self.client = boto3.resource('dynamodb', region_name=RUMAHIOT_REGION)

    # get user account by email
    # input parameter : email(string)
    # return user [dict]
    def get_user_by_email(self, email):
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        # get user account
        response = table.scan(
            FilterExpression=Key('email').eq(email),
        )
        # please take the first element , (its shouldn't be possible though , just in case)
        # return [uuid(string), email(string), password(string), last_login (string) -> utc timestamp] or [] if theres not match
        return response['Items']

    # get user account by user_uuid
    # input parameter : user_uuid(string)
    # return user [dict]
    def get_user_by_user_uuid(self, user_uuid):
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        # get user account
        response = table.scan(
            FilterExpression=Key('user_uuid').eq(user_uuid),
        )
        # please take the first element , (its shouldn't be possible though , just in case)
        # return [uuid(string), email(string), password(string), last_login (string) -> utc timestamp] or [] if theres not match
        return response['Items']
        # get user account by user_uuid
        # input parameter : user_uuid(string)
        # return user [dict]

    def get_user_by_activation_uuid(self, activation_uuid):
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        # get user account
        response = table.scan(
            FilterExpression=Key('activation_uuid').eq(activation_uuid),
        )
        # please take the first element , (its shouldn't be possible though , just in case)
        # return [uuid(string), email(string), password(string), last_login (string) -> utc timestamp] or [] if theres not match
        return response['Items']

    # email authentication
    # input parameter : email(string) , password(string)
    # return : is_valid(boolean) , data(dict) , error_message(string)
    # todo : add last login
    def check_user(self, email, password):
        data = {}
        user = self.get_user_by_email(email)
        if len(user) != 1:
            # If returned data isnt normal (more than 1 email) -> shouldn't happen though
            data['is_valid'] = False
            data['user'] = None
            data['error_message'] = "There was an error with your E-Mail/Password combination"
            return data

        else:
            utils = SidikUtils()
            if user[0]['password'] != utils.password_hasher(user[0]['salt'], password):
                # if the password wasn't correct
                data['is_valid'] = False
                data['user'] = None
                data['error_message'] = "There was an error with your E-Mail/Password combination"
                return data
            elif user[0]['activated'] != True:
                data['is_valid'] = False
                data['user'] = None
                data['error_message'] = "Please activate your account before logging in"
                return data
            else:
                data['is_valid'] = True
                data['user'] = user[0]
                data['error_message'] = None
                return data

    # Create user and put the data in dynamodb
    # input parameter : email(string) , password(string), activation_uuid(string)
    # return : status(boolean)
    # todo check aws timezone
    def create_user_by_email(self, full_name, email, password, activation_uuid):
        utils = SidikUtils()
        status = False
        # for password salt
        salt = uuid4().hex
        # for user uuid
        uuid = uuid4().hex
        # password
        hashed_password = utils.password_hasher(salt, password)
        # check for account existance
        user = self.get_user_by_email(email)

        # if user already exist
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
                    'activation_uuid': activation_uuid,
                    'activated': False,
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
                    'phone_number': '0000000',
                    'time_updated': str(datetime.now().timestamp())
                }
            )
            status = True
        return status

    def activate_user_account(self, user_uuid):
        # keep the error from breaking service by catching the client error in the view
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        response = table.update_item(
            Key={
                'user_uuid': user_uuid
            },
            UpdateExpression="set activated=:a",
            ExpressionAttributeValues={
                ':a': True,
            },
            ReturnValues="UPDATED_NEW"
        )

    def change_user_password(self, user_uuid, new_password):
        # keep the error from breaking service by catching the client error in the view
        new_salt = uuid4().hex
        utils = SidikUtils()
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        response = table.update_item(
            Key={
                'user_uuid': user_uuid
            },
            UpdateExpression="set salt=:s, password=:p",
            ExpressionAttributeValues={
                ':s': new_salt,
                ':p': utils.password_hasher(salt=new_salt, password=new_password)
            },
            ReturnValues="UPDATED_NEW"
        )
