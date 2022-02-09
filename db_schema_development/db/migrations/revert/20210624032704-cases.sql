START TRANSACTION;

SET search_path = api, pg_catalog;

DROP VIEW atlanta_metro_area_cases;

CREATE VIEW atlanta_metro_area_cases AS
	SELECT atlanta_metro_area_case.id,
    atlanta_metro_area_case.street,
    atlanta_metro_area_case.city,
    atlanta_metro_area_case.zip,
    atlanta_metro_area_case.filingdate,
    atlanta_metro_area_case.answer,
    atlanta_metro_area_case.county,
    atlanta_metro_area_case.latitude,
    atlanta_metro_area_case.longitude
   FROM data.atlanta_metro_area_case;

ALTER VIEW atlanta_metro_area_cases OWNER TO api;

REVOKE ALL ON TABLE atlanta_metro_area_cases FROM webuser;
GRANT SELECT ON TABLE atlanta_metro_area_cases TO webuser;


SET search_path = data, pg_catalog;

ALTER TABLE atlanta_metro_area_case
	DROP COLUMN services,
	DROP COLUMN dismiss,
	DROP COLUMN defaultjudgment,
	DROP COLUMN judgment,
	DROP COLUMN answerdate,
	DROP COLUMN servicesdate,
	DROP COLUMN dismissdate,
	DROP COLUMN defaultjudgmentdate,
	DROP COLUMN judgmentdate;

COMMIT TRANSACTION;
