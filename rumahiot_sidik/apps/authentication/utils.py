import hashlib,uuid

# return salt(string),hashed_password(string)
# salt will be used as uuid in the user table
def password_hasher(salt,password):
    return hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()

# generate error response in dict format
def error_response_generator(code,message):
    response = {
        "error":{
            "code" : code,
            "message" : message
        }
    }
    return response

# generate data response in dict format
# input parameter data(dict)
def data_response_generator(data):
    response = {
        "data" : data
    }
    return response

# generate error response in dict format
def success_response_generator(code,message):
    response = {
        "success":{
            "code" : code,
            "message" : message
        }
    }
    return response