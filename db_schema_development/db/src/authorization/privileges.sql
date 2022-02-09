\echo # Loading roles privilege

-- this file contains the privileges of all aplications roles to each database entity
-- if it gets too long, you can split it one file per entity ore move the permissions
-- to the file where you defined the entity

-- specify which application roles can access this api (you'll probably list them all)
grant usage on schema api to anonymous, webuser;

-- set privileges to all the auth flow functions
grant execute on function api.login(text,text) to anonymous;
grant execute on function api.signup(text,text,text) to webuser;
grant execute on function api.me() to webuser;
grant execute on function api.login(text,text) to webuser;
grant execute on function api.refresh_token() to webuser;

-- define the who can access todo model data
-- enable RLS on the table holding the data
-- alter table data.todo enable row level security;
-- -- define the RLS policy controlling what rows are visible to a particular application user
-- create policy todo_access_policy on data.todo to api 
-- using (
-- 	-- the authenticated users can see all his todo items
-- 	-- notice how the rule changes based on the current user_id
-- 	-- which is specific to each individual request
-- 	(request.user_role() = 'webuser' and request.user_id() = owner_id)

-- 	or
-- 	-- everyone can see public todo
-- 	(private = false)
-- )
-- with check (
-- 	-- authenticated users can only update/delete their todos
-- 	(request.user_role() = 'webuser' and request.user_id() = owner_id)
-- );


-- -- give access to the view owner to this table
-- grant select, insert, update, delete on data.todo to api;
-- grant select, insert, update, delete on data.client to api;
-- grant usage on data.todo_id_seq to webuser;

grant select on data.atlanta_metro_area_tract to api;
grant select on data.fulton_county_case to api;
grant select on data.atlanta_metro_area_case to api;

-- While grants to the view owner and the RLS policy on the underlying table 
-- takes care of what rows the view can see, we still need to define what 
-- are the rights of our application user in regard to this api view.

-- -- authenticated users can request/change all the columns for this view
-- grant select, insert, update, delete on api.todos to webuser;
-- -- ...
-- grant select, insert, update, delete 
-- on api.clients, api.projects, api.tasks, api.project_comments, api.task_comments, api.comments
-- to webuser;

-- grant select, insert, update, delete 
-- on api.clients
-- to customer;

-- -- anonymous users can only request specific columns from this view
-- grant select (id, todo) on api.todos to anonymous;
grant select on api.atlanta_metro_area_tracts to anonymous;
grant select on api.fulton_county_cases to anonymous;
grant select on api.atlanta_metro_area_cases to webuser;
-- grant select on api.atlanta_metro_area_cases_geojson to webuser;

\set jwt_secret `echo $JWT_SECRET`
\set quoted_jwt_secret '\'' :jwt_secret '\''
select settings.set('jwt_secret', :quoted_jwt_secret);
select settings.set('jwt_lifetime', '360000000');
-------------------------------------------------------------------------------
