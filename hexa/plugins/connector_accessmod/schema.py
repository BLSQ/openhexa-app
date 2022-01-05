from ariadne import QueryType

accessmod_type_defs = """
    # Files
    type AccessmodFile {
        id: String!
        name: String!
        fileName: String!
        mimeType: String!
        uri: String!
    }
    type AccessmodFilePage {
        pageNumber: Int!
        totalPages: Int!
        totalItems: Int!
        items: [AccessmodFile!]!
    }
    input AccessmodFileUploadUrlInput {
        fileName: String!
        mimeType: String
    }
    type AccessmodFileUploadUrlResult {
        success: Boolean!
        url: String!
    }
    input AccessmodFileInput {
        name: String!
        fileName: String!
        mimeType: String!
        uri: String!
    }
    type AccessmodFileResult {
        success: Boolean!
        accessModFile: AccessmodFile
    }
    extend type Query {
        accessModFiles: AccessmodFilePage!
        accessModFile(id: String!): AccessmodFile
    }
    extend type Mutation {
        generateAccessmodFileUploadUrl(input: AccessmodFileUploadUrlInput): AccessmodFileUploadUrlResult
        createAccessmodFile(input: AccessmodFileInput!): AccessmodFileResult!
    }
    
    # Other content
"""

accessmod_query = QueryType()


@accessmod_query.field("accessModFiles")
def resolve_accessmod_files(_, info):
    return {
        "total_pages": 1,
        "page_number": 1,
        "total_items": 3,
        "items": [
            {
                "id": "79bc2a17-50ed-42bf-9540-dfe860b158e8",
                "name": "Travel times scenarios",
                "file_name": "scenarios.csv",
                "mime_type": "text/csv",
                "uri": "/some/dir/scenarios.csv",
            },
            {
                "id": "a4043c07-379e-4c27-b2a8-df64e0238544",
                "file_name": "file2.tif",
                "mime_type": "image/tiff",
                "uri": "/some/dir/file2.tiff",
            },
            {
                "id": "720ae99f-8336-44ed-ba8c-2f7917afed88",
                "file_name": "file3.svg",
                "mime_type": "image/svg+xml",
                "uri": "/some/dir/file1.csv",
            },
        ],
    }


accessmod_bindables = []
