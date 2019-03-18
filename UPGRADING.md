# Bumping the year

1.  On server, back up current database:

    ```bash
    mysqldump -u root -p brackets > backups/brackets-$(date +%Y).sql
    ```

2.  Update config, setting `YEAR` and flipping `BRACKET_CHANGES_ALLOWED`:

    ```bash
    vi /srv/qxlp.net/brackets/config.py
    ```

3.  Restart server:

    ```bash
    sudo service apache2 restart
    ```

# Adding changes from locally (new machine)

1.  Make sure remote is available:

    ```bash
    git remote add deploy ssh://gunsch@HOST/srv/git/brackets.git
    ```

1.  Deploy to remote

    ```bash
    git push deploy master
    ```

