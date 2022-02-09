START TRANSACTION;

SET search_path = data, pg_catalog;

CREATE TABLE fulton_county_case (
	filedate text,
	caseid text NOT NULL
);

REVOKE ALL ON TABLE fulton_county_case FROM api;
GRANT SELECT ON TABLE fulton_county_case TO api;

ALTER TABLE fulton_county_case
	ADD CONSTRAINT fulton_county_case_pkey PRIMARY KEY (caseid);
	
SET search_path = api, pg_catalog;

CREATE VIEW fulton_county_cases AS
	SELECT fulton_county_case.filedate,
    fulton_county_case.caseid
   FROM data.fulton_county_case;

ALTER VIEW fulton_county_cases OWNER TO api;

REVOKE ALL ON TABLE fulton_county_cases FROM anonymous;
GRANT SELECT ON TABLE fulton_county_cases TO anonymous;




COMMIT TRANSACTION;
