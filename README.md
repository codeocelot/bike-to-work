# Bike 2 Work

## Simple Multimodal Trip Planning to- and from-work

This is a simple script that uses the Google Maps API to plan a multimodal trip to and from work. It uses the Google Maps API to get the directions.

### To Work
Computes the time it takes to bike to both Lake Merritt and 19th St BART stations. For both of those stations, it then computes the next arriving train to Embarcadero station. It then works backward to determine the last possible time to leave home in order to make that train.  Finally, the script computes the next train after that one, in case I don't feel like immediately leaving the house.

```
Take 19th, train leaves at 11:12:46, arrive @ Embarcadero by 11:29:40
Must leave by 10:57:49 to catch the train (5 minutes)
After that:
---------------
Take Lake Merritt, train leaves at 11:16:28, arrive @ Embarcadero by 11:33:01
Must leave by 11:00:55 to catch the train (8 minutes)
```

## Setup

### Install deps

```bash
pip install -r requirements.txt
```

Write secrets

```bash
echo "MAPS_API_KEY=$MAPS_API_KEY" > .env
```

### Run

```bash
python main.py --direction work
```
