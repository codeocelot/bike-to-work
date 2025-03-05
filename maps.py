from typing import Union

import googlemaps
from datetime import datetime, timedelta, date
import humanize
from secrets import maps_key


class Location:
    def __init__(self, name, address):
        self.name = name
        self.address = address

    def __str__(self):
        return f"{self.name} ({self.address})"

    def __repr__(self):
        return self.__str__()


class Leg:
    arrive_time: datetime
    depart_time: datetime
    duration: timedelta
    start: Location
    end: Location
    mode: str

    def __init__(self, start: Location, end: Location, arrive_time: datetime, depart_time: datetime,
                 duration: timedelta, mode: str):
        self.start = start
        self.end = end
        self.arrive_time = arrive_time
        self.depart_time = depart_time
        self.duration = duration
        self.mode = mode

    def __str__(self):
        return f"{self.start.name} to {self.end.name} {self.arrive_time.time()} ({self.duration})"


class Route:
    def __init__(self, frm: Location, to: Location, mid: Location, leave: datetime, modes = ('bicycling', 'transit')):
        self.frm = frm
        self.to = to
        self.mid = mid
        self.leave = leave
        self.modes = modes
        self.legs = self._get_legs()
        self.final_arrive = None

    def _get_legs(self):
        leg_to_mid = _get_arrival(self.modes[0], self.frm, self.mid, self.leave)
        leg_mid_to_to = _get_arrival(self.modes[1], self.mid, self.to, leg_to_mid.arrive_time)
        self.final_arrive = leg_mid_to_to.arrive_time
        legs = [leg_to_mid, leg_mid_to_to]
        return legs

    def _leave_by(self, leg: Leg) -> str:
        delta = datetime.combine(date.min, datetime.now().time()) - datetime.combine(date.min, leg.depart_time.time())
        return humanize.naturaldelta(delta)

    def leave_by(self):
        leg = self.legs[0]

        if self.modes[0] == 'bicycling':
            leg = get_biking_arrival(leg.start, leg.end, None, arrive_by=self.legs[1].depart_time)
            print(f'Must leave by {leg.depart_time.time()} to catch the train ({self._leave_by(leg)})')
        else:
            leg = get_transit_arrival(leg.start, leg.end, self.leave)
            print(f'Must leave by {leg.depart_time.time()} to catch the train ({self._leave_by(leg)})')

        return leg.depart_time

    @property
    def bike_leg(self):
        return [l for l in self.legs if l.mode == 'bicycling'][0]

    @property
    def transit_leg(self):
        return [l for l in self.legs if l.mode == 'transit'][0]

    @property
    def arrive_by(self):
        return max(self.bike_leg.arrive_time, self.transit_leg.arrive_time)

    def __str__(self):
        return f"{self.legs}"

    def __repr__(self):
        return self.__str__()


HOME = Location('Home', "926 Mandana Blvd, Oakland, CA, 94610")
BART_19TH = Location('19th', "19th St. Oakland BART Station, 1900 Broadway, Oakland, CA 94612")
BART_LAKE_MERRITT = Location('Lake Merritt', "Lake Merritt BART Station, 800 Madison St, Oakland, CA 94607")
OFFICE = Location('Office', '181 Fremont St, San Francisco, CA 94105')
BART_EMBARCADERO = Location('Embarcadero', 'Embarcadero BART Station, 1 Market St, San Francisco, CA 94105')

BART_OAKLAND_STATIONS = [BART_19TH, BART_LAKE_MERRITT]
BART_SF_STATIONS = [BART_EMBARCADERO],

gmaps = googlemaps.Client(key=maps_key)


def get_biking_arrival(frm: Location, to: Location, leave: Union[datetime, None] = datetime.now(),
                       arrive_by=None) -> Leg:
    if arrive_by and leave:
        raise ValueError("Cannot specify both arrive_by and leave")
    ex_args = {}
    if arrive_by:
        ex_args['arrival_time'] = arrive_by
    if leave:
        ex_args['departure_time'] = leave
        ex_args['traffic_model'] = 'best_guess'
    resp = gmaps.directions(frm.address, to.address, mode="bicycling", **ex_args)
    duration = resp[0]['legs'][0]['duration']['value']
    duration = timedelta(seconds=duration)
    if leave:
        departure_time = leave
    else:
        departure_time = arrive_by - duration
    if arrive_by:
        arrival = arrive_by
    else:
        arrival = leave + duration
    leg = Leg(frm, to, arrival, departure_time, duration, 'bicycling')
    return leg


def get_transit_arrival(frm: Location, to: Location, leave=datetime.now()) -> Leg:
    resp = gmaps.directions(frm.address, to.address, mode="transit", departure_time=leave, traffic_model="best_guess")
    all_legs = resp[0]['legs']
    if len(all_legs) > 1:
        print(f"Multiple legs found, using first")
    duration = resp[0]['legs'][0]['duration']['value']
    departure_time = datetime.fromtimestamp(resp[0]['legs'][0]['departure_time']['value'])
    arrive_time = datetime.fromtimestamp(resp[0]['legs'][0]['arrival_time']['value'])
    duration = timedelta(seconds=duration)

    leg = Leg(frm, to, arrive_time, departure_time, duration, 'transit')
    return leg


def _get_arrival(mode, frm: Location, to: Location, leave=datetime.now()):
    if mode == 'bicycling':
        return get_biking_arrival(frm, to, leave)
    if mode == 'transit':
        return get_transit_arrival(frm, to, leave)


def _print_to_work_option(route: Route):
    print(
        f"Take {route.bike_leg.end.name}, train leaves at {route.transit_leg.depart_time.time()}, arrive @ Embarcadero by {route.arrive_by.time()}")

def _print_route(route: Route):
    if route.modes[0] == 'bicycling':
        print(
            f"Take {route.bike_leg.end.name}, train leaves at {route.transit_leg.depart_time.time()}, arrive @ Embarcadero by {route.arrive_by.time()}")
    else:
        print(
            f"Take {route.transit_leg.end.name}, train leaves at {route.transit_leg.depart_time.time()}, arrive @ home by {route.arrive_by.time()}")


def to_work_options(leave=datetime.now()) -> Route:
    route_19 = Route(HOME, BART_EMBARCADERO, BART_19TH, leave)
    route_lake = Route(HOME, BART_EMBARCADERO, BART_LAKE_MERRITT, leave)
    min_route = min(route_19, route_lake, key=lambda r: r.arrive_by)
    _print_route(min_route)
    return min_route


def to_home_options(leave=datetime.now()) -> Route:
    route_19 = Route(OFFICE, BART_EMBARCADERO, BART_19TH, leave, ['transit', 'bicycling'])
    route_lake = Route(OFFICE, BART_EMBARCADERO, BART_LAKE_MERRITT, leave, ['transit', 'bicycling'])
    min_route = min(route_19, route_lake, key=lambda r: r.arrive_by)
    _print_route(min_route)
    return min_route
