import pandas as pd
import psycopg2
from psycopg2 import sql


def upload_to_ElephantSQL(database_url, table_name, new_df):
  # Convert DataFrame to records
  records = new_df.to_dict(orient='records')

  # Use psycopg2 to insert data into the PostgreSQL database
  with psycopg2.connect(database_url) as connection:
      with connection.cursor() as cursor:
          # Check if the table exists
          cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
          table_exists = cursor.fetchone()[0]

          if table_exists:
              # Drop the table if it exists
              cursor.execute(sql.SQL("DROP TABLE {} CASCADE;").format(sql.Identifier(table_name)))

          # Extract column names and data types from the DataFrame
          column_data_types = [
          (column, new_df[column].dtype.name) for column in new_df.columns
          ]

          # Map Pandas data types to PostgreSQL data types
          pg_data_types = {
              'int64': 'INTEGER',
              'object': 'VARCHAR',  # Assuming 'object' corresponds to text-like data
             
          }

          # Create the table
          create_table_query = sql.SQL("CREATE TABLE {} ({});").format(
              sql.Identifier(table_name),
              sql.SQL(', ').join(
                  sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(pg_data_types[dtype]))
                  for column, dtype in column_data_types
              )
          )
      
          cursor.execute(create_table_query)

          # Insert data into the table
          for record in records:
            columns = ', '.join(f'"{column}"' for column in record.keys())
            values = ', '.join(['%s'] * len(record))
            # Use double quotes around both table name and column names
            query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({values});'
            cursor.execute(query, list(record.values()))
      # Commit the changes
      connection.commit()