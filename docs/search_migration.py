from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0001_initial"),
    ]

    migration = """
        CREATE TRIGGER text_search_update BEFORE INSERT OR UPDATE
        ON search_searchdocument FOR EACH ROW EXECUTE PROCEDURE
        tsvector_update_trigger(text_search, 'pg_catalog.english', text);

        -- Force triggers to run and populate the text_search column.
        UPDATE search_searchdocument set ID = ID;
    """

    reverse_migration = """
        DROP TRIGGER text_search ON search_searchdocument;
    """

    operations = [migrations.RunSQL(migration, reverse_migration)]
