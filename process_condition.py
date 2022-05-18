import re
from typing import Any, Dict, Tuple, Optional
from prereq_rules import PrereqRule, RuleAND, RuleCourse, RuleNone, RuleOR, RuleUOC, RuleUOCinList, RuleUOCinPattern

PREDEFINED_RULES = {
    "4951": RuleCourse("comp4951"),
    "4952": RuleCourse("comp4952"),
    "18 units oc credit in (COMP9417, COMP9418, COMP9444, COMP9447)": RuleUOCinList(18, ["comp9417", "comp9418", "comp9444", "comp9447"])
}

def processCondition(condition: str) -> PrereqRule:
    """Main entry point, processes a condition string to a PrereqRule which can then be evaluated. If too hard, will use pre defined"""
    # check predefined
    predefined = getPredefined(condition)
    if predefined is not None:
        return predefined

    # clean up the string
    condition = cleanup(condition)

    # replace the subgroups with identifiers forming a sort of subgroup tree
    condition, subgroupConditions = identifySubgroups(condition)

    # recursively evaluate the tree now
    return preprocessedConditionToRule(condition, subgroupConditions)



def getPredefined(condition: str) -> Optional[PrereqRule]:
    """check if the condition has a premade Rule object"""
    # matched on condition instead of course to allow for duplicates and changes of handbook to invalidate
    return PREDEFINED_RULES.get(condition)



def cleanup(condition: str) -> str:
    """Returns a cleaned up version of the condition string"""
    condition = condition.lower()
    condition = re.sub(" +", " ", condition)  # strip the excess spaces
    condition = re.sub("p.*: ", "", condition)  # strip the Prereq prefix, this might break terribly
    condition = condition.replace(".", "")  # strip full stops
    condition = condition.replace("completion of ", "")  # remove the "completion of" before a uoc
    return condition



def identifySubgroups(condition: str) -> Tuple[str, Dict[int, str]]:
    """Replaces all the subgroups with ids and returns the new condition str as well as the subgroups"""
    subgroupRules = {}
    while re.search("\([a-z0-9\[\] ]+\)", condition):
        for subgroupCondition in re.findall("\([a-z0-9\[\] ]+\)", condition):
            # replace the subgroup with an id that is mapped to its string
            subgroupID = len(subgroupRules)
            subgroupRules[subgroupID] = subgroupCondition[1:-1]
            condition = condition.replace(subgroupCondition, f"[{subgroupID}]")
    return (condition, subgroupRules)



def preprocessedConditionToRule(condition: str, subgroupConditions: Dict[int, str]) -> Any:
    """Converts a preprocessed condition string to a PrereqRule"""

    if condition == "":
        return RuleNone()
    if re.match("\([a-z0-9\[\] ]+\)", condition):
        raise Exception("Condition should not have any subgroups still to be processed!")

    # if no conjunctions or subgroups, then its at lowest level rule, create a PrereqRule from it
    if (not re.search(" and | or ", condition)) and (not re.search("\[\d+\]", condition)):
        if re.search("^[a-z]{4}\d{4}$", condition):
            # eg "COMP1531"
            return RuleCourse(condition)
        elif re.search("^\d+ units of credit in \(", condition):
            # eg "12 uoc in (comp1511, comp1521, comp1531)"
            uoc = int(re.match("^\d+", condition).group(0))
            options = re.search("\(.+\)$", condition).group(0)[1:-1].split(", ")
            return RuleUOCinList(uoc, options)
        elif re.search("^\d+ units of credit in( level \d)? [a-z]+ courses$", condition):
            # eg "12 uoc in level 1 comp courses" | "12 uoc in comp courses"
            uoc = int(re.match("^\d+", condition).group(0))
            pattern = re.search("[a-z]+ courses", condition).group(0).replace(" courses", "")
            level = re.search("level \d", condition)
            if level is not None:
                # include level in pattern
                pattern += level.group(0)[-1]
            return RuleUOCinPattern(uoc, pattern)
        elif re.search("^\d+ units of credit$", condition):
            # eg "12 units of credit", checked after all other uoc are parsed
            uoc = int(re.match("^\d+", condition).group(0))
            return RuleUOC(uoc)
        else:
            # unknown base level rule
            raise NotImplementedError("Unimplemented base condition:", condition)

    # should only be base conditions / subgroup ids joined by either "and" or "or"
    # evaluate each subrule recursively
    subrules = []
    for subrule in re.split(" and | or ", condition):
        # check if its a rule comprised of a subgroup
        if re.match("^\[\d+\]$", subrule):
            subrule = subgroupConditions[int(subrule[1:-1])]
        subrules.append(preprocessedConditionToRule(subrule, subgroupConditions))

    # convert the joined subrules into a rule and return it omg
    if "and" in condition:
        return RuleAND(set(subrules))
    elif "or" in condition:
        return RuleOR(set(subrules))

    raise NotImplementedError("This should never be reached!!!")
    