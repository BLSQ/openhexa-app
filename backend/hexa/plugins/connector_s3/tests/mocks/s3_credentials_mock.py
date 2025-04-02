def get_s3_mocked_env():
    return {
        "AWS_USERNAME": "hexa-app-test",
        "AWS_USER_ARN": "test-user-arn-arn-arn",
        "AWS_ACCESS_KEY_ID": "test-access-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret-access-key",
        "AWS_DEFAULT_REGION": "eu-central-1",
        "AWS_APP_ROLE_ARN": "test-app-arn-arn-arn",
        "AWS_PERMISSIONS_BOUNDARY_POLICY_ARN": "arn:aws:iam::333:policy/hexa-app-unittest",
    }
