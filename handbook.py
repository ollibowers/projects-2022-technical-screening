"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: We do not expect you to come up with a perfect solution. We are more interested
in how you would approach a problem like this.
"""
import json

from process_condition import processCondition

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    
    # process the condition into a Prereq Rule object
    rule = processCondition(CONDITIONS[target_course])
    print(rule)

    # evaluate the rule
    courses_list_lower = list(map(lambda code: code.lower(), courses_list))
    return rule.check(set(courses_list_lower))

if __name__ == "__main__":
    for condition in CONDITIONS.values():
        print(processCondition(condition))
        print()

    print()
    print()
    print(processCondition(CONDITIONS["COMP3900"]))





    