import unittest
from datetime import datetime, timedelta

import oneonone

now = datetime.now()
THIS_MONDAY = now - timedelta(now.weekday())
LAST_FRIDAY = THIS_MONDAY - timedelta(days=3)
THIS_FRIDAY = LAST_FRIDAY + timedelta(weeks=1)
NEXT_MONDAY = THIS_MONDAY + timedelta(weeks=1)


def create_user(start_date=None, end_date=None):
    return {
        "gid": "1234",
        "name": "test@test.com",
        "vacation_dates": {"start_date": start_date, "end_date": end_date},
    }


def fmt(date):
    return date.strftime("%Y-%m-%d")


class TestOneOnOne(unittest.TestCase):
    def test_user_is_not_away(self):
        user = create_user()
        self.assertFalse(oneonone.user_is_away(user))

    def test_user_is_away_from_last_week(self):
        user = create_user(start_date=fmt(LAST_FRIDAY))
        self.assertTrue(oneonone.user_is_away(user))

    def test_user_is_away_this_monday(self):
        user = create_user(start_date=fmt(THIS_MONDAY), end_date=fmt(NEXT_MONDAY))
        self.assertTrue(oneonone.user_is_away(user))

    def test_user_is_away_part_of_this_week(self):
        WEDNESDAY = THIS_MONDAY + timedelta(days=2)
        user = create_user(start_date=fmt(WEDNESDAY), end_date=fmt(THIS_FRIDAY))
        self.assertFalse(oneonone.user_is_away(user))

    def test_user_is_away_this_friday(self):
        user = create_user(start_date=fmt(THIS_FRIDAY))
        self.assertFalse(oneonone.user_is_away(user))

    def test_user_is_away_next_week(self):
        user = create_user(start_date=fmt(NEXT_MONDAY))
        self.assertFalse(oneonone.user_is_away(user))


if __name__ == "__main__":
    unittest.main()
