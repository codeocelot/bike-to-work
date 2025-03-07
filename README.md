# Bike 2 Work

## Simple Multimodal Trip Planning to- and from-work

This is a simple script that uses the Google Maps API to plan a multimodal trip to and from work.

### To Work
Computes the time it takes to bike to both Lake Merritt and 19th St BART stations. For both of those stations, it then computes the next arriving train to Embarcadero station. It then works backward to determine the last possible time to leave home in order to make that train.  Finally, the script computes the next train after that one, in case I don't feel like immediately leaving the house. It then reports the full time it takes to bike to the station, ride the train to Embarcadero, then bike from Embarcadero station to the office.

```
Take 19th, train leaves at 11:12:46, arrive @ Embarcadero by 11:29:40
Must leave by 10:57:49 to catch the train (5 minutes)
---------------
After that:
Take Lake Merritt, train leaves at 11:16:28, arrive @ Embarcadero by 11:33:01
Must leave by 11:00:55 to catch the train (8 minutes)
```


### To Home

Computes the time it takes to bike from the office to Embarcadero station. It then computes the next arriving train to Lake Merritt and 19th St stations. It then works backward to determine the last possible time to leave the office in order to make that train. Finally, the script computes the next train after that one, in case I don't feel like immediately leaving the office. It then reports the full time it takes to bike from the office to Embarcadero station, ride the train to the station, then bike from the station to home.

Admittedly, this is a bit less useful than the to-work calculation, since I always leave Embarcadero and trains always leave pretty frequently during commute hours.

## Setup

### Install

```bash
pip install git+https://github.com/codeocelot/bike-to-work
```

Write secrets

```bash
echo "MAPS_API_KEY=$MAPS_API_KEY" > ~/.bike2work.env
# or 
export MAPS_API_KEY=...
```

### Run

```bash
bike2work --direction work
```

### Options

```bash
usage: bike2work [-h] [--direction DIRECTION] [-v] [--leave LEAVE] [-c COUNT]

options:
  -h, --help            show this help message and exit
  --direction DIRECTION
                        Direction to calculate route for. Must be 'work' or 'home', defaults to 'work'
  -v, --verbose         Print more detailed route information
  --leave LEAVE         Time to leave in 'YYYY-MM-DD HH:MM:SS' format
  -c COUNT, --count COUNT
                        Number of routes to display
```

### Example

```bash
bike2work --direction work --count 3 --verbose

Take 19th, train leaves at 10:52:46, arrive @ Office by 11:13:41
	 Home -> 19th 10:36:39.650759 -> 10:51:36.650759
	 19th -> Embarcadero 10:52:46 -> 11:09:40
	 Embarcadero -> Office 11:09:40 -> 11:13:41
Must leave by 10:37:49 to catch the train (a minute)
---------------
After that:
Take Lake Merritt, train leaves at 10:56:42, arrive @ Office by 11:17:18
	 Home -> Lake Merritt 10:37:50 -> 10:53:23
	 Lake Merritt -> Embarcadero 10:56:42 -> 11:13:17
	 Embarcadero -> Office 11:13:17 -> 11:17:18
Must leave by 10:41:09 to catch the train (4 minutes)
---------------
After that:
Take 19th, train leaves at 10:57:34, arrive @ Office by 11:18:29
	 Home -> 19th 10:41:10 -> 10:56:07
	 19th -> Embarcadero 10:57:34 -> 11:14:28
	 Embarcadero -> Office 11:14:28 -> 11:18:29
Must leave by 10:42:37 to catch the train (5 minutes)
```

### Tests

```bash
pytest
```

### Extensions

The project should support other modes and routes, albeit with the caveat that only a single transit leg can be used, meaning it doesn't support 'hacking' the BART system by, say, taking a Blue line to Lake Merritt and then transferring to a Red/Yellow to 19th. 
