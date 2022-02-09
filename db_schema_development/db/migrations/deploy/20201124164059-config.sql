START TRANSACTION;

SET search_path = api, pg_catalog;

CREATE OR REPLACE FUNCTION login(email text, password text) RETURNS json
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    AS $_$
declare
    usr record;
begin

	select * from data."user" as u
    where u.email = $1 and u.password = public.crypt($2, u.password)
   	INTO usr;

    if usr is NULL then
        raise exception 'invalid email/password';
    else
        
        return json_build_object(
            'me', json_build_object(
                'id', usr.id,
                'name', usr.name,
                'email', usr.email,
                'role', 'king'
            ),
            'token', pgjwt.sign(
                json_build_object(
                    'role', usr.role,
                    'user_id', usr.id,
                    'exp', extract(epoch from now())::integer + settings.get('jwt_lifetime')::int -- token expires in 1 hour
                ),
                settings.get('jwt_secret')
            )
        );
    end if;
end
$_$;

COMMIT TRANSACTION;
