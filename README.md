# London Housing API
A Flask API to return Information on House Prices and Sales

Source data can be found here: https://www.kaggle.com/justinas/housing-in-london and is also part of this repository, the `data` folder.

Currently the API has 3 endpoints:

* `/price`: returns the latest price for an area given by the client (e.g. 'city of london')
* `/ela`: returns the price elasticity from a log-log model based solely on average house prices and houses sold in a requested area
* `/plot`: returns a time series plot with the data normalized to a common scale using a z-transformation. One plot represents the evolution of prices and sales over the entire period for a given area. 

All endpoints are available via `GET` or `POST` requests. Data should be sent via the request body in a `json` format, e.g.: `{"area":"city of london"}`.

To run the API locally, navigate into the root of the repository and run `python housing_api.py`.

## Issues
The app crashed after sending requests to the `plot` endpoint. This will be fixed at some point.
