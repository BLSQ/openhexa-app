# Reading and writing to S3 using Pandas
import pandas as pd

df = pd.read_csv("s3://{{datasource.name}}/path-in-bucket/example.csv")
df.to_csv("s3://{{datasource.name}}/other-path-in-bucket/result.csv")


# Using S3FS to work directly with S3 resources
import s3fs, json

fs = s3fs.S3FileSystem()
with fs.open("s3://{{datasource.name}}/path-in-bucket/example.json", "rb") as f:
    print(len(json.load(f)))
