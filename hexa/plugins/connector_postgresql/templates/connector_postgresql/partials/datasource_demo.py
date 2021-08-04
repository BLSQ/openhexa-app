import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ["{{ datasource.env_name }}_URL"])

# create sample dataframe
df = pd.DataFrame({"name": ["Jane", "John", "Tyler"], "age": [19, 17, 22]})

# Write data
df.to_sql("database_tutorial", con=engine, if_exists="replace")
