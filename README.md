# ACP Brevet Control Time Calculator

A small Flask application that calculates opening and closing times for
controls on ACP-sanctioned brevets. Enter a control distance in kilometers or
miles; the calculator requests the times from Flask and updates the row without
reloading the page.

## Usage

The calculator supports nominal brevet distances of 200, 300, 400, 600, and
1000 km. Set the brevet distance and start date/time, then enter control
distances. The kilometer and mile fields convert each other automatically.
Open and close times are shown in the start date/time's local wall-clock time.
The location field is optional.

## Installation and running

From the `brevets` directory, install the dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python flask_brevets.py
```

This project is tested with Python 3.9 because Nose 1.3.7 is not compatible
with newer Python releases.

Open `http://localhost:5000` in a browser. The Flask development server binds
to all interfaces, which is useful when running in a container.

## ACP control time calculations

Calculations follow the [RUSA ACP Brevet Control Times Calculator
description](https://rusa.org/pages/acp-brevet-control-times-calculator). The
backend accepts a control distance in kilometers, truncates it to whole
kilometers, and caps it at the nominal brevet distance. Thus, for example, a
205 km route's finish on a 200 km brevet is calculated at 200 km. Calculated
times are rounded to the nearest minute and added to the specified brevet
start time.

Opening times use the maximum speeds for successive distance segments:

| Segment | Maximum speed |
| --- | ---: |
| First 200 km | 34 km/h |
| 200–400 km | 32 km/h |
| 400–600 km | 30 km/h |
| Beyond 600 km | 28 km/h |

For example, the opening time at 350 km is `200/34 + 150/32`, or 10 hours 34
minutes after the start.

Closing times use a minimum speed of 15 km/h through 600 km and 11.428 km/h
after 600 km. RUSA's relaxed close-time rule applies below 60 km: the close
time is `distance/20 + 1 hour`. At 60 km and beyond, the standard minimum-speed
calculation applies. The start control at 0 km therefore closes one hour after
the start. At the nominal brevet finish, the official overall limits take
precedence: 13h30 for 200 km, 20h for 300 km, 27h for 400 km, 40h for 600 km,
and 75h for 1000 km.

## Development

`acp_times.py` contains the standalone open/close calculations. The Flask
endpoint `/_calc_times` receives the control distance, selected brevet
distance, and start date/time and returns a JSON object with `open` and
`close` ISO date-times. `templates/calc.html` handles distance conversion,
AJAX requests, and display updates. No database or additional application
framework is used.

## Testing

From the `brevets` directory, run the Nose suite:

```bash
nosetests
```

Tests cover RUSA examples, each finish-time limit, early controls, speed-band
boundaries, over-distance finishes, kilometer truncation, and the Flask JSON
endpoint.

## Docker

From the `brevets` directory, build and run the existing image configuration:

```bash
docker build -t acp-brevet-calculator .
docker run --rm -p 5000:5000 acp-brevet-calculator
```

Then open `http://localhost:5000`.

## Author

Banyan Jullian
bjullian@uoregon.edu
https://github.com/BeanTree007/CS_322_Proj4.git
