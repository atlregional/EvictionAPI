START TRANSACTION;

SET search_path = data, pg_catalog;


ALTER TABLE atlanta_metro_area_case
	ADD COLUMN services text,
	ADD COLUMN dismiss text,
	ADD COLUMN defaultjudgment text,
	ADD COLUMN judgment text,
	ADD COLUMN answerdate date,
	ADD COLUMN servicesdate date,
	ADD COLUMN dismissdate date,
	ADD COLUMN defaultjudgmentdate date,
	ADD COLUMN judgmentdate date;

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
    atlanta_metro_area_case.longitude,
    atlanta_metro_area_case.services,
    atlanta_metro_area_case.dismiss,
    atlanta_metro_area_case.defaultjudgment,
    atlanta_metro_area_case.judgment,
    atlanta_metro_area_case.answerdate,
    atlanta_metro_area_case.servicesdate,
    atlanta_metro_area_case.dismissdate,
    atlanta_metro_area_case.defaultjudgmentdate,
    atlanta_metro_area_case.judgmentdate
   FROM data.atlanta_metro_area_case;

ALTER VIEW atlanta_metro_area_cases OWNER TO api;

REVOKE ALL ON TABLE atlanta_metro_area_cases FROM webuser;
GRANT SELECT ON TABLE atlanta_metro_area_cases TO webuser;

COMMIT TRANSACTION;
