accessmod_type_defs = """
    # Files
    type AccessmodFile {
        id: String!
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

accessmod_bindables = []
