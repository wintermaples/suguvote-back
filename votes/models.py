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
from rest_framework.exceptions import ValidationError

from common.session import get_or_create_session_id
from users.models import User
from votes import voter
from votes.validators import validate_tags
from votes.voting_results_of_question_generator import generate_voting_results_of_question

questions_schema = json.loads(open('./votes/questions_schema.json', 'r').read())
answers_schema = json.loads(open('./votes/answers_schema.json', 'r').read())


class Vote(models.Model):
    creator = models.ForeignKey(to=User, on_delete=models.PROTECT, null=True, blank=False)
    title = models.CharField(max_length=256, null=False, blank=False)
    password = models.CharField(max_length=60, null=False, blank=False)
    description = models.TextField(max_length=512, blank=False, null=False)
    tags = models.CharField(max_length=(settings.MAX_TAG_LENGTH + 1)*settings.MAX_TAG_COUNT, null=False, blank=False, validators=[validate_tags])
    __questions_id = models.CharField(max_length=24, blank=False, null=False, name='questions_id')
    __voting_results_id = models.CharField(max_length=24, blank=False, null=False, name='voting_results_id')
    closing_at = models.DateTimeField(blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)
    vote_count = models.IntegerField(null=False, default=0)

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), settings.BCRYPT_SALT).decode("utf-8")

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode("UTF-8"), self.password.encode("UTF-8"))

    def set_questions(self, questions: List[dict]):
        '''
        質問を設定します。既に作成された質問はすべて置き換えられ、今までの質問への回答も上書きされ初期化されます。
        :param questions: 質問のリスト
        '''
        mongodb: Database = settings.MONGODB_CONNECTOR.connect_and_get_db()

        # 質問のDictを作成
        questions_json = {'_': questions}

        # 質問の答えを格納するDictの作成
        voting_results = [generate_voting_results_of_question(q) for q in questions]
        voting_results_json = {'_': voting_results}

        # 質問をデータベースに保存
        questions_id = mongodb.questions_list.update_one(
            {"_id": ObjectId(self.questions_id) if self.questions_id else ObjectId()},
            {'$set': questions_json},
            upsert=True
        ).upserted_id
        self.questions_id = questions_id

        # 質問の答えを格納するDictをデータベースに保存
        voting_results_id = mongodb.voting_results_list.update_one(
            {"_id": ObjectId(self.voting_results_id) if self.voting_results_id else ObjectId()},
            {'$set': voting_results_json},
            upsert=True
        ).upserted_id
        self.voting_results_id = voting_results_id

    def get_questions(self):
        mongodb: Database = settings.MONGODB_CONNECTOR.connect_and_get_db()
        questions: Union[dict, None] = mongodb.questions_list.find_one({"_id": ObjectId(self.questions_id)})

        return questions['_']

    def get_voting_results(self):
        mongodb: Database = settings.MONGODB_CONNECTOR.connect_and_get_db()
        voting_results: Union[dict, None] = mongodb.voting_results_list.find_one({"_id": ObjectId(self.voting_results_id)})

        return voting_results['_']

    def update_voting_results(self, voting_results: List[any]):
        mongodb: Database = settings.MONGODB_CONNECTOR.connect_and_get_db()

        mongodb.voting_results_list.update_one(
            {"_id": ObjectId(self.voting_results_id)},
            {'$set': {'_': voting_results}},
            upsert=True
        )

    def vote(self, answers: List[any]):
        voting_results = self.get_voting_results()
        voter.vote(voting_results, answers)
        self.update_voting_results(voting_results)
        self.vote_count += 1

    @classmethod
    def validate_questions(cls, questions: List[dict]):
        questions_str = str(questions).replace("'", '"')
        questions_json = json.loads(f'{{"_":{questions_str}}}')
        try:
            jsonschema.validate(
                instance=questions_json,
                schema=questions_schema
            )
        except:
            raise ValidationError('Invalid questions structure.')

    @classmethod
    def validate_answers(cls, answers: List[any]):
        answers_str = str(answers).replace("'", '"')
        answers_json = json.loads(f'{{"_":{answers_str}}}')
        try:
            jsonschema.validate(
                instance=answers_json,
                schema=answers_schema
            )
        except:
            raise ValidationError('Invalid answers structure.')

    def is_voted_by(self, request):
        if request.user.is_anonymous:
            if VotingHistory.objects.filter(vote=self,
                                            anonymous_user_session_id=get_or_create_session_id(request)).exists():
                return True
        else:
            if VotingHistory.objects.filter(vote=self, user=request.user).exists():
                return True
        return False

class VotingHistory(models.Model):
    vote = models.ForeignKey(to=Vote, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.PROTECT, null=True)
    anonymous_user_session_id = models.CharField(max_length=12, null=True, blank=False)


@receiver(pre_delete, sender=Vote)
def post_delete(sender, instance, **kwargs):
    mongodb: Database = settings.MONGODB_CONNECTOR.connect_and_get_db()
    try:
        mongodb.questions_list.delete_one({'_id': ObjectId(instance.questions_id)})
    except:
        traceback.print_exc()
    try:
        mongodb.voting_results_list.delete_one({'_id': ObjectId(instance.voting_results_id)})
    except:
        traceback.print_exc()
