DROP USER IF EXISTS 'developer';
CREATE USER 'developer' identified by 'Z68vSVQyqJ15PUhU0MmDD9fiY8n9a0HVKyan4J35s6rMxj3i53Du1C3zw5y21awN';

GRANT INSERT, SELECT, UPDATE, DELETE ON `dev`.* TO 'developer';



/* deny root login from non-localhost */
RENAME USER 'root' TO 'root'@'127.0.0.1';
