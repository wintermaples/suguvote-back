import json
from typing import List

import bcrypt
import jsonschema
from bson import ObjectId
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from pymongo.database import Database

from users.models import User

questions_schema = json.loads(open('./votes/questions_schema.json', 'r').read())


class Vote(models.Model):
    creator = models.ForeignKey(to=User, on_delete=models.PROTECT, null=True, blank=False)
    title = models.CharField(max_length=256, null=False, blank=False)
    password = models.CharField(max_length=60, null=False, blank=False)
    __questions_id = models.CharField(max_length=24, blank=False, null=False, name='questions_id')
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), settings.BCRYPT_SALT)

    def set_questions(self, questions: List[dict]):
        questions_str = str(questions).replace("'", '"')
        questions_json = json.loads(f'{{"_":{questions_str}}}')  # {"_": [QUESTIONS...]}の形式で保存

        mongodb: Database = settings.MONGODB
        questions_id = mongodb.questions_set.insert_one(
            questions_json
        ).inserted_id
        self.questions_id = questions_id

    def get_questions(self):
        mongodb: Database = settings.MONGODB
        questions = mongodb.questions_set.find_one({"_id": ObjectId(self.questions_id)})

        return questions['_']

    @classmethod
    def validate_questions(cls, questions: List[dict]):
        questions_str = str(questions).replace("'", '"')
        questions_json = json.loads(f'{{"_":{questions_str}}}')
        try:
            jsonschema.validate(
                instance=questions_json,
                schema=questions_schema
            )
            return True
        except:
            return False


@receiver(pre_delete, sender=Vote)
def post_delete(sender, instance, **kwargs):
    mongodb: Database = settings.MONGODB
    mongodb.questions_set.delete_one({'_id': ObjectId(instance.questions_id)})
