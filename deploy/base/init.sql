CREATE TABLE releases (id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                       version text NOT NULL, description text NOT NULL);
INSERT INTO releases(version, description) VALUES ('0.1.0', 'Initial secure delivery lab');
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
