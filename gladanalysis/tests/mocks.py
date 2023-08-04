import re

def mock_geostore_not_found(mocker):
    matcher = re.compile('.*/geostore.*')
    return mocker.get(
        matcher,
        request_headers={'content-type': 'application/json', 'x-api-key': 'api-key-test'},
        status_code=404
    )

def mock_geostore(mocker):
    matcher = re.compile('.*/geostore.*')
    return mocker.get(
        matcher,
        request_headers={'content-type': 'application/json', 'x-api-key': 'api-key-test'},
        status_code=200,
        json={"data": {"attributes": {"areaHa": 231065643.70829132, "downloadUrls": {
            "csv": "/download/1dca5597-d6ac-4064-82cf-9f02b178f424?sql=SELECT lat, long, country_iso, state_id, dist_id, year, day FROM index_1dca5597d6ac406482cf9f02b178f424 WHERE ((year = 2004 and day >= 161) or (year >= 2005 and year <= 2016) or (year = 2017 and day <= 81))ORDER BY year, day&format=csv&geostore=141cba8b4aadde4a5b981917214666e0",
            "json": "/download/1dca5597-d6ac-4064-82cf-9f02b178f424?sql=SELECT lat, long, country_iso, state_id, dist_id, year, day FROM index_1dca5597d6ac406482cf9f02b178f424 WHERE ((year = 2004 and day >= 161) or (year >= 2005 and year <= 2016) or (year = 2017 and day <= 81))ORDER BY year, day&format=json&geostore=141cba8b4aadde4a5b981917214666e0"},
                                      "value": 1000}, "geostore": "141cba8b4aadde4a5b981917214666e0",
                       "id": "1dca5597-d6ac-4064-82cf-9f02b178f424", "type": "terrai-alerts"}}
    )


def mock_query(mocker):
    matcher = re.compile('.*/query.*')
    return mocker.get(
        matcher,
        request_headers={'content-type': 'application/json', 'x-api-key': 'api-key-test'},
        status_code=200,
        json={
            "data": [{"MAX(year)": 123, "MAX(day)": 123, "MIN(year)": 123, "MIN(day)": 123, "COUNT(day)": 123}]}
    )
