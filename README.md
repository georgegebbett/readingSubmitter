# Is there anything I won't waste time on?!

Our electricity is supplied by Sainsbury's Energy, and they do not interface well with our smart meters.

This means we frequently end up with absolutely mental estimated bills, which is not that fun. I am also very bad at remembering to submit energy readings, and so I sniffed around their site until I figured out how the API worked, and then wrote this script which will submit the readings for me.

You too can use this if you so desire, simply by running `submit_readings.py` with the relevant command line args:

```
--email      Your Sainsbury's Energy account email
--password   Your Sainsbury's Energy account password
--gas        An integer value to submit as the gas meter reading
--elec       An integer value to submit as the electricity meter reading
```