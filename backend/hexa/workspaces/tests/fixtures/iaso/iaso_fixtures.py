iaso_mocked_auth_token = {
    "access": "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxNzY5MDEwNCwiaWF0IjoxNzE3NjkwMTA0fQ.WsmnKvyKFR2eWNL4wD4yrnd6F9CDBV2dCaMx9lE6V84",  # noqa: E501
    "refresh": "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxNzY5MDEwNCwiaWF0IjoxNzE3NjkwMTA0fQ.WsmnKvyKFR2eWNL4wD4yrnd6F9CDBV2dCaMx9lE6V84",  # noqa: E501
}
iaso_mocked_refreshed_auth_token = {
    "access": "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxNzY5MDEwNCwiaWF0IjoxNzE3NzYwMTA0fQ._pXcqDw0QgvznvNuhVPwYyIms3H5imH-q6A7lIQJjYQ",  # noqa: E501
    "refresh": "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxNzY5MDEwNCwiaWF0IjoxNzE3NjkwMTA0fQ.WsmnKvyKFR2eWNL4wD4yrnd6F9CDBV2dCaMx9lE6V84",  # noqa: E501
}


iaso_mocked_forms = {
    "forms": [
        {
            "id": 278,
            "name": "Test (form styling)",
            "form_id": "pathways_indonesia_survey_1",
            "device_field": "deviceid",
            "location_field": "",
            "org_unit_types": [
                {
                    "id": 781,
                    "name": "Province",
                    "short_name": "Prov",
                    "created_at": 1712825023.047433,
                }
            ],
            "projects": [{"id": 149, "name": "Pathways"}],
            "created_at": 1713171086.141424,
        }
    ]
}

iaso_mocked_projects = {
    "projects": [
        {
            "id": 149,
            "name": "Pathways",
            "app_id": "pathways",
            "feature_flags": [
                {
                    "id": 3,
                    "name": "GPS point for each form",
                    "code": "TAKE_GPS_ON_FORM",
                },
                {
                    "id": 7,
                    "name": "Mobile: Show data collection screen",
                    "code": "DATA_COLLECTION",
                },
                {
                    "id": 12,
                    "name": "Mobile: Finalized forms are read only",
                    "code": "MOBILE_FINALIZED_FORM_ARE_READ",
                },
                {"id": 4, "name": "Authentication", "code": "REQUIRE_AUTHENTICATION"},
            ],
            "created_at": 1710153966.532745,
            "updated_at": 1717664805.185712,
            "needs_authentication": True,
        }
    ]
}

iaso_mocked_orgunits = {
    "orgUnits": [
        {
            "name": "ACEH",
            "id": 1978297,
            "parent_id": 1978331,
            "org_unit_type_id": 781,
            "org_unit_type_name": "Province",
            "validation_status": "VALID",
            "created_at": 1712825023.085615,
            "updated_at": 1712828860.665764,
        }
    ]
}


iaso_mocked_orgunits_with_params = {
    "orgunits": [
        {
            "name": "ACEH",
            "id": 1978297,
            "parent_id": 1978331,
            "org_unit_type_id": 781,
            "org_unit_type_name": "Province",
            "validation_status": "VALID",
            "created_at": 1712825023.085615,
            "updated_at": 1712828860.665764,
        }
    ]
}

