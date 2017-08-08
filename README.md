# GLAD and Terra I Analysis API Microservice Overview

Query the GLAD and Terra I forest loss datasets with the [Global Forest Watch (GFW)](http://globalforestwatch.org) API

- Analyze datasets by a custom area of interest using the [GFW Geostore API](https://github.com/gfw-api/gfw-geostore-api) or by sending GeoJson in Post
- Analyze datasets by Country, State and Districts (defined by the [GADM Database](http://www.gadm.org/))
- Analyze datasets by GFW Land Use features (Managed Forest Concessions, Oil Palm Concessions, Mining Concessions and Wood Fiber Concessions- available in select countries)
- Analyze datasets by Protected Areas (defined by the [WDPA database](http://www.wdpa.org/))
- Get dataset download urls (csv and json) for areas of interest
- Summarize analysis results by day, week, month, quarter or year
- Get dataset date range/ latest date

## API Endpoints
For endpoint documentation, please visit our [API documentation page for GLAD](https://production-api.globalforestwatch.org/documentation/#/?tags=GLAD) and our
[API documentation page for TerraI](https://production-api.globalforestwatch.org/documentation/#/?tags=TERRAI)

# Getting Started
Perform the following steps:
* [Install docker](https://docs.docker.com/engine/installation/)
* [Install control tower](https://github.com/control-tower/control-tower)
* Clone this repository: ```git clone https://github.com/gfw-api/forest-change-analysis-elastic.git```
* Enter in the directory (cd forest-change-analysis-elastic)
* Change the CT_URL and Port in the docker-compose-develop.yml and docker-compose.yml and Dockerfile to your machine and port #
* Open a terminal (if you have mac or windows, open a terminal with the 'Docker Quickstart Terminal') and run the gladanalysis.sh shell script in development mode:

```ssh
./gladanalysis.sh develop
```

If this is the first time you run it, it may take a few minutes.

## Testing
Testing API endpoints

```ssh
./gladanalysis.sh test
```

## Config

## register.json
This is the configuration file for the rest endpoints in the microservice. This json connects to the API Gateway. It contains variables such as:
* #(service.id) => Id of the service set in the config file by environment
* #(service.name) => Name of the service set in the config file by environment
* #(service.uri) => Base uri of the service set in the config file by environment

Example:
````
{
    "id": "#(service.id)",
    "name": "#(service.name)",
    "tags": ["gfw"],
    "urls": [{
        "url": "/v1/glad-alerts/admin/:iso_code",
        "method": "GET",
        "endpoints": [{
            "method": "GET",
            "path": "/api/v2/ms/glad-alerts/admin/:iso_code"
        }]
    }, {
        "url": "/v1/glad-alerts/admin/:iso_code/:admin_id",
        "method": "GET",
        "endpoints": [{
            "method": "GET",
            "path": "/api/v2/ms/glad-alerts/admin/:iso_code/:admin_id"
        }]
    }, {
        "url": "/v1/glad-alerts/admin/:iso_code/:admin_id/:dist_id",
        "method": "GET",
        "endpoints": [{
            "method": "GET",
            "path": "/api/v2/ms/glad-alerts/admin/:iso_code/:admin_id/:dist_id"
        }]
    }]
}

'''
