class ConstructMatches(object):
    def __init__(self, members, previous_matches, member_id, get_custom_field_value):
        """
        :param members: A list of members objects.
        :param previous_matches: A dict of ids for members. Contains id:id and an optional unmatched:id.
         Where id:id represents matches between ids of members.
        {"A": "B", "B": "C", unmatched: "D"} means A's last match was B but B's last match was C, and D was last unmatched member
        :param member_id: A function that can take in a member and return an id for that member
        """
        self.members = members
        self.previous_match_data = previous_matches
        self.member_id = member_id
        self._get_custom_field_value = get_custom_field_value

        # List of members objects that have been matched. [A, B, C, D] is a match of A:B and C:D
        self.matched_members = []
        # Updated version of previous_match_data with new matches and unmatched member
        self.match_data = {}
        # A member object that didn't get any match
        self.unmatched_member = None

    def got_matched_last_time(self, member1, member2):
        m_id1, m_id2 = self.member_id(member1), self.member_id(member2)
        return (
            self.previous_match_data.get(m_id1) == m_id2
            or self.previous_match_data.get(m_id2) == m_id1
        )

    def compatible_match_preferences(self, member1, member2):
        """Checks if match preferences between 2 given members are compatible"""

        no_team = "None (default)"
        m1_team = self._get_custom_field_value(member1, "Team", no_team)
        m2_team = self._get_custom_field_value(member2, "Team", no_team)
        m1_team = None if m1_team == no_team else m1_team
        m2_team = None if m2_team == no_team else m2_team

        if m1_team is None or m2_team is None:
            # Preferences require a Team field to be set on both members in order to compare
            # Teams with Preferences
            return True

        no_preference = "No preference (default)"
        only_same_team_preference = "Only match with same team"
        only_other_teams_preference = "Only match with other teams"

        m1_preference = self._get_custom_field_value(
            member1, "Match Preference", no_preference
        )
        m2_preference = self._get_custom_field_value(
            member2, "Match Preference", no_preference
        )
        m1_preference = None if m1_preference == no_preference else m1_preference
        m2_preference = None if m2_preference == no_preference else m2_preference

        if m1_preference is None and m2_preference is None:
            return True  # Both members have no preferences and are therefor a suitable match

        # We now know that both members have set their Team field and at least one of them
        # has any preference. Lets find out if any Preference makes this an incompatible match
        are_on_same_team = m1_team == m2_team
        if are_on_same_team and only_other_teams_preference not in [
            m1_preference,
            m2_preference,
        ]:
            return True  # Team members that are ok with being matched with other team members
        if not are_on_same_team and only_same_team_preference not in [
            m1_preference,
            m2_preference,
        ]:
            return True  # Not team members that are ok with being matched outside of their team

        return False

    def can_be_matched(self, m1, m2):
        # Check if 2 members did not get matched last time and have compatible match preferences
        return not self.got_matched_last_time(
            m1, m2
        ) and self.compatible_match_preferences(m1, m2)

    def match(self, m1, m2):
        self.matched_members.extend([m1, m2])
        self.match_data[self.member_id(m2)] = self.member_id(m1)
        self.match_data[self.member_id(m1)] = self.member_id(m2)

    def find_and_create_valid_match_for_member(self, m1):
        for i, m2 in enumerate(self.members):
            if self.can_be_matched(m1, m2):
                self.match(m1, self.members.pop(i))
                return True
        return False

    def try_to_break_up_and_create_a_new_match(self, m1, m2, m3):
        """
        :param m1: an unmatched member.
        :param m2: Member matched with m3. m1 is trying to match with m2
        :param m3: Member matched with m2

        m1 is trying to match with m2 by trying to break an existing match between m2 and m3.
        If there exist another unmatched member, m4, that m3 can match with,
        we create new matches m1:m2 and m3:m4.

        Now m4 has been matched but the caller of this function needs to handle
        the logic to break up m2:m3

        :return: True if new matches were made, False otherwise
        """
        if self.can_be_matched(m1, m2):
            for i, m4 in enumerate(self.members):
                if self.can_be_matched(m3, m4):
                    self.match(m1, m2)
                    self.match(m3, m4)
                    self.members.pop(i)  # Remove m4 from members since it got matched
                    return True
        return False

    def find_and_create_match_that_breaks_up_and_rematches_member(self, m1):
        # m1 is an unmatched member trying to break up an existing match and match with either
        # of the two, if the remaining one can match with another unmatched member
        for i, x in enumerate(self.matched_members):
            # We only need every other matched member since they come in pairs
            if i % 2 == 1:
                continue
            m2 = self.matched_members[i]
            m3 = self.matched_members[i + 1]
            # First we try and see if m1 can match with m2 and then if m1 can match with m3
            # If either is possible we break up the match for m2:m3
            if self.try_to_break_up_and_create_a_new_match(
                m1, m2, m3
            ) or self.try_to_break_up_and_create_a_new_match(m1, m3, m2):
                # Break up this match since they got matched with m1 and another available member
                self.matched_members.pop(i + 1)
                self.matched_members.pop(i)
                return True
        return False

    def construct_matches(self):
        if len(self.members) == 2:
            # only 2 members, lets match them
            self.match(self.members.pop(), self.members.pop())
        if len(self.members) == 1:
            self.unmatched_member = self.members.pop()

        while len(self.members):
            member1 = self.members.pop()  # Lets match this member with someone
            if len(self.members):
                # We try to match with any of the remaining members
                if self.find_and_create_valid_match_for_member(member1):
                    continue
                # Try to break up a match to do a new match
                if self.find_and_create_match_that_breaks_up_and_rematches_member(
                    member1
                ):
                    continue
                # Edge case, no valid match can be made between the last two and the rest so they get matched
                elif len(self.members) == 1:
                    self.match(member1, self.members.pop())
                # Edge case, no valid match can be made for this member and remaining members. Matching with unmatched
                elif self.unmatched_member is not None:
                    self.match(member1, self.unmatched_member)
                    self.unmatched_member = None
                else:
                    # This member is not viable for any matches
                    # Can happen due to low member count, frequency differences, match preferences
                    # Leave as unmatched since lowest priority match.
                    # Will end up:
                    #   * getting matched with the next unmatchable member
                    #   * getting matched with the last member
                    #   * becoming the odd one out
                    self.unmatched_member = member1
            else:
                # Odd one out
                if self.unmatched_member is not None:
                    # The unmatched member was involved in all possible matches.
                    # Lets match the last one with the unmatched since we rather want some than none
                    self.match(member1, self.unmatched_member)
                    self.unmatched_member = None
                else:
                    # Last one standing, gets priority next week.
                    self.unmatched_member = member1

        # Don't overwrite previous matches for members not getting matches this week
        tmp = self.previous_match_data.copy()
        tmp.update(self.match_data)
        self.match_data = tmp

        if self.unmatched_member:
            # There is a problem here. If the previous unmatched member was not a part of this weeks
            # matches, due to frequency, it will be overwritten by this weeks unmatched member
            # https://app.asana.com/0/1148284538006491/1149538479691025/f
            self.match_data["unmatched"] = self.member_id(self.unmatched_member)
        elif self.match_data.get("unmatched") in [
            self.member_id(m) for m in self.matched_members
        ]:
            # Unmatched from previous matches got matched. So no one will receive priority next week
            self.match_data["unmatched"] = ""
        # Here we let the unmatched data stay the same from previous matches
