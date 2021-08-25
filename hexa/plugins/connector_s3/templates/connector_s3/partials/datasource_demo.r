library(aws.s3)

# Read CSV file
df <- s3read_using(
    FUN = read.csv,
    object = 's3://{{ datasource.name}}/path-in-bucket/example.csv'
)

# Write CSV file
df.out <- head(df)
s3write_using(
    x = df,
    FUN = write.csv,
    object = 's3://{{ datasource.name}}/path-in-bucket/some-output.csv'
)
