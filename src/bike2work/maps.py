from functools import cached_property
from typing import Union, List

import googlemaps
from datetime import datetime, timedelta, date
import humanize

from .secrets import maps_key


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
    def __init__(self, leave: datetime, modes = ('bicycling', 'transit'), locations: List[Location]=None):
        self.locations = locations
        self.leave = leave
        self.modes = modes
        self.final_arrive = None

    @cached_property
    def route_legs(self):
        return self._get_legs()

    def _get_legs(self) -> List[Leg]:
        legs = []
        for i in range(len(self.locations) - 1):
            if i == 0:
                leave = self.leave
            else:
                leave = legs[-1].arrive_time
            leg = _get_arrival(self.modes[i], self.locations[i], self.locations[i + 1], leave)
            legs.append(leg)
        self.final_arrive = legs[-1].arrive_time
        return legs

    def _leave_by(self, leg: Leg) -> str:
        delta = datetime.combine(date.min, datetime.now().time()) - datetime.combine(date.min, leg.depart_time.time())
        return humanize.naturaldelta(delta)

    def leave_by(self):
        leg = self.route_legs[0]

        if self.modes[0] == 'bicycling':
            leg = _get_arrival('bicycling', leg.start, leg.end, None, arrive_by=self.route_legs[1].depart_time)
        else:
            leg = _get_arrival('transit', leg.start, leg.end, self.leave)

        print(f'Must leave by {leg.depart_time.time()} to catch the train ({self._leave_by(leg)})')

        return leg.depart_time

    @property
    def bike_leg(self):
        return [l for l in self.route_legs if l.mode == 'bicycling'][0]

    @property
    def transit_leg(self):
        return [l for l in self.route_legs if l.mode == 'transit'][0]

    @property
    def arrive_by(self):
        return max([l.arrive_time for l in self.route_legs])

    def __str__(self):
        return f"{self.route_legs}"

    def __repr__(self):
        return self.__str__()


HOME = Location('Home', "926 Mandana Blvd, Oakland, CA, 94610")
BART_19TH = Location('19th', "19th St. Oakland BART Station, 1900 Broadway, Oakland, CA 94612")
BART_LAKE_MERRITT = Location('Lake Merritt', "Lake Merritt BART Station, 800 Madison St, Oakland, CA 94607")
OFFICE = Location('Office', '181 Fremont St, San Francisco, CA 94105')
BART_EMBARCADERO = Location('Embarcadero', 'Embarcadero BART Station, 1 Market St, San Francisco, CA 94105')

BART_OAKLAND_STATIONS = [BART_19TH, BART_LAKE_MERRITT]
BART_SF_STATIONS = [BART_EMBARCADERO],



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

    gmaps = googlemaps.Client(key=maps_key)
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
    gmaps = googlemaps.Client(key=maps_key)
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


def _get_arrival(mode, *args, **kwargs) -> Leg:
    if mode == 'bicycling':
        return get_biking_arrival(*args, **kwargs)
    if mode == 'transit':
        return get_transit_arrival(*args, **kwargs)


def _print_to_work_option(route: Route):
    print(
        f"Take {route.bike_leg.end.name}, train leaves at {route.transit_leg.depart_time.time()}, arrive @ {route.locations[-1].name} by {route.arrive_by.time()}")

def _print_route(route: Route, verbose: bool):
    print(
        f"Take {route.bike_leg.end.name}, train leaves at {route.transit_leg.depart_time.time()}, arrive @ {route.locations[-1].name} by {route.arrive_by.time()}")
    if verbose:
        for i in range(len(route.route_legs)):
            print('\t', route.locations[i].name, "->", route.locations[i+1].name, route.route_legs[i].depart_time.time(), "->", route.route_legs[i].arrive_time.time())


def to_work_options(leave=None, verbose=False) -> Route:
    if leave is None:
        leave = datetime.now()
    route_19 = Route(leave, locations=[HOME, BART_19TH, BART_EMBARCADERO, OFFICE], modes=['bicycling', 'transit', 'bicycling'])
    route_lake = Route(leave, locations=[HOME, BART_LAKE_MERRITT, BART_EMBARCADERO, OFFICE], modes=['bicycling', 'transit', 'bicycling'])
    min_route = min(route_19, route_lake, key=lambda r: r.arrive_by)
    _print_route(min_route, verbose)
    return min_route


def to_home_options(leave=None, verbose=False) -> Route:
    if leave is None:
        leave = datetime.now()
    route_19 = Route(leave,  locations=[OFFICE, BART_EMBARCADERO, BART_19TH, HOME], modes=['bicycling', 'transit', 'bicycling'])
    route_lake = Route(leave, locations=[OFFICE, BART_EMBARCADERO, BART_LAKE_MERRITT, HOME], modes=['bicycling', 'transit', 'bicycling'])
    min_route = min(route_19, route_lake, key=lambda r: r.arrive_by)
    _print_route(min_route, verbose)
    return min_route

def get_options(dest: str, leave=None, verbose=False):
    return to_work_options(leave, verbose) if dest == 'work' else to_home_options(leave, verbose)

if __name__ == '__main__':
    r = to_work_options()
    r.leave_by()
    print(r.final_arrive)