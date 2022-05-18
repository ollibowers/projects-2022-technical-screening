import re
from typing import List, Set


def getUOC(courseCode: str) -> int:
    """Returns the course codes UOC, constant 6 for now"""
    return 6


class PrereqRule:
    """Base class for a prerequisite rule. Doesn't get used aside from being a parent class."""

    def check(self, completed: Set[str]) -> bool:
        """Evaluates the rule, takes a Set of completed course codes and checks whether the rule is fulfilled."""
        return False


class RuleNone(PrereqRule):
    """Dummy Rule for courses without a prereq, to help maintain structure"""
    def check(self, completed: Set[str]) -> bool:
        # just return true as there are no rules to act ually check
        return True

    def __repr__(self) -> str:
        return "RuleNone()"


class RuleCourse(PrereqRule):
    """Basic course fulfilment rule."""
    __course: str

    def __init__(self, course: str) -> None:
        self.__course = course

    def check(self, completed: Set[str]) -> bool:
        # check if the required course is in the completed courses
        return self.__course in completed

    def __repr__(self) -> str:
        return f"RuleCourse(course='{self.__course}')"


class RuleOR(PrereqRule):
    """The OR rule"""
    __children: Set[PrereqRule]

    def __init__(self, options: Set[PrereqRule]) -> None:
        self.__children = options

    def check(self, completed: Set[str]) -> bool:
        # check if any of the children rules are fulfilled
        return any(
            map(lambda childRule: childRule.check(completed), self.__children)
        )

    def __repr__(self) -> str:
        return f"RuleOR(options='{list(self.__children)}')"


class RuleAND(PrereqRule):
    """The AND rule"""
    __children: Set[PrereqRule]

    def __init__(self, options: Set[PrereqRule]) -> None:
        self.__children = options

    def check(self, completed: Set[str]) -> bool:
        # check if all of the children rules are fulfilled
        return all(
            map(lambda childRule: childRule.check(completed), self.__children)
        )

    def __repr__(self) -> str:
        return f"RuleAND(options='{list(self.__children)}')"


class RuleUOC(PrereqRule):
    """The UOC completed rule"""
    __amount: int

    def __init__(self, minUOC: int) -> None:
        self.__amount = minUOC

    def check(self, completed: Set[str]) -> bool:
        # count the amount of UOC completed and check if its >= the required amount
        completedAmount = sum(map(getUOC, completed))
        return completedAmount >= self.__amount

    def __repr__(self) -> str:
        return f"RuleUOC(minUOC='{self.__amount}')"


class RuleUOCinPattern(PrereqRule):
    """The UOC in Degree/Level of course, uses a Regex pattern"""
    __amount: int
    __pattern: str

    def __init__(self, minUOC: int, pattern: str) -> None:
        self.__amount = minUOC
        self.__pattern = pattern

    def check(self, completed: Set[str]) -> bool:
        # count UOC of completed that match pattern, and check >=
        relevantCompleted = filter(
            lambda code: (re.match(self.__pattern, code) is not None),
            completed
        )
        completedAmount = sum(map(getUOC, relevantCompleted))
        return completedAmount >= self.__amount

    def __repr__(self) -> str:
        return f"RuleUOCinPattern(minUOC='{self.__amount}', pattern='{self.__pattern}')"


class RuleUOCinList(PrereqRule):
    """The UOC completed in a list of courses rule"""
    __amount: int
    __options: List[str]

    def __init__(self, minUOC: int, options: List[str]) -> None:
        self.__amount = minUOC
        self.__options = options

    def check(self, completed: Set[str]) -> bool:
        # count the UOC of completed that are also options
        relevantCompleted = filter(
            lambda code: (code in self.__options),
            completed
        )
        completedAmount = sum(map(getUOC, relevantCompleted))
        return completedAmount >= self.__amount

    def __repr__(self) -> str:
        return f"RuleUOCinList(minUOC='{self.__amount}', options='{self.__options}')"
