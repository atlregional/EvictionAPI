-- create or replace view clients as
-- select id, name, address, created_on, updated_on from data.client;

-- create or replace view projects as
-- select id, name, client_id, created_on, updated_on from data.project;

-- create or replace view tasks as
-- select id, name, completed, project_id, created_on, updated_on from data.task;

-- create or replace view project_comments as
-- select id, body, project_id, created_on, updated_on from data.project_comment;

-- create or replace view task_comments as
-- select id, body, task_id, created_on, updated_on from data.task_comment;

-- create or replace view comments as
-- select 
--   id, body, 'project'::text as parent_type, project_id as parent_id, 
--   project_id, null as task_id, created_on, updated_on
-- from data.project_comment
-- union
-- select id, body, 'task'::text as parent_type, task_id as parent_id,
--   null as project_id, task_id, created_on, updated_on
-- from data.task_comment;

-- -- ...
-- alter view clients owner to api;
-- alter view projects owner to api;
-- alter view tasks owner to api;
-- alter view comments owner to api;


create or replace view atlanta_metro_area_tracts as
select id, FileDate, tractID, COUNTYFP10, TotalFilings,TotalAnsweredFilings,indexID from data.atlanta_metro_area_tract;
alter view atlanta_metro_area_tracts owner to api; 

create or replace view fulton_county_cases as
select FileDate, caseID from data.fulton_county_case;
alter view fulton_county_cases owner to api; -- it is important to set the correct owner to the RLS policy kicks in

create or replace view atlanta_metro_area_cases as
select id, street, city, zip, filingdate, answer, county, latitude, longitude,services,dismiss,defaultJudgment,judgment,answerdate,servicesdate,dismissdate,defaultJudgmentdate,judgmentdate,tractid,blockgroupid from data.atlanta_metro_area_case;
alter view atlanta_metro_area_cases owner to api;

-- CREATE or replace view atlanta_metro_area_cases_geojson AS SELECT row_to_json(fc) AS geojson FROM 
-- (SELECT 'FeatureCollection' As type, array_to_json(array_agg(f))
-- As features FROM 
-- (SELECT 
-- 'Feature' As type, 
-- ST_AsGeoJSON((ST_GeogFromText('POINT('||lg.longitude||' '||lg.latitude||')')))::json As geometry,
-- (select row_to_json(_) from (select lg.id, lg.street, lg.city, lg.zip, lg.filingdate, lg.answer, lg.county, lg.latitude, lg.longitude) as _) As properties
-- FROM data.atlanta_metro_area_case As lg) As f ) As fc;
-- alter view atlanta_metro_area_cases_geojson owner to api;