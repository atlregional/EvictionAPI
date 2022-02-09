START TRANSACTION;


SET search_path = data, pg_catalog;
CREATE TABLE atlanta_metro_area_case (
	id text NOT NULL,
	street text,
	city text,
	zip text,
	filingdate text,
	answer text,
	county text
);

REVOKE ALL ON TABLE atlanta_metro_area_case FROM api;
GRANT SELECT ON TABLE atlanta_metro_area_case TO api;

ALTER TABLE atlanta_metro_area_case
	ADD CONSTRAINT atlanta_metro_area_case_pkey PRIMARY KEY (id);



SET search_path = api, pg_catalog;

CREATE VIEW atlanta_metro_area_cases AS
	SELECT atlanta_metro_area_case.id,
    atlanta_metro_area_case.street,
    atlanta_metro_area_case.city,
    atlanta_metro_area_case.zip,
    atlanta_metro_area_case.filingdate,
    atlanta_metro_area_case.answer,
    atlanta_metro_area_case.county
   FROM data.atlanta_metro_area_case;

ALTER VIEW atlanta_metro_area_cases OWNER TO api;

REVOKE ALL ON TABLE atlanta_metro_area_cases FROM webuser; 
GRANT SELECT ON TABLE atlanta_metro_area_cases TO webuser;

COMMIT TRANSACTION;
