# -*- coding: utf-8 -*-
import enum
from abc import ABCMeta, abstractmethod
from typing import Union, List

from more_itertools import first_true

from votes.question_type import QuestionType

FACTORIES = []


def generate_voting_results_of_question(question: dict) -> dict:
    """
    質問から、その質問の投票結果を格納するためのDictを作成する関数です。
    :param question: 質問
    :return: 質問を元に作られた、その質問の投票結果を格納するためのDict
    """
    factory = first_true(FACTORIES, None, lambda f: f.get_question_type().value == question['type'])
    if not factory:
        raise ValueError(f'The answer of question factory for {question["type"]} is not implemented!')

    return factory.generate(question)


class VotingResultsOfQuestionFactory(metaclass=ABCMeta):
    """
    質問から、その質問の投票結果を格納するためのDictを作成する抽象クラスです。
    """
    @abstractmethod
    def get_question_type(self):
        raise NotImplementedError()

    @abstractmethod
    def _generate_results(self, question: dict) -> any:
        raise NotImplementedError()

    def generate(self, question: dict) -> dict:
        return {
            'type': self.get_question_type().value,
            'results': self._generate_results(question)
        }


class VotingResultsOfOneSelectQuestionFactory(VotingResultsOfQuestionFactory):
    def get_question_type(self):
        return QuestionType.ONE_SELECT

    def _generate_results(self, question: dict) -> any:
        results = [0] * len(question['options'])
        return results


FACTORIES.append(VotingResultsOfOneSelectQuestionFactory())
