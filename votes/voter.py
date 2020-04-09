# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from votes.question_type import QuestionType

VOTER = []


def vote(voting_results: List[any], answers: List[any]):
    for voting_result, answer in zip(voting_results, answers):
        for voter in VOTER:
            if voter.get_question_type().value == voting_result['type']:
                voter.vote(voting_result, answer)
                return


class Voter(metaclass=ABCMeta):
    @abstractmethod
    def get_question_type(self):
        raise NotImplementedError()

    @abstractmethod
    def vote(self, voting_result: dict, answer: any) -> None:
        raise NotImplementedError()


class OneSelectQuestionVoter(Voter):
    def get_question_type(self):
        return QuestionType.ONE_SELECT

    def vote(self, voting_result: dict, answer: any) -> None:
        voting_result['results'][answer] = voting_result['results'][answer] + 1


VOTER.append(OneSelectQuestionVoter())
