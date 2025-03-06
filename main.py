import argparse
from datetime import timedelta, datetime
from maps import to_home_options, to_work_options, get_options
from datetime import datetime
from dateutil.parser import parse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--direction', type=str, required=False, default='work', help="Direction to calculate route for. Must be 'work' or 'home', defaults to 'work'")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print more detailed route information")
    parser.add_argument('--leave', type=str, required=False, help="Time to leave in 'YYYY-MM-DD HH:MM:SS' format")
    parser.add_argument('-c', '--count', type=int, required=False, default=1, help="Number of routes to display")
    args = parser.parse_args()
    return args

def parse_user_datetime(user_input: str) -> datetime:
    """
    Parses a datetime string in a 'generous' way using dateutil.
    If only a time is provided, the date defaults to today.
    """
    default_datetime = datetime.now()
    try:
        # dateutil's parse() will fill in any missing components from default_datetime
        dt = parse(user_input or default_datetime.isoformat(), default=default_datetime)
        return dt
    except ValueError as e:
        # Handle bad/unparseable input gracefully:
        raise ValueError(f"Could not parse '{user_input}': {e}")

if __name__ == '__main__':
    args = parse_args()
    leave_by = parse_user_datetime(args.leave)

    if args.direction not in ['work', 'home']:
        raise ValueError("Invalid direction. Must be 'work' or 'home'")
    route = get_options(args.direction, leave_by, verbose=args.verbose)
    must_leave_by = route.leave_by()
    count = args.count
    for i in range(count - 1):
        print("---------------")
        print("After that:")
        route = get_options(args.direction, must_leave_by + timedelta(seconds=1), verbose=args.verbose)
        must_leave_by = route.leave_by()


