# GENX
Assignment for the TU Delft Master Course: AE4238 Aero Engine Technology

## Primary Assumtions
1. The specific heat are assumed constant w.r.t. temperture
2. Fuel does not alter the Individual gas constant of the exhaust air (hot nozzle)
3. The intermediate values in a process can be approximated by an exponential function
4. The flow through both nozzles is always choked

## Usage
1. Create config file for desired engine in accordance with the examples in `engine/data`
2. import the `Engine` class from ``engine.py`` and instantiate object w/ syntax: `Engine(filename='myengine.cfg')`
3. Enjoy

## TODO
Make table of governing relations between stages w/ assumptions
