# GLAD and Terra I Analysis Microservice

Query the GLAD and Terra I forest loss datasets with the [Global Forest Watch (GFW)](http://globalforestwatch.org) API

- Analyze datasets by custom area of interest using the [GFW Geostore API](https://github.com/gfw-api/gfw-geostore-api)
- Analyze datasets by Country, State and Districts (defined by the [GADM Database](http://www.gadm.org/))
- Analyze datasets by Land Use features (Managed Forest Concessions, Oil Palm Concessions, Mining Concessions and Wood Fiber Concessions- available in select countries)
- Analyze datasets by Protected Areas (defined by the [WDPA database](http://www.wdpa.org/))

# GLAD API Endpoints

## Query GLAD by Geostore

*Analyzes GLAD by area of interest defined by a geostore hash*

- URL:

*/gladanalysis*

- Method:

GET

- Query Params:

Required:

*geostore=[string]*

*period=[YYYY-MM-DD,YYYY-MM-DD]*

Optional:

*gladConfirmOnly=[True]*

- Successful Response:

  - *Status: 200*

    *Content:* *{"data":{"attributes":{"areaHa":446564.6496673005,"downloadUrls":{"csv":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 1))ORDER BY year, julian_day&format=csv&geostore=939a166f7e824f62eb967f7cfb3462ee","json":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 1))ORDER BY year, julian_day&format=json&geostore=939a166f7e824f62eb967f7cfb3462ee"},"value":61317},"id":"274b4818-be18-4890-9d10-eae56d2a82e5","type":"glad-alerts"}}*

- Error Responses:

  - *Status: 400*

    *Content: {errors: [{detail: parameter not set correctly}]}*

  - *Status: 404*

    *Content: {errors: [{detail: endpoint not found}]}*

- Sample Call:

*curl "localhost:9000/v1/gladanalysis?geostore=939a166f7e824f62eb967f7cfb3462ee&period=2015-01-01,2017-01-01"*

## Query GLAD by Country, State and District

*Analyzes GLAD by country, state and district boundaries based on the GADM database*

- URL:

*/gladanalysis/admin/:country_iso/:admin_id/:dist_id*

- Method:

GET

- Query Params:

Required:

*period=[YYYY-MM-DD,YYYY-MM-DD]*

Optional:

*gladConfirmOnly=[True]*

- Successful Response:

  - *Status: 200*

    *Content:* *{"data":{"attributes":{"areaHa":4381204.954885732,"downloadUrls":{"csv":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 69)) AND (country_iso = 'PER') AND (state_id = 5)ORDER BY year, julian_day&format=csv","json":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 69)) AND (country_iso = 'PER') AND (state_id = 5)ORDER BY year, julian_day&format=json"},"value":6341},"id":"274b4818-be18-4890-9d10-eae56d2a82e5","type":"glad-alerts"}}*

- Error Responses:

    - *Status: 400

      Content: {errors: [{detail: parameter not set correctly}]}

    - Status: 404

      Content: {errors: [{detail: endpoint not found}]}*

- Sample Call:

*curl "localhost:9000/v1/gladanalysis/admin/per/5&period=2015-01-01,2017-01-01"*

## Query GLAD by Land Use data

*Analyzes GLAD by intersecting with Land Use data from GFW*

- URL:

*/gladanalysis/use/:use_type/:use_id*

- Method:

GET

- Query Params:

Required:

*period=[YYYY-MM-DD,YYYY-MM-DD]*

Optional:

*gladConfirmOnly=[True]*

- Successful Response:

  - *Status: 200*

    *Content:*
    *{"data":{"attributes":{"areaHa":60.27047655915518,"downloadUrls":{"csv":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 69))ORDER BY year, julian_day&format=csv&geostore=9f2f479b0f65588845147d63a9819746","json":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 69))ORDER BY year, julian_day&format=json&geostore=9f2f479b0f65588845147d63a9819746"},"value":0},"id":"274b4818-be18-4890-9d10-eae56d2a82e5","type":"glad-alerts"}}*

- Error Responses:

    - *Status: 400

      Content: {errors: [{detail: parameter not set correctly}]}

    - Status: 404

      Content: {errors: [{detail: endpoint not found}]}*

- Sample Call:

*curl "localhost:9000/v1/gladanalysis/use/logging/900&period=2015-01-01,2017-01-01"*

## Query GLAD by WDPA Features

*Analyzes GLAD by features within the WDPA dataset*

- URL:

*/gladanalysis/wdpa/:wdpa_id*

- Method:

GET

- Query Params:

Required:

*period=[YYYY-MM-DD,YYYY-MM-DD]*

Optional:

*gladConfirmOnly=[True]*

- Successful Response:

  - *Status: 200*

    *Content:*
    *{"data":{"attributes":{"areaHa":7639.43533583115,"downloadUrls":{"csv":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 69))ORDER BY year, julian_day&format=csv&geostore=ffecda456408bc9900708fc35771fae4","json":"/download/274b4818-be18-4890-9d10-eae56d2a82e5?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_e663eb0904de4f39b87135c6c2ed10b5 WHERE ((year = '2015' and julian_day >= 1) or (year = '2016') or (year = '2017' and julian_day <= 69))ORDER BY year, julian_day&format=json&geostore=ffecda456408bc9900708fc35771fae4"},"value":0},"id":"274b4818-be18-4890-9d10-eae56d2a82e5","type":"glad-alerts"}}*

- Error Responses:

    - *Status: 400

      Content: {errors: [{detail: parameter not set correctly}]}

    - Status: 404

      Content: {errors: [{detail: endpoint not found}]}*

- Sample Call:

*curl "localhost:9000/v1/gladanalysis/wdpa/1000&period=2015-01-01,2017-01-01"*

## Get GLAD Date Range

*Returns a min and max date for the GLAD dataset* 

- URL:

*/gladanalysis/date-range*

- Method:

GET

- Query Params:

*None*

- Successful Response:

  - *Status: 200*

    *Content:*
    *{"data":{"attributes":{"maxDate":"2017-03-10","minDate":"2015-01-01"},"id":"274b4818-be18-4890-9d10-eae56d2a82e5","type":"glad-alerts"}}*

- Error Responses:

    - *Status: 404*

      *Content: {errors: [{detail: endpoint not found}]}*

- Sample Call:

*curl "localhost:9000/v1/gladanalysis/wdpa/1000&period=2015-01-01,2017-01-01"*

## Query Parameters Look-up

| Parameter        | Definition                                                        |
| -------------    |:------------------------------------------------------------------|
| period           | Time period in format YYYY-MM-DD,YYYY-MM-DD                       |
| geostore         | A unique hash assigned to a geographic area                       |
| gladConfirmOnly  | A True or False parameter to filter glad by confirmed alerts only |

## Path Parameters Look-up

| Parameter        | Definition                                                                                       |
| -------------    |:-------------------------------------------------------------------------------------------------|
| iso_code         | The 3-letter ISO unique identifier for countries                                                 |
| admin_id         | A numeric id which refers to the first administrative-level of the GADM database                 |
| dist_id          | A numeric id which refers to the second administrative-level of the GADM database                |
| use_type         | A keyword identifier for the land use datasets (logging, oilpalm, fiber, mining)                 |
| use_type         | A numeric identifier for individual concessions within land use datasets                         |
| wdpa_id          | A numeric identifier for individual protected areas within the World Database of Portected Areas |
