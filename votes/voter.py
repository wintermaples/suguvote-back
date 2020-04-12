# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

from more_itertools import first_true

from votes.question_type import QuestionType

VOTER = []


def vote(voting_results: List[any], answers: List[any]) -> None:
    """
    voting_resultsに対して、回答を与えて、投票をします。
    この関数は直接voting_resultsを変更します。
    :param voting_results: 投票結果
    :param answers: 回答
    """
    for voting_result, answer in zip(voting_results, answers):
        voter = first_true(VOTER, None, lambda v: v.get_question_type().value == voting_result['type'])
        if not voter:
            raise ValueError(f'The voter of {voting_result["type"]} is not implemented!')
        voter.vote(voting_result, answer)


class Voter(metaclass=ABCMeta):
    """
    投票結果に対して、回答が与えられた時に、投票するための処理をする抽象クラスです。
    """
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
