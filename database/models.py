from mongoengine import *
from datetime import datetime

# def get_collection(dbname):
#     client = pymongo.MongoClient('localhost', '27017')
#     db = client.kgproject
#     database = db[dbname]
#     return database


class User(Document):
    _id = StringField(required=True)
    name = StringField(required=True)
    password = StringField(required=True)
    email = StringField(required=True)
    type = StringField(required=True)
    registrationDate = DateTimeField(default=datetime.now(), required=True)

    def insert(self):
        self.save()


class Teacher(Document):

    name = StringField(required=True)
    age = IntField(required=True)
    sex = StringField(required=True)
    skilled = StringField(required=True)
    num = IntField(default=0)


class Student(Document):

    name = StringField(required=True)
    specialized_subject = StringField(required=True)
    sex = StringField(required=True)
    age = IntField(required=True)
    school = StringField(required=True)
    email = StringField(required=True)
    Learning_resource_type = StringField()
    phone_number = StringField()
    behavior_pattern = StringField()
    background_knowledge = StringField()
    cognitive_level = StringField()
    learning_degree = StringField()
    search_history = StringField()
    answer_content = StringField()
    answer_liked = IntField(default=0)


class Project(Document):
    projectName = StringField(required=True)
    thumbnailUrl = StringField(required=True)
    userid = StringField(required=True)
    data = ObjectIdField()
    createDate = DateTimeField(default=datetime.now(), required=True)
    updateDate = DateTimeField(default=datetime.now())


class Material(Document):
    materialName = StringField(required=True)
    thumbnailUrl = StringField(required=True)
    userID = StringField(required=True)
    materialUrl = StringField(required=True)
    materialType = StringField(required=True)
    duration = StringField(required=True)


class Categories(Document):
    #继承Document类,为普通文档 '
    name = StringField(max_length=30, required=True)
    artnum = IntField(default=0, required=True)
    date = DateTimeField(default=datetime.now(), required=True)

