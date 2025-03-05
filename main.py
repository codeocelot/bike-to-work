import argparse
from datetime import timedelta
from maps import to_home_options, to_work_options


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--direction', type=str, required=False, default='work')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    if args.direction == 'work':
        route = to_work_options()
        leave_by = route.leave_by()
        print("After that:")
        print("---------------")
        route2 = to_work_options(leave_by + timedelta(minutes=1))
        leave_by2 = route2.leave_by()
    else:
        route = to_home_options()
        leave_by = route.leave_by()
