START TRANSACTION;

SET search_path = api, pg_catalog;

DROP VIEW fulton_county_cases;

SET search_path = data, pg_catalog;

DROP TABLE fulton_county_case;

COMMIT TRANSACTION;