iaso_mocked_instances = {
    "count": 28,
    "instances": [
        {
            "uuid": "4dc8c051-5b86-4b8e-b767-137e017d3c07",
            "export_id": "ArtNWdBsfAj",
            "file_name": "276_513ae6cf-5efa-4754-b7fb-2d2124ef3efd_2024-04-11_14-17-05.xml",
            "file_content": {
                "age": "14",
                "name": "qfdsf",
                "U1_u1": "U1",
                "address": "qsdfqsdf",
                "endtime": "2024-04-11T14:18:46.435+02:00",
                "village": "dddddd",
                "_version": "6004241215",
                "deviceid": "853e64340cfa95b8",
                "district": "badung",
                "location": "urban",
                "religion": "protestant",
                "username": "",
                "ethnicity": "sasak",
                "pregnancy": "yes",
                "starttime": "2024-04-11T14:17:05.394+02:00",
                "time_slot": "14_to_16",
                "instanceID": "uuid:676558f6-17f2-4a4f-a8f0-08b43cc572da",
                "occupation": "ffffffff",
                "subdistrict": "dddd",
                "children_age": "12,12",
                "partner_name": "",
                "phone_number": "111",
                "type_of_work": "formal",
                "have_children": "yes",
                "type_of_phone": "feature_phone",
                "devicephonenum": "",
                "final_comments": "thanks",
                "jkn_mobile_app": "no",
                "marital_status": "single",
                "preferred_date": "2024-04-11",
                "access_to_phone": "yes",
                "number_of_children": "1",
                "type_jnk_insurance": "pbi",
                "living_with_partner": "no",
                "enrolled_jnk_insurance": "yes",
                "person_with_disability": "yes",
                "education_participant_1": "no_education",
                "screening_questions_intro": "",
                "preferred_language_interview": "bahasa_daerah",
            },
            "file_url": "https://iaso-stg.s3.amazonaws.com/instances/276_513ae6cf-5efa-4754-b7fb-2d2124ef3efd_2024-04-11_14-17-05.xml?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAS4KZU3S6DZBAV5GW%2F20240611%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20240611T075045Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=7ebdbe2c44d8251589b31596aa61cf488fae5970a64a76084804b7c7cb9356c7",
            "id": 36627,
            "form_id": 276,
            "form_name": "Pathways Indonesia Recruitment (test)",
            "created_at": 1712837926.0,
            "updated_at": 1712837933.562898,
            "org_unit": {
                "name": "ACEH",
                "short_name": "ACEH",
                "id": 1978297,
                "source": "Indonesia",
                "source_id": 192,
                "source_ref": "ID001001000000000000",
                "parent_id": 1978331,
                "org_unit_type_id": 781,
                "org_unit_type_name": "Province",
                "org_unit_type_depth": 1,
                "created_at": 1712825023.085615,
                "updated_at": 1712828860.665764,
                "aliases": None,
                "validation_status": "VALID",
                "latitude": None,
                "longitude": None,
                "altitude": None,
                "has_geo_json": True,
                "version": 0,
                "opening_date": None,
                "closed_date": None,
            },
            "latitude": 50.8267504,
            "longitude": 4.3505693,
            "altitude": 113.30000305175781,
            "period": None,
            "status": "READY",
            "correlation_id": 36627503,
            "created_by": {
                "username": "mdewulf-pathways",
                "first_name": "Martin",
                "last_name": "De Wulf",
            },
            "last_modified_by": "mdewulf-pathways",
            "can_user_modify": True,
            "is_locked": False,
            "is_instance_of_reference_form": False,
            "is_reference_instance": False,
        },
        {
            "uuid": "d2fc1f2f-ed83-47db-b4db-be2679a26aff",
            "export_id": "pNI8aE6Am2Z",
            "file_name": "276_1770f9ff-254f-43af-9c13-21679a12a3d6_2024-04-12_11-47-29.xml",
            "file_content": {
                "age": "30",
                "name": "Test 1",
                "R1_r1": "R1",
                "address": "Test 1",
                "endtime": "2024-04-12T11:51:29.661+03:00",
                "village": "Test 1",
                "_version": "6004241215",
                "deviceid": "cb5f71d5c9b0f248",
                "district": "pidie",
                "location": "rural",
                "religion": "protestant",
                "username": "",
                "ethnicity": "aceh",
                "pregnancy": "no",
                "starttime": "2024-04-12T11:47:29.176+03:00",
                "time_slot": "12_to_14",
                "instanceID": "uuid:3b07bced-1155-4a3a-9324-189653cac25e",
                "occupation": "Test 1",
                "subdistrict": "Test 1",
                "partner_name": "",
                "phone_number": "235866358",
                "type_of_work": "informal",
                "have_children": "no",
                "type_of_phone": "smartphone",
                "devicephonenum": "",
                "final_comments": "Test 1",
                "jkn_mobile_app": "yes",
                "marital_status": "married_partner",
                "preferred_date": "2024-04-12",
                "access_to_phone": "yes",
                "jkn_mobile_app_use": "sometimes_use_it",
                "type_jnk_insurance": "pbi",
                "living_with_partner": "no",
                "enrolled_jnk_insurance": "yes",
                "person_with_disability": "no",
                "education_participant_1": "some_education",
                "hh_member_with_disability": "no",
                "screening_questions_intro": "",
                "preferred_language_interview": "bahasa_indonesia",
            },
            "file_url": "https://iaso-stg.s3.amazonaws.com/instances/276_1770f9ff-254f-43af-9c13-21679a12a3d6_2024-04-12_11-47-29.xml?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAS4KZU3S6DZBAV5GW%2F20240611%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20240611T075045Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=05eb2a925b34dd620cf35b27a0b9850f0dc4f0351e96a4c41ad4d82da58f11e6",
            "id": 36628,
            "form_id": 276,
            "form_name": "Pathways Indonesia Recruitment (test)",
            "created_at": 1712911889.0,
            "updated_at": 1712911890.646247,
            "org_unit": {
                "name": "ACEH",
                "short_name": "ACEH",
                "id": 1978297,
                "source": "Indonesia",
                "source_id": 192,
                "source_ref": "ID001001000000000000",
                "parent_id": 1978331,
                "org_unit_type_id": 781,
                "org_unit_type_name": "Province",
                "org_unit_type_depth": 1,
                "created_at": 1712825023.085615,
                "updated_at": 1712828860.665764,
                "aliases": None,
                "validation_status": "VALID",
                "latitude": None,
                "longitude": None,
                "altitude": None,
                "has_geo_json": True,
                "version": 0,
                "opening_date": None,
                "closed_date": None,
            },
            "latitude": 60.1916042,
            "longitude": 24.9458922,
            "altitude": 46.978047416201505,
            "period": None,
            "status": "READY",
            "correlation_id": 36628816,
            "created_by": None,
            "last_modified_by": None,
            "can_user_modify": True,
            "is_locked": False,
            "is_instance_of_reference_form": False,
            "is_reference_instance": False,
        },
    ],
    "has_next": True,
    "has_previous": False,
    "page": 1,
    "pages": 14,
    "limit": 2,
}
