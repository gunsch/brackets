# Bumping the year

1.  On server, back up current database:

    ```bash
    docker exec CONTAINER_ID /usr/bin/mysqldump -u root --password=password brackets > backups/brackets-$(date +%Y).sql
    ```

1.  Update [config.py.DOCKER](config.py.DOCKER) in this repository, setting `YEAR` and flipping `BRACKET_CHANGES_ALLOWED` to 'True' (until the tournament begins).

    CI/CD will automatically rebuild, redeploy, and restart.
