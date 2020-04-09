# -*- coding: utf-8 -*-
import enum
from abc import ABCMeta, abstractmethod
from typing import Union, List

from votes.question_type import QuestionType

FACTORIES = []


def generate_voting_results_of_question(question: dict) -> dict:
    for factory in FACTORIES:
        if factory.get_question_type().value == question['type']:
            return factory.generate(question)

    raise ValueError(f'The answer of question factory for {question["type"]} is not implemented!')


class VotingResultsOfQuestionFactory(metaclass=ABCMeta):
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
