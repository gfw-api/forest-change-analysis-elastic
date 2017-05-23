# GLAD and Terra I Analysis Microservice

Query the GLAD and Terra I forest loss datasets with the [Global Forest Watch (GFW)](http://globalforestwatch.org) API

- Analyze datasets by custom area of interest using the [GFW Geostore API](https://github.com/gfw-api/gfw-geostore-api)
- Analyze datasets by Country, State and Districts (defined by the [GADM Database](http://www.gadm.org/))
- Analyze datasets by Land Use features (Managed Forest Concessions, Oil Palm Concessions, Mining Concessions and Wood Fiber Concessions- available in select countries)
- Analyze datasets by Protected Areas (defined by the [WDPA database](http://www.wdpa.org/))

# API Endpoints

## Query GLAD by Geostore

- URL:

/gladanalysis

- Method:

GET

- URL Params:

Required:

geostore=[string]

period=[YYYY-MM-DD,YYYY-MM-DD]

- Successful Response:

  - Status: 200

    Content: {"data":{"attributes":{"areaHa":446564.6496673005,"downloadUrls":{"csv":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 1))ORDER BY year, julian_day&format=csv&geostore=939a166f7e824f62eb967f7cfb3462ee","json":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 1))ORDER BY year, julian_day&format=json&geostore=939a166f7e824f62eb967f7cfb3462ee"},"value":61317},"id":"274b4818-be18-4890-9d10-eae56d2a82e5","type":"glad-alerts"}}

- Error Responses:

  - Status: 400

    Content: {errors: [{detail: parameter not set correctly}]}
    
  - Status: 404

    Content: {errors: [{detail: endpoint not found}]}

- Sample Call:

curl "localhost:9000/v1/gladanalysis?geostore=939a166f7e824f62eb967f7cfb3462ee&period=2015-01-01,2017-01-01"
