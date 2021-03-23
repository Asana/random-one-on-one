from __future__ import print_function
import unittest

from oneonone.construct_matches import ConstructMatches

Same = "SameTeam"
Other = "OtherTeam"


def member_id(m):
    return m["id"]


def get_custom_field(member, name, default=None):
    return member[name] if member.get(name) else default


def create_members(list_of_members):
    return [{"id": i} for i in list_of_members]


def create_members_with_preferences(list_of_members):
    # list_of_members is a list of ["id", "Team", option] where option is an integer either 0 or 1
    options = {Same: "Only match with same team", Other: "Only match with other teams"}
    return [
        {"id": member[0], "Team": member[1], "Match Preference": options.get(member[2])}
        for member in list_of_members
    ]


class TestConstructMatches(unittest.TestCase):
    def _assert(self, m, members, data, unmatched):
        matched_members = [member["id"] for member in m.matched_members]
        unmatched_member = m.unmatched_member["id"] if m.unmatched_member else None
        self.assertEqual(matched_members, members)
        self.assertEqual(m.match_data, data)
        self.assertEqual(unmatched_member, unmatched)

    def test_construct_match_for_one_member_returns_member_as_unmatched(self):
        m = ConstructMatches(create_members(["A"]), {}, member_id, get_custom_field)
        m.construct_matches()
        expected_data = {"unmatched": "A"}
        self._assert(m, [], expected_data, "A")

    def test_construct_match_for_two_members_returns_them_as_match(self):
        previous_matches = {"A": "B"}
        members = create_members(["A", "B"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"A": "B", "B": "A"}
        expected_matches = ["B", "A"]
        self._assert(m, expected_matches, expected_data, None)

    def test_previous_unmatched_doesnt_change_if_no_unmatch_member_this_time(self):
        previous_matches = {"A": "B", "unmatched": "C"}
        members = create_members(["A", "B"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"A": "B", "B": "A", "unmatched": "C"}
        expected_matches = ["B", "A"]
        self._assert(m, expected_matches, expected_data, None)

    def test_first_match_valid_leaving_last_member_unmatched(self):
        previous_matches = {}
        members = create_members(["A", "B", "C"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"A": "C", "C": "A", "unmatched": "B"}
        expected_matches = ["C", "A"]
        self._assert(m, expected_matches, expected_data, "B")

    def test_first_match_valid_leaving_last_member_unmatched_keeps_its_previous_match(
        self,
    ):
        previous_matches = {"B": "E"}
        members = create_members(["A", "B", "C"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"A": "C", "C": "A", "B": "E", "unmatched": "B"}
        expected_matches = ["C", "A"]
        self._assert(m, expected_matches, expected_data, "B")

    def test_no_valid_match_defaults_on_last_match_possible(self):
        previous_matches = {"A": "C", "C": "B", "B": "A"}
        members = create_members(["A", "B", "C"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"A": "B", "B": "A", "C": "B", "unmatched": "C"}
        expected_matches = ["B", "A"]
        self._assert(m, expected_matches, expected_data, "C")

    def test_last_match_invalid_so_break_up_a_valid_match_and_rematch(self):
        previous_matches = {"B": "C"}
        members = create_members(["A", "B", "C", "D"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"D": "C", "C": "D", "B": "A", "A": "B"}
        expected_matches = ["C", "D", "A", "B"]
        self._assert(m, expected_matches, expected_data, None)

    def test_last_match_invalid_and_cannot_break_up_anything_results_in_a_match_anyway(
        self,
    ):
        previous_matches = {"A": "B", "B": "A", "C": "A", "D": "A"}
        members = create_members(["A", "B", "C", "D"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"D": "B", "B": "D", "A": "C", "C": "A"}
        expected_matches = ["D", "B", "C", "A"]
        self._assert(m, expected_matches, expected_data, None)

    def test_unmatchable_member_and_an_odd_one_out_get_matched(self):
        previous_matches = {"A": "B", "B": "A", "C": "A", "D": "A"}
        members = create_members(["B", "C", "D", "A"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"D": "B", "B": "D", "A": "C", "C": "A"}
        expected_matches = ["D", "B", "C", "A"]
        self._assert(m, expected_matches, expected_data, None)

    def test_unmatchable_member_will_become_the_odd_one_out(self):
        previous_matches = {"A": "B", "B": "A", "C": "A", "D": "A", "E": "A"}
        members = create_members(["B", "C", "D", "E", "A"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {
            "A": "B",
            "E": "B",
            "B": "E",
            "D": "C",
            "C": "D",
            "unmatched": "A",
        }
        expected_matches = ["E", "B", "D", "C"]
        self._assert(m, expected_matches, expected_data, "A")

    def test_last_two_matches_not_possible_so_break_up_and_rematch_twice(self):
        previous_matches = {"B": "E", "C": "E", "E": "D", "D": "C"}
        members = create_members(["A", "B", "C", "D", "E", "F"])
        m = ConstructMatches(members, previous_matches, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"A": "D", "D": "A", "E": "F", "F": "E", "B": "C", "C": "B"}
        expected_matches = ["E", "F", "D", "A", "B", "C"]
        self._assert(m, expected_matches, expected_data, None)

    def test_only_match_with_team_members(self):
        members = create_members_with_preferences(
            [["A", "T1", Same], ["B", "T2", Same], ["C", "T1", Same], ["D", "T2", Same]]
        )
        m = ConstructMatches(members, {}, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"D": "B", "B": "D", "C": "A", "A": "C"}
        expected_matches = ["D", "B", "C", "A"]
        self._assert(m, expected_matches, expected_data, None)

    def test_only_match_with_other_team(self):
        members = create_members_with_preferences(
            [
                ["A", "T2", Other],
                ["B", "T1", Other],
                ["C", "T1", Other],
                ["D", "T2", Other],
            ]
        )
        m = ConstructMatches(members, {}, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"D": "B", "B": "D", "C": "A", "A": "C"}
        expected_matches = ["D", "B", "C", "A"]
        self._assert(m, expected_matches, expected_data, None)

    def test_unmatchable_member_will_match_with_a_previous_unmatchable_member(self):
        members = create_members_with_preferences(
            [
                ["A", "T1", Other],
                ["B", "T1", Other],
                ["C", "T1", Other],
                ["D", "T1", Other],
            ]
        )
        m = ConstructMatches(members, {}, member_id, get_custom_field)
        m.construct_matches()

        expected_data = {"C": "D", "D": "C", "B": "A", "A": "B"}
        expected_matches = ["C", "D", "B", "A"]
        self._assert(m, expected_matches, expected_data, None)

    """
    Lets test compatible_match_preferences for all possible outcomes
    Legend:
        T1, T2 = Member has team field set
        P1, P2 = Member has preference field set
        R = Result where 0 is not compatible match and 1 is a compatible match
        ? = Can be either 0 or 1 but won't change the Result. Example a 0 ? =  0 0 and 0 1
        
    Case T1 P1 T2 P2 | R   Reason
    1    0  ?  ?  ?  | 1   Member1 has no Team, matchable
    2    ?  ?  0  ?  | 1   Member2 has no Team, matchable
    3    ?  0  ?  0  | 1   Neither have preferences, matchable
    4    1  1  1  0  | ?   Both have Team, member1 has Preference, possible match
    5    1  0  1  1  | ?   Both have Team, member2 has Preference, possible match
    6    1  1  1  1  | ?   Both have Team and Preference, possible match
    """

    def test_members_without_the_team_field_results_in_a_match(self):
        # Test all combinations of Case 1 and 2
        # All combinations of one member having no Team
        members1 = create_members_with_preferences(
            [["A", None, None], ["B", None, None]]
        )
        members2 = create_members_with_preferences(
            [["A", None, None], ["B", None, Same]]
        )
        members3 = create_members_with_preferences(
            [["A", None, None], ["B", "T1", None]]
        )
        members4 = create_members_with_preferences(
            [["A", None, None], ["B", "T1", Same]]
        )
        members5 = create_members_with_preferences(
            [["A", None, Same], ["B", None, None]]
        )
        members6 = create_members_with_preferences(
            [["A", None, Same], ["B", None, Same]]
        )
        members7 = create_members_with_preferences(
            [["A", None, Same], ["B", "T1", None]]
        )
        members8 = create_members_with_preferences(
            [["A", None, Same], ["B", "T1", Same]]
        )

        memberA_no_team_no_preference = [
            members1,
            members2,
            members3,
            members4,
            members5,
            members6,
            members7,
            members8,
        ]
        m = ConstructMatches([], {}, member_id, get_custom_field)

        error_msg = (
            "MemberA is without a team, should be a compatible match with MemberB: {}"
        )
        for member_pair in memberA_no_team_no_preference:
            # All possible combination of Case 1
            match_result = m.compatible_match_preferences(
                member_pair[0], member_pair[1]
            )
            self.assertTrue(match_result, error_msg.format(member_pair[1]))
            # All possible combination of Case 2 (by switching A and B)
            match_result = m.compatible_match_preferences(
                member_pair[1], member_pair[0]
            )
            self.assertTrue(match_result, error_msg.format(member_pair[1]))

    def test_neither_member_has_set_the_preference_field(self):
        # Test all combinations of Case 3
        members1 = create_members_with_preferences(
            [["A", None, None], ["B", None, None]]
        )
        members2 = create_members_with_preferences(
            [["A", None, None], ["B", "T1", None]]
        )
        members3 = create_members_with_preferences(
            [["A", "T1", None], ["B", None, None]]
        )
        members4 = create_members_with_preferences(
            [["A", "T1", None], ["B", "T1", None]]
        )

        m = ConstructMatches([], {}, member_id, get_custom_field)

        error_msg = "Neither member has any preference and should therefor be a match"
        for member_pair in [members1, members2, members3, members4]:
            result = m.compatible_match_preferences(member_pair[0], member_pair[1])
            self.assertTrue(result, error_msg)
            result = m.compatible_match_preferences(member_pair[1], member_pair[0])
            self.assertTrue(result, error_msg)

    def test_both_members_have_teams_only_one_has_preferences(self):
        # Test all combinations of Case 4 and 5
        # On the same team, one wants to match with members from same team
        members1 = create_members_with_preferences(
            [["A", "T1", Same], ["B", "T1", None]]
        )
        # Not on the same team, one wants to match with members from same team
        members2 = create_members_with_preferences(
            [["A", "T1", Same], ["B", "T2", None]]
        )
        # On the same team, one wants to match with members from another team
        members3 = create_members_with_preferences(
            [["A", "T1", Other], ["B", "T1", None]]
        )
        # Not on the same team, one wants to match with members from another team
        members4 = create_members_with_preferences(
            [["A", "T1", Other], ["B", "T2", None]]
        )

        m = ConstructMatches([], {}, member_id, get_custom_field)

        self.assertTrue(m.compatible_match_preferences(members1[0], members1[1]))
        self.assertTrue(m.compatible_match_preferences(members1[1], members1[0]))

        self.assertFalse(m.compatible_match_preferences(members2[0], members2[1]))
        self.assertFalse(m.compatible_match_preferences(members2[1], members2[0]))

        self.assertFalse(m.compatible_match_preferences(members3[0], members3[1]))
        self.assertFalse(m.compatible_match_preferences(members3[1], members3[0]))

        self.assertTrue(m.compatible_match_preferences(members4[0], members4[1]))
        self.assertTrue(m.compatible_match_preferences(members4[1], members4[0]))

    def test_both_members_have_teams_and_preferences(self):
        # Test all combinations of Case 6
        # On the same team, one wants to match with members from same team, the other doesn't
        members1 = create_members_with_preferences(
            [["A", "T1", Same], ["B", "T1", Other]]
        )
        # On the same team, both want to match with members from same team
        members2 = create_members_with_preferences(
            [["A", "T1", Same], ["B", "T1", Same]]
        )
        # Not on the same team, one wants to match with members from same team, the other doesn't
        members3 = create_members_with_preferences(
            [["A", "T1", Same], ["B", "T2", Other]]
        )
        # Not on the same team, both want to match with members from other teams
        members4 = create_members_with_preferences(
            [["A", "T1", Other], ["B", "T2", Other]]
        )

        m = ConstructMatches([], {}, member_id, get_custom_field)

        self.assertFalse(m.compatible_match_preferences(members1[0], members1[1]))
        self.assertTrue(m.compatible_match_preferences(members2[0], members2[1]))
        self.assertFalse(m.compatible_match_preferences(members3[0], members3[1]))
        self.assertTrue(m.compatible_match_preferences(members4[0], members4[1]))


if __name__ == "__main__":
    unittest.main()
