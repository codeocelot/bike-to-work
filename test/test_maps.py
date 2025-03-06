from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.bike2work.maps import Location, Leg, Route


@patch('src.bike2work.maps._get_arrival')
class TestMaps(TestCase):
    def test_to_work(self, mock_get_arrival):
        start_location = Location('start', '123 Main St')
        mid_location = Location('mid', '456 Elm St')
        end_location = Location('end', '789 Oak St')
        depart_time = datetime(2025, 1, 1, 9, 0, 0)
        mid_time = datetime(2025, 1, 1, 10, 0 ,0)
        arrive_time = datetime(2025, 1, 1, 11, 0, 0)
        legs = [
            Leg(start_location, mid_location, mid_time, depart_time, timedelta(hours=1), 'bicycling' ),
            Leg(mid_location, end_location, arrive_time, mid_time, timedelta(hours=1), 'transit' )
            ]
        mock_get_arrival.side_effect = legs
        leave_time = datetime(2025, 1, 1, 8, 0, 0)
        route = Route(leave_time, locations=[start_location, mid_location, end_location],modes=['bicycling', 'transit'] )
        print(route)
        assert route.final_arrive == arrive_time
        assert len(route.route_legs) == 2
        assert route.route_legs[0].start == start_location
        assert route.route_legs[0].end == mid_location
        assert route.route_legs[1].start == mid_location
        assert route.route_legs[1].end == end_location
        assert route.route_legs[0].depart_time == depart_time

        leave_by_time = datetime(2025, 1, 1, 9, 30, 0)
        mock_get_arrival.side_effect = [Leg(start_location, mid_location, mid_time, leave_by_time, timedelta(hours=1), 'bicycling')]
        leave_by = route.leave_by()
        assert leave_by == leave_by_time
