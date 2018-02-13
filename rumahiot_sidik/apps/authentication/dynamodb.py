import boto3
from uuid import uuid4
from rumahiot_sidik.apps.authentication.utils import SidikUtils
from boto3.dynamodb.conditions import Key
from rumahiot_sidik.settings import RUMAHIOT_USERS_TABLE,RUMAHIOT_REGION,RUMAHIOT_USERS_PROFILE_TABLE,DEFAULT_PROFILE_IMAGE_URL,RUMAHIOT_DEVICE_TABLE
from datetime import datetime

class SidikDynamoDB():

    # initiate the client
    def __init__(self):
        self.client = boto3.resource('dynamodb', region_name=RUMAHIOT_REGION)

    # get user account by email
    # input parameter : email(string)
    # return user [dict]
    def get_user_by_email(self,email):
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
    def get_user_by_user_uuid(self,user_uuid):
        table = self.client.Table(RUMAHIOT_USERS_TABLE)
        # get user account
        response = table.scan(
            FilterExpression=Key('user_uuid').eq(user_uuid),
        )
        # please take the first element , (its shouldn't be possible though , just in case)
        # return [uuid(string), email(string), password(string), last_login (string) -> utc timestamp] or [] if theres not match
        return response['Items']

    # email authentication
    # input parameter : email(string) , password(string)
    # return : is_valid(boolean) , data(dict) , error_message(string)
    # todo : add last login
    def check_user(self,email, password):
        data = {}
        user = self.get_user_by_email(email)
        if len(user) != 1:
            # If returned data isnt normal (more than 1 email) -> shouldn't happen though
            data['is_valid'] = False
            data['user'] = None
            data['error_message'] = "Invalid email or password"
            return data
        else:
            utils = SidikUtils()
            if user[0]['password'] != utils.password_hasher(user[0]['salt'], password):
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
    # return : status(boolean)
    # todo check aws timezone
    def create_user_by_email(self,full_name, email, password):
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

    # TODO : Move this two method into mongodb

    # Get device_uuid from writekey in DynamoDB
    # input parameter : write_key(string)
    # return : device_uuid(string)
    def get_device_uuid_by_write_key(self,write_key):
        table = self.client.Table(RUMAHIOT_DEVICE_TABLE)
        # get device data
        response = table.scan(
            FilterExpression=Key('write_key').eq(write_key),
        )
        # return the device_uuid
        return response['Items'][0]['device_uuid']

    # Get device_uuid from writekey in DynamoDB
    # input parameter : write_key(string)
    # return : device_uuid(string)
    def get_device_uuid_by_read_key(self, read_key):
        table = self.client.Table(RUMAHIOT_DEVICE_TABLE)
        # get device data
        response = table.scan(
            FilterExpression=Key('read_key').eq(read_key),
        )
        # return the device_uuid
        return response['Items'][0]['device_uuid']

    # Regenerate device read_key and write_key using device uuid
    # input parameter : device_uuid (string)

    def refresh_device_key(self,device_uuid):
        table = self.client.Table(RUMAHIOT_DEVICE_TABLE)
        # update the key
        response = table.update_item(
            Key={
                'device_uuid' : device_uuid
            },
            UpdateExpression="set write_key=:wk, read_key=:rk",
            ExpressionAttributeValues={
                ':wk': uuid4().hex,
                ':rk': uuid4().hex,
            },
            ReturnValues="UPDATED_NEW"
        )

    # Get device detail using device uuid
    # input parameter : device_uuid (string)
    # return :
    def get_device_detail(self,device_uuid):
        table = self.client.Table(RUMAHIOT_DEVICE_TABLE)
        # get the detail
        response = table.scan(
            FilterExpression = Key('device_uuid').eq(device_uuid),
        )
        return response['Items']