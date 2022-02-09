START TRANSACTION;

SET search_path = api, pg_catalog;

-- CREATE EXTENSION postgis WITH SCHEMA api;

-- CREATE VIEW atlanta_metro_area_cases_geojson AS
-- 	SELECT row_to_json(fc.*) AS geojson
--    FROM ( SELECT 'FeatureCollection'::text AS type,
--             array_to_json(array_agg(f.*)) AS features
--            FROM ( SELECT 'Feature'::text AS type,
-- 		   ST_AsGeoJSON((ST_GeogFromText('POINT('||lg.longitude||' '||lg.latitude||')')))::json AS geometry,
--                     ( SELECT row_to_json(_.*) AS row_to_json
--                            FROM ( SELECT lg.id,
--                                     lg.street,
--                                     lg.city,
--                                     lg.zip,
--                                     lg.filingdate,
--                                     lg.answer,
--                                     lg.county,
--                                     lg.latitude,
--                                     lg.longitude) _) AS properties
--                    FROM data.atlanta_metro_area_case lg) f) fc;

-- ALTER VIEW atlanta_metro_area_cases_geojson OWNER TO api;

-- REVOKE ALL ON TABLE atlanta_metro_area_cases_geojson FROM webuser;
-- GRANT SELECT ON TABLE atlanta_metro_area_cases_geojson TO webuser;


COMMIT TRANSACTION;
