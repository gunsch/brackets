# Bumping the year

1.  On server, back up current database:

    ```bash
    docker exec brackets_db_1 /usr/bin/mysqldump -u root --password=password brackets > backups/brackets-$(date +%Y).sql
    ```

1.  Update the brackets environment varfile on the destination host, setting `YEAR` and flipping `BRACKET_CHANGES_ALLOWED` to 'True' (until the tournament begins).

    ```bash
    vi /srv/brackets/env
    ```

1.  Restart the site:

    ```bash
    sudo systemctl restart docker-gunsch-brackets.service
    ```
