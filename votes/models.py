import enum
import json
import traceback
from typing import List, Union

import bcrypt
import jsonschema
from bson import ObjectId
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from pymongo.database import Database

from users.models import User
from votes import voter
from votes.voting_results_of_question_generator import generate_voting_results_of_question

questions_schema = json.loads(open('./votes/questions_schema.json', 'r').read())


class Vote(models.Model):
    creator = models.ForeignKey(to=User, on_delete=models.PROTECT, null=True, blank=False)
    title = models.CharField(max_length=256, null=False, blank=False)
    password = models.CharField(max_length=60, null=False, blank=False)
    __questions_id = models.CharField(max_length=24, blank=False, null=False, name='questions_id')
    __voting_results_id = models.CharField(max_length=24, blank=False, null=False, name='voting_results_id')
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), settings.BCRYPT_SALT)

    def set_questions(self, questions: List[dict]):
        mongodb: Database = settings.MONGODB

        # 質問のDictを作成
        questions_json = {'_': questions}

        # 質問の答えを格納するDictの作成
        voting_results = [generate_voting_results_of_question(q) for q in questions]
        voting_results_json = {'_': voting_results}

        # 質問をデータベースに保存
        questions_id = mongodb.questions_list.insert_one(
            questions_json
        ).inserted_id
        self.questions_id = questions_id

        # 質問の答えを格納するDictをデータベースに保存
        voting_results_id = mongodb.voting_results_list.insert_one(
            voting_results_json
        ).inserted_id
        self.voting_results_id = voting_results_id

    def get_questions(self):
        mongodb: Database = settings.MONGODB
        questions: Union[dict, None] = mongodb.questions_list.find_one({"_id": ObjectId(self.questions_id)})

        return questions['_']

    def get_voting_results(self):
        mongodb: Database = settings.MONGODB
        voting_results: Union[dict, None] = mongodb.voting_results_list.find_one({"_id": ObjectId(self.voting_results_id)})

        return voting_results['_']

    def update_voting_results(self, voting_results: List[any]):
        mongodb: Database = settings.MONGODB

        mongodb.voting_results_list.update_one(
            {"_id": ObjectId(self.voting_results_id)},
            {'$set': {'_': voting_results}},
            upsert=True
        )

    def vote(self, answers: List[any]):
        voting_results = self.get_voting_results()
        voter.vote(voting_results, answers)
        self.update_voting_results(voting_results)

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
    try:
        mongodb.questions_list.delete_one({'_id': ObjectId(instance.questions_id)})
    except:
        traceback.print_exc()
    try:
        mongodb.voting_results_list.delete_one({'_id': ObjectId(instance.voting_results_id)})
    except:
        traceback.print_exc()
