export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  AccessmodFilesetMetadata: { input: any; output: any; }
  BigInt: { input: any; output: any; }
  Date: { input: any; output: any; }
  DateTime: { input: any; output: any; }
  Generic: { input: any; output: any; }
  JSON: { input: any; output: any; }
  MovingSpeeds: { input: any; output: any; }
  OpaqueID: { input: any; output: any; }
  SimplifiedExtentType: { input: any; output: any; }
  StackPriorities: { input: any; output: any; }
  TimeThresholds: { input: any; output: any; }
  URL: { input: any; output: any; }
  UUID: { input: any; output: any; }
};

export type AccessmodAccessRequest = {
  __typename?: 'AccessmodAccessRequest';
  acceptedTos: Scalars['Boolean']['output'];
  createdAt: Scalars['DateTime']['output'];
  email: Scalars['String']['output'];
  firstName: Scalars['String']['output'];
  id: Scalars['String']['output'];
  lastName: Scalars['String']['output'];
  status: AccessmodAccessRequestStatus;
  updatedAt: Scalars['DateTime']['output'];
};

export type AccessmodAccessRequestPage = {
  __typename?: 'AccessmodAccessRequestPage';
  items: Array<AccessmodAccessRequest>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export enum AccessmodAccessRequestStatus {
  Approved = 'APPROVED',
  Denied = 'DENIED',
  Pending = 'PENDING'
}

export type AccessmodAccessibilityAnalysis = AccessmodAnalysis & AccessmodOwnership & {
  __typename?: 'AccessmodAccessibilityAnalysis';
  algorithm?: Maybe<AccessmodAccessibilityAnalysisAlgorithm>;
  author: User;
  barrier?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime']['output'];
  dem?: Maybe<AccessmodFileset>;
  frictionSurface?: Maybe<AccessmodFileset>;
  healthFacilities?: Maybe<AccessmodFileset>;
  id: Scalars['String']['output'];
  invertDirection?: Maybe<Scalars['Boolean']['output']>;
  knightMove?: Maybe<Scalars['Boolean']['output']>;
  landCover?: Maybe<AccessmodFileset>;
  maxTravelTime?: Maybe<Scalars['Int']['output']>;
  movingSpeeds?: Maybe<Scalars['MovingSpeeds']['output']>;
  name: Scalars['String']['output'];
  owner?: Maybe<AccessmodOwner>;
  permissions: AccessmodAnalysisPermissions;
  stack?: Maybe<AccessmodFileset>;
  stackPriorities?: Maybe<Scalars['StackPriorities']['output']>;
  status: AccessmodAnalysisStatus;
  transportNetwork?: Maybe<AccessmodFileset>;
  travelTimes?: Maybe<AccessmodFileset>;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime']['output'];
  water?: Maybe<AccessmodFileset>;
  waterAllTouched?: Maybe<Scalars['Boolean']['output']>;
};

export enum AccessmodAccessibilityAnalysisAlgorithm {
  Anisotropic = 'ANISOTROPIC',
  Isotropic = 'ISOTROPIC'
}

export type AccessmodAnalysis = {
  author: User;
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: AccessmodAnalysisPermissions;
  status: AccessmodAnalysisStatus;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime']['output'];
};

export type AccessmodAnalysisPage = {
  __typename?: 'AccessmodAnalysisPage';
  items: Array<AccessmodAnalysis>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type AccessmodAnalysisPermissions = {
  __typename?: 'AccessmodAnalysisPermissions';
  delete: Scalars['Boolean']['output'];
  run: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export enum AccessmodAnalysisStatus {
  Draft = 'DRAFT',
  Failed = 'FAILED',
  Queued = 'QUEUED',
  Ready = 'READY',
  Running = 'RUNNING',
  Success = 'SUCCESS'
}

export enum AccessmodAnalysisType {
  Accessibility = 'ACCESSIBILITY',
  GeographicCoverage = 'GEOGRAPHIC_COVERAGE',
  ZonalStatistics = 'ZONAL_STATISTICS'
}

export type AccessmodFile = {
  __typename?: 'AccessmodFile';
  createdAt: Scalars['DateTime']['output'];
  fileset?: Maybe<AccessmodFileset>;
  id: Scalars['String']['output'];
  mimeType: Scalars['String']['output'];
  name: Scalars['String']['output'];
  updatedAt: Scalars['DateTime']['output'];
  uri: Scalars['String']['output'];
};

export type AccessmodFileset = AccessmodOwnership & {
  __typename?: 'AccessmodFileset';
  author: User;
  createdAt: Scalars['DateTime']['output'];
  files: Array<AccessmodFile>;
  id: Scalars['String']['output'];
  metadata: Scalars['AccessmodFilesetMetadata']['output'];
  mode: AccessmodFilesetMode;
  name: Scalars['String']['output'];
  owner?: Maybe<AccessmodOwner>;
  permissions: AccessmodFilesetPermissions;
  role: AccessmodFilesetRole;
  status: AccessmodFilesetStatus;
  updatedAt: Scalars['DateTime']['output'];
};

export enum AccessmodFilesetFormat {
  Raster = 'RASTER',
  Tabular = 'TABULAR',
  Vector = 'VECTOR'
}

export enum AccessmodFilesetMode {
  AutomaticAcquisition = 'AUTOMATIC_ACQUISITION',
  UserInput = 'USER_INPUT'
}

export type AccessmodFilesetPage = {
  __typename?: 'AccessmodFilesetPage';
  items: Array<AccessmodFileset>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type AccessmodFilesetPermissions = {
  __typename?: 'AccessmodFilesetPermissions';
  createFile: Scalars['Boolean']['output'];
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export type AccessmodFilesetRole = {
  __typename?: 'AccessmodFilesetRole';
  code: AccessmodFilesetRoleCode;
  createdAt: Scalars['DateTime']['output'];
  format: AccessmodFilesetFormat;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  updatedAt: Scalars['DateTime']['output'];
};

export enum AccessmodFilesetRoleCode {
  Barrier = 'BARRIER',
  Boundaries = 'BOUNDARIES',
  Coverage = 'COVERAGE',
  Dem = 'DEM',
  FrictionSurface = 'FRICTION_SURFACE',
  Geometry = 'GEOMETRY',
  HealthFacilities = 'HEALTH_FACILITIES',
  LandCover = 'LAND_COVER',
  Population = 'POPULATION',
  Stack = 'STACK',
  TransportNetwork = 'TRANSPORT_NETWORK',
  TravelTimes = 'TRAVEL_TIMES',
  Water = 'WATER',
  ZonalStatistics = 'ZONAL_STATISTICS',
  ZonalStatisticsTable = 'ZONAL_STATISTICS_TABLE'
}

export enum AccessmodFilesetStatus {
  Invalid = 'INVALID',
  Pending = 'PENDING',
  ToAcquire = 'TO_ACQUIRE',
  Valid = 'VALID',
  Validating = 'VALIDATING'
}

export type AccessmodGeographicCoverageAnalysis = AccessmodAnalysis & AccessmodOwnership & {
  __typename?: 'AccessmodGeographicCoverageAnalysis';
  anisotropic?: Maybe<Scalars['Boolean']['output']>;
  author: User;
  catchmentAreas?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime']['output'];
  dem?: Maybe<AccessmodFileset>;
  frictionSurface?: Maybe<AccessmodFileset>;
  geographicCoverage?: Maybe<AccessmodFileset>;
  healthFacilities?: Maybe<AccessmodFileset>;
  hfProcessingOrder?: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  maxTravelTime?: Maybe<Scalars['Int']['output']>;
  name: Scalars['String']['output'];
  owner?: Maybe<AccessmodOwner>;
  permissions: AccessmodAnalysisPermissions;
  population?: Maybe<AccessmodFileset>;
  status: AccessmodAnalysisStatus;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime']['output'];
};

export type AccessmodOwner = Team | User;

export type AccessmodOwnership = {
  owner?: Maybe<AccessmodOwner>;
};

export type AccessmodProject = AccessmodOwnership & {
  __typename?: 'AccessmodProject';
  author: User;
  country: Country;
  createdAt: Scalars['DateTime']['output'];
  crs: Scalars['Int']['output'];
  dem?: Maybe<AccessmodFileset>;
  description: Scalars['String']['output'];
  extent?: Maybe<Array<Array<Scalars['Float']['output']>>>;
  id: Scalars['String']['output'];
  members: Array<AccessmodProjectMember>;
  name: Scalars['String']['output'];
  owner?: Maybe<AccessmodOwner>;
  permissions: AccessmodProjectPermissions;
  spatialResolution: Scalars['Int']['output'];
  updatedAt: Scalars['DateTime']['output'];
};

export type AccessmodProjectMember = {
  __typename?: 'AccessmodProjectMember';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['String']['output'];
  mode: PermissionMode;
  permissions: AccessmodProjectMemberPermissions;
  project: AccessmodProject;
  team?: Maybe<Team>;
  updatedAt: Scalars['DateTime']['output'];
  user?: Maybe<User>;
};

export type AccessmodProjectMemberPermissions = {
  __typename?: 'AccessmodProjectMemberPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export enum AccessmodProjectOrder {
  NameAsc = 'NAME_ASC',
  NameDesc = 'NAME_DESC',
  UpdatedAtAsc = 'UPDATED_AT_ASC',
  UpdatedAtDesc = 'UPDATED_AT_DESC'
}

export type AccessmodProjectPage = {
  __typename?: 'AccessmodProjectPage';
  items: Array<AccessmodProject>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type AccessmodProjectPermissions = {
  __typename?: 'AccessmodProjectPermissions';
  createAnalysis: Scalars['Boolean']['output'];
  createFileset: Scalars['Boolean']['output'];
  createMember: Scalars['Boolean']['output'];
  createPermission: Scalars['Boolean']['output'];
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export type AccessmodZonalStatistics = AccessmodAnalysis & AccessmodOwnership & {
  __typename?: 'AccessmodZonalStatistics';
  author: User;
  boundaries?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  owner?: Maybe<AccessmodOwner>;
  permissions: AccessmodAnalysisPermissions;
  population?: Maybe<AccessmodFileset>;
  status: AccessmodAnalysisStatus;
  timeThresholds?: Maybe<Scalars['TimeThresholds']['output']>;
  travelTimes?: Maybe<AccessmodFileset>;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime']['output'];
  zonalStatisticsGeo?: Maybe<AccessmodFileset>;
  zonalStatisticsTable?: Maybe<AccessmodFileset>;
};

/** Represents the input for adding an output to a pipeline. */
export type AddPipelineOutputInput = {
  name?: InputMaybe<Scalars['String']['input']>;
  type: Scalars['String']['input'];
  uri: Scalars['String']['input'];
};

/** Represents the result of adding an output to a pipeline. */
export type AddPipelineOutputResult = {
  __typename?: 'AddPipelineOutputResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

export type AddPipelineRecipientResult = {
  __typename?: 'AddPipelineRecipientResult';
  errors: Array<PipelineRecipientError>;
  recipient?: Maybe<PipelineRecipient>;
  success: Scalars['Boolean']['output'];
};

export enum ApproveAccessmodAccessRequestError {
  Invalid = 'INVALID'
}

export type ApproveAccessmodAccessRequestInput = {
  id: Scalars['String']['input'];
};

export type ApproveAccessmodAccessRequestResult = {
  __typename?: 'ApproveAccessmodAccessRequestResult';
  errors: Array<ApproveAccessmodAccessRequestError>;
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when archiving a workspace. */
export enum ArchiveWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for archiving a workspace. */
export type ArchiveWorkspaceInput = {
  slug: Scalars['String']['input'];
};

/** Represents the result of archiving a workspace. */
export type ArchiveWorkspaceResult = {
  __typename?: 'ArchiveWorkspaceResult';
  errors: Array<ArchiveWorkspaceError>;
  success: Scalars['Boolean']['output'];
};

/** The Avatar type represents the avatar of a user. */
export type Avatar = {
  __typename?: 'Avatar';
  /** The color of the user's avatar. */
  color: Scalars['String']['output'];
  /** The initials of the user's avatar. */
  initials: Scalars['String']['output'];
};

/** A bucket is where all the files and data related to a workspace are stored. */
export type Bucket = {
  __typename?: 'Bucket';
  name: Scalars['String']['output'];
  object?: Maybe<BucketObject>;
  objects: BucketObjectPage;
};


/** A bucket is where all the files and data related to a workspace are stored. */
export type BucketObjectArgs = {
  key: Scalars['String']['input'];
};


/** A bucket is where all the files and data related to a workspace are stored. */
export type BucketObjectsArgs = {
  ignoreHiddenFiles?: InputMaybe<Scalars['Boolean']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  prefix?: InputMaybe<Scalars['String']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
};

/** An object in a workspace's bucket. */
export type BucketObject = {
  __typename?: 'BucketObject';
  key: Scalars['String']['output'];
  name: Scalars['String']['output'];
  path: Scalars['String']['output'];
  size?: Maybe<Scalars['BigInt']['output']>;
  type: BucketObjectType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

/** A page of objects in a workspace's bucket. */
export type BucketObjectPage = {
  __typename?: 'BucketObjectPage';
  hasNextPage: Scalars['Boolean']['output'];
  hasPreviousPage: Scalars['Boolean']['output'];
  items: Array<BucketObject>;
  pageNumber: Scalars['Int']['output'];
};

/** The type of an object in a workspace's bucket. */
export enum BucketObjectType {
  Directory = 'DIRECTORY',
  File = 'FILE'
}

export type Config = {
  __typename?: 'Config';
  /** List of requirements for the password. */
  passwordRequirements?: Maybe<Array<Scalars['String']['output']>>;
};

/** Represents a connection to an external data source or service. */
export type Connection = {
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};

/** Represents a field in a connection. */
export type ConnectionField = {
  __typename?: 'ConnectionField';
  code: Scalars['String']['output'];
  createdAt: Scalars['DateTime']['output'];
  secret: Scalars['Boolean']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  value?: Maybe<Scalars['String']['output']>;
};

/** Represents the input for a connection field. */
export type ConnectionFieldInput = {
  code: Scalars['String']['input'];
  secret: Scalars['Boolean']['input'];
  value?: InputMaybe<Scalars['String']['input']>;
};

/** Represents the permissions of a connection. */
export type ConnectionPermissions = {
  __typename?: 'ConnectionPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

/** Represents the types of connections. */
export enum ConnectionType {
  Custom = 'CUSTOM',
  Dhis2 = 'DHIS2',
  Gcs = 'GCS',
  Iaso = 'IASO',
  Postgresql = 'POSTGRESQL',
  S3 = 'S3'
}

export type Country = {
  __typename?: 'Country';
  alpha3: Scalars['String']['output'];
  code: Scalars['String']['output'];
  flag: Scalars['String']['output'];
  name: Scalars['String']['output'];
  whoInfo: WhoInfo;
};

export type CountryInput = {
  alpha3?: InputMaybe<Scalars['String']['input']>;
  code: Scalars['String']['input'];
  flag?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

export enum CreateAccessmodAccessibilityAnalysisError {
  NameDuplicate = 'NAME_DUPLICATE'
}

export type CreateAccessmodAccessibilityAnalysisInput = {
  name: Scalars['String']['input'];
  projectId: Scalars['String']['input'];
};

export type CreateAccessmodAccessibilityAnalysisResult = {
  __typename?: 'CreateAccessmodAccessibilityAnalysisResult';
  analysis?: Maybe<AccessmodAccessibilityAnalysis>;
  errors: Array<CreateAccessmodAccessibilityAnalysisError>;
  success: Scalars['Boolean']['output'];
};

export enum CreateAccessmodFileError {
  UriDuplicate = 'URI_DUPLICATE'
}

export type CreateAccessmodFileInput = {
  filesetId: Scalars['String']['input'];
  mimeType: Scalars['String']['input'];
  uri: Scalars['String']['input'];
};

export type CreateAccessmodFileResult = {
  __typename?: 'CreateAccessmodFileResult';
  errors: Array<CreateAccessmodFileError>;
  file?: Maybe<AccessmodFile>;
  success: Scalars['Boolean']['output'];
};

export enum CreateAccessmodFilesetError {
  NameDuplicate = 'NAME_DUPLICATE',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateAccessmodFilesetInput = {
  automatic?: InputMaybe<Scalars['Boolean']['input']>;
  metadata?: InputMaybe<Scalars['AccessmodFilesetMetadata']['input']>;
  name: Scalars['String']['input'];
  projectId: Scalars['String']['input'];
  roleId: Scalars['String']['input'];
};

export type CreateAccessmodFilesetResult = {
  __typename?: 'CreateAccessmodFilesetResult';
  errors: Array<CreateAccessmodFilesetError>;
  fileset?: Maybe<AccessmodFileset>;
  success: Scalars['Boolean']['output'];
};

export enum CreateAccessmodProjectError {
  NameDuplicate = 'NAME_DUPLICATE',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateAccessmodProjectInput = {
  country: CountryInput;
  crs: Scalars['Int']['input'];
  description?: InputMaybe<Scalars['String']['input']>;
  extent?: InputMaybe<Array<Array<Scalars['Float']['input']>>>;
  name: Scalars['String']['input'];
  spatialResolution: Scalars['Int']['input'];
};

export enum CreateAccessmodProjectMemberError {
  AlreadyExists = 'ALREADY_EXISTS',
  NotFound = 'NOT_FOUND',
  NotImplemented = 'NOT_IMPLEMENTED',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateAccessmodProjectMemberInput = {
  mode: PermissionMode;
  projectId: Scalars['String']['input'];
  teamId?: InputMaybe<Scalars['String']['input']>;
  userId?: InputMaybe<Scalars['String']['input']>;
};

export type CreateAccessmodProjectMemberResult = {
  __typename?: 'CreateAccessmodProjectMemberResult';
  errors: Array<CreateAccessmodProjectMemberError>;
  member?: Maybe<AccessmodProjectMember>;
  success: Scalars['Boolean']['output'];
};

export type CreateAccessmodProjectResult = {
  __typename?: 'CreateAccessmodProjectResult';
  errors: Array<CreateAccessmodProjectError>;
  project?: Maybe<AccessmodProject>;
  success: Scalars['Boolean']['output'];
};

export enum CreateAccessmodZonalStatisticsError {
  NameDuplicate = 'NAME_DUPLICATE'
}

export type CreateAccessmodZonalStatisticsInput = {
  name: Scalars['String']['input'];
  projectId: Scalars['String']['input'];
};

export type CreateAccessmodZonalStatisticsResult = {
  __typename?: 'CreateAccessmodZonalStatisticsResult';
  analysis?: Maybe<AccessmodZonalStatistics>;
  errors: Array<CreateAccessmodZonalStatisticsError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when creating a folder in a workspace's bucket. */
export enum CreateBucketFolderError {
  AlreadyExists = 'ALREADY_EXISTS',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for creating a folder in a workspace's bucket. */
export type CreateBucketFolderInput = {
  folderKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** The result of creating a folder in a workspace's bucket. */
export type CreateBucketFolderResult = {
  __typename?: 'CreateBucketFolderResult';
  errors: Array<CreateBucketFolderError>;
  folder?: Maybe<BucketObject>;
  success: Scalars['Boolean']['output'];
};

/** Represents the error types for creating a connection. */
export enum CreateConnectionError {
  InvalidSlug = 'INVALID_SLUG',
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the input for creating a connection. */
export type CreateConnectionInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  fields?: InputMaybe<Array<ConnectionFieldInput>>;
  name: Scalars['String']['input'];
  slug?: InputMaybe<Scalars['String']['input']>;
  type: ConnectionType;
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of creating a connection. */
export type CreateConnectionResult = {
  __typename?: 'CreateConnectionResult';
  connection?: Maybe<Connection>;
  errors: Array<CreateConnectionError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when creating a dataset. */
export enum CreateDatasetError {
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Input for creating a dataset. */
export type CreateDatasetInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  name: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Result of creating a dataset. */
export type CreateDatasetResult = {
  __typename?: 'CreateDatasetResult';
  dataset?: Maybe<Dataset>;
  errors: Array<CreateDatasetError>;
  link?: Maybe<DatasetLink>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when creating a dataset version. */
export enum CreateDatasetVersionError {
  DatasetNotFound = 'DATASET_NOT_FOUND',
  DuplicateName = 'DUPLICATE_NAME',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Errors that can occur when creating a dataset version file. */
export enum CreateDatasetVersionFileError {
  AlreadyExists = 'ALREADY_EXISTS',
  InvalidUri = 'INVALID_URI',
  LockedVersion = 'LOCKED_VERSION',
  PermissionDenied = 'PERMISSION_DENIED',
  VersionNotFound = 'VERSION_NOT_FOUND'
}

/** Input for creating a dataset version file. */
export type CreateDatasetVersionFileInput = {
  contentType: Scalars['String']['input'];
  uri: Scalars['String']['input'];
  versionId: Scalars['ID']['input'];
};

/** Result of creating a dataset version file. */
export type CreateDatasetVersionFileResult = {
  __typename?: 'CreateDatasetVersionFileResult';
  errors: Array<CreateDatasetVersionFileError>;
  /** The created file object */
  file?: Maybe<DatasetVersionFile>;
  success: Scalars['Boolean']['output'];
  /**
   * The URL to upload the file to
   * @deprecated moved to dedicated generateDatasetUploadUrl mutation
   */
  uploadUrl: Scalars['String']['output'];
};

/** Input for creating a dataset version. */
export type CreateDatasetVersionInput = {
  changelog?: InputMaybe<Scalars['String']['input']>;
  datasetId: Scalars['ID']['input'];
  name: Scalars['String']['input'];
};

/** Result of creating a dataset version. */
export type CreateDatasetVersionResult = {
  __typename?: 'CreateDatasetVersionResult';
  errors: Array<CreateDatasetVersionError>;
  success: Scalars['Boolean']['output'];
  version?: Maybe<DatasetVersion>;
};

/** The CreateMembershipError enum represents the possible errors that can occur during the createMembership mutation. */
export enum CreateMembershipError {
  /** Indicates that a membership with the same user and team already exists. */
  AlreadyExists = 'ALREADY_EXISTS',
  /** Indicates that the team or user was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to create a membership in the team. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The CreateMembershipInput type represents the input for the createMembership mutation. */
export type CreateMembershipInput = {
  /** The role of the user in the team. */
  role: MembershipRole;
  /** The unique identifier of the team. */
  teamId: Scalars['UUID']['input'];
  /** The email address of the user to add to the team. */
  userEmail: Scalars['String']['input'];
};

/** The CreateMembershipResult type represents the result of the createMembership mutation. */
export type CreateMembershipResult = {
  __typename?: 'CreateMembershipResult';
  /** The list of errors that occurred during the createMembership mutation. */
  errors: Array<CreateMembershipError>;
  /** The created membership object. */
  membership?: Maybe<Membership>;
  /** Indicates whether the createMembership mutation was successful. */
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when creating a pipeline from a template version. */
export enum CreatePipelineFromTemplateVersionError {
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineAlreadyExists = 'PIPELINE_ALREADY_EXISTS',
  PipelineTemplateVersionNotFound = 'PIPELINE_TEMPLATE_VERSION_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the input for creating a new pipeline from a template version. */
export type CreatePipelineFromTemplateVersionInput = {
  pipelineTemplateVersionId: Scalars['UUID']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of creating a new pipeline from a template version. */
export type CreatePipelineFromTemplateVersionResult = {
  __typename?: 'CreatePipelineFromTemplateVersionResult';
  errors?: Maybe<Array<CreatePipelineFromTemplateVersionError>>;
  pipeline?: Maybe<Pipeline>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for creating a pipeline. */
export type CreatePipelineInput = {
  code: Scalars['String']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  notebookPath?: InputMaybe<Scalars['String']['input']>;
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the input for adding a recipient to a pipeline. */
export type CreatePipelineRecipientInput = {
  notificationLevel: PipelineNotificationLevel;
  pipelineId: Scalars['UUID']['input'];
  userId: Scalars['UUID']['input'];
};

/** Represents the result of creating a pipeline. */
export type CreatePipelineResult = {
  __typename?: 'CreatePipelineResult';
  errors: Array<PipelineError>;
  pipeline?: Maybe<Pipeline>;
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when creating a pipeline template version. */
export enum CreatePipelineTemplateVersionError {
  DuplicateTemplateNameOrCode = 'DUPLICATE_TEMPLATE_NAME_OR_CODE',
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineVersionNotFound = 'PIPELINE_VERSION_NOT_FOUND',
  UnknownError = 'UNKNOWN_ERROR',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the input for creating a new pipeline template version. */
export type CreatePipelineTemplateVersionInput = {
  changelog?: InputMaybe<Scalars['String']['input']>;
  code?: InputMaybe<Scalars['String']['input']>;
  config?: InputMaybe<Scalars['String']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  pipelineId: Scalars['UUID']['input'];
  pipelineVersionId: Scalars['UUID']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of creating a new pipeline template version. */
export type CreatePipelineTemplateVersionResult = {
  __typename?: 'CreatePipelineTemplateVersionResult';
  errors?: Maybe<Array<CreatePipelineTemplateVersionError>>;
  pipelineTemplate?: Maybe<PipelineTemplate>;
  success: Scalars['Boolean']['output'];
};

/** The CreateTeamError enum represents the possible errors that can occur during the createTeam mutation. */
export enum CreateTeamError {
  /** Indicates that a team with the same name already exists. */
  NameDuplicate = 'NAME_DUPLICATE',
  /** Indicates that the user does not have permission to create a team. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The CreateTeamInput type represents the input for the createTeam mutation. */
export type CreateTeamInput = {
  /** The name of the team. */
  name: Scalars['String']['input'];
};

/** The CreateTeamResult type represents the result of the createTeam mutation. */
export type CreateTeamResult = {
  __typename?: 'CreateTeamResult';
  /** The list of errors that occurred during the createTeam mutation. */
  errors: Array<CreateTeamError>;
  /** Indicates whether the createTeam mutation was successful. */
  success: Scalars['Boolean']['output'];
  /** The created team object. */
  team?: Maybe<Team>;
};

/** Enum representing the possible errors that can occur when creating a workspace. */
export enum CreateWorkspaceError {
  InvalidSlug = 'INVALID_SLUG',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for creating a workspace. */
export type CreateWorkspaceInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  loadSampleData?: InputMaybe<Scalars['Boolean']['input']>;
  name: Scalars['String']['input'];
  slug?: InputMaybe<Scalars['String']['input']>;
};

/** Represents the result of creating a workspace. */
export type CreateWorkspaceResult = {
  __typename?: 'CreateWorkspaceResult';
  errors: Array<CreateWorkspaceError>;
  success: Scalars['Boolean']['output'];
  workspace?: Maybe<Workspace>;
};

/** Custom connection object */
export type CustomConnection = Connection & {
  __typename?: 'CustomConnection';
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};

export type Dag = {
  __typename?: 'DAG';
  countries: Array<Country>;
  description?: Maybe<Scalars['String']['output']>;
  externalId: Scalars['String']['output'];
  externalUrl?: Maybe<Scalars['URL']['output']>;
  formCode?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  label: Scalars['String']['output'];
  runs: DagRunPage;
  schedule?: Maybe<Scalars['String']['output']>;
  tags: Array<Tag>;
  template: DagTemplate;
  user?: Maybe<User>;
};


export type DagRunsArgs = {
  orderBy?: InputMaybe<DagRunOrderBy>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export type DagPage = {
  __typename?: 'DAGPage';
  items: Array<Dag>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type DagRun = {
  __typename?: 'DAGRun';
  config?: Maybe<Scalars['JSON']['output']>;
  duration?: Maybe<Scalars['Int']['output']>;
  executionDate?: Maybe<Scalars['DateTime']['output']>;
  externalId?: Maybe<Scalars['String']['output']>;
  externalUrl?: Maybe<Scalars['URL']['output']>;
  id: Scalars['UUID']['output'];
  isFavorite: Scalars['Boolean']['output'];
  label?: Maybe<Scalars['String']['output']>;
  lastRefreshedAt?: Maybe<Scalars['DateTime']['output']>;
  logs?: Maybe<Scalars['String']['output']>;
  messages: Array<DagRunMessage>;
  outputs: Array<DagRunOutput>;
  progress: Scalars['Int']['output'];
  status: DagRunStatus;
  triggerMode?: Maybe<DagRunTrigger>;
  user?: Maybe<User>;
};

export type DagRunMessage = {
  __typename?: 'DAGRunMessage';
  message: Scalars['String']['output'];
  priority: Scalars['String']['output'];
  timestamp?: Maybe<Scalars['DateTime']['output']>;
};

export enum DagRunOrderBy {
  ExecutionDateAsc = 'EXECUTION_DATE_ASC',
  ExecutionDateDesc = 'EXECUTION_DATE_DESC'
}

export type DagRunOutput = {
  __typename?: 'DAGRunOutput';
  title: Scalars['String']['output'];
  uri: Scalars['String']['output'];
};

export type DagRunPage = {
  __typename?: 'DAGRunPage';
  items: Array<DagRun>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export enum DagRunStatus {
  Failed = 'failed',
  Queued = 'queued',
  Running = 'running',
  Stopped = 'stopped',
  Success = 'success',
  Terminating = 'terminating'
}

export enum DagRunTrigger {
  Manual = 'MANUAL',
  Scheduled = 'SCHEDULED'
}

export type DagTemplate = {
  __typename?: 'DAGTemplate';
  code: Scalars['String']['output'];
  description?: Maybe<Scalars['String']['output']>;
  sampleConfig?: Maybe<Scalars['JSON']['output']>;
};

/** DHIS2 connection object */
export type Dhis2Connection = Connection & {
  __typename?: 'DHIS2Connection';
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  queryMetadata: Dhis2QueryResult;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};


/** DHIS2 connection object */
export type Dhis2ConnectionQueryMetadataArgs = {
  filter?: InputMaybe<Scalars['String']['input']>;
  type: Scalars['String']['input'];
};

export enum Dhis2ConnectionError {
  ConnectionError = 'CONNECTION_ERROR',
  UnknownError = 'UNKNOWN_ERROR'
}

/** DHIS2 metadata item */
export type Dhis2MetadataItem = {
  __typename?: 'DHIS2MetadataItem';
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

/** DHIS2 metadata query result */
export type Dhis2QueryResult = {
  __typename?: 'DHIS2QueryResult';
  error?: Maybe<Dhis2ConnectionError>;
  items?: Maybe<Array<Dhis2MetadataItem>>;
  success: Scalars['Boolean']['output'];
};

export type Database = {
  __typename?: 'Database';
  credentials?: Maybe<DatabaseCredentials>;
  table?: Maybe<DatabaseTable>;
  tables: DatabaseTablePage;
};


export type DatabaseTableArgs = {
  name: Scalars['String']['input'];
};


export type DatabaseTablesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export type DatabaseCredentials = {
  __typename?: 'DatabaseCredentials';
  dbName: Scalars['String']['output'];
  host: Scalars['String']['output'];
  password: Scalars['String']['output'];
  port: Scalars['Int']['output'];
  url: Scalars['String']['output'];
  username: Scalars['String']['output'];
};

/** Represents a database table. */
export type DatabaseTable = {
  __typename?: 'DatabaseTable';
  /** The columns of the table. */
  columns: Array<TableColumn>;
  /** The number of rows in the table. */
  count?: Maybe<Scalars['Int']['output']>;
  /** The name of the table. */
  name: Scalars['String']['output'];
  /** Retrieves a paginated list of rows from the table. */
  rows: TableRowsPage;
  /** A sample row from the table. */
  sample: Scalars['JSON']['output'];
};


/** Represents a database table. */
export type DatabaseTableRowsArgs = {
  direction: OrderByDirection;
  orderBy: Scalars['String']['input'];
  page: Scalars['Int']['input'];
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

/** Represents a paginated list of database tables. */
export type DatabaseTablePage = {
  __typename?: 'DatabaseTablePage';
  /** The tables in the current page. */
  items: Array<DatabaseTable>;
  /** The page number of the result. */
  pageNumber: Scalars['Int']['output'];
  /** The total number of items. */
  totalItems: Scalars['Int']['output'];
  /** The total number of pages. */
  totalPages: Scalars['Int']['output'];
};

/** Dataset is a collection of files that are related to each other and are versioned. */
export type Dataset = MetadataObject & {
  __typename?: 'Dataset';
  attributes: Array<MetadataAttribute>;
  createdAt: Scalars['DateTime']['output'];
  createdBy?: Maybe<User>;
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  latestVersion?: Maybe<DatasetVersion>;
  links: DatasetLinkPage;
  name: Scalars['String']['output'];
  permissions: DatasetPermissions;
  slug: Scalars['String']['output'];
  targetId: Scalars['OpaqueID']['output'];
  updatedAt: Scalars['DateTime']['output'];
  version?: Maybe<DatasetVersion>;
  versions: DatasetVersionPage;
  workspace?: Maybe<Workspace>;
};


/** Dataset is a collection of files that are related to each other and are versioned. */
export type DatasetLinksArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


/** Dataset is a collection of files that are related to each other and are versioned. */
export type DatasetVersionArgs = {
  id: Scalars['ID']['input'];
};


/** Dataset is a collection of files that are related to each other and are versioned. */
export type DatasetVersionsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

/** File sample for dataset file */
export type DatasetFileSample = {
  __typename?: 'DatasetFileSample';
  sample?: Maybe<Scalars['JSON']['output']>;
  status: FileSampleStatus;
  statusReason?: Maybe<Scalars['String']['output']>;
};

/** A link of a dataset with a workspace. */
export type DatasetLink = {
  __typename?: 'DatasetLink';
  createdAt: Scalars['DateTime']['output'];
  createdBy?: Maybe<User>;
  dataset: Dataset;
  id: Scalars['ID']['output'];
  isPinned: Scalars['Boolean']['output'];
  permissions: DatasetLinkPermissions;
  workspace: Workspace;
};

/** A page of dataset links. */
export type DatasetLinkPage = {
  __typename?: 'DatasetLinkPage';
  items: Array<DatasetLink>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Permissions of a dataset link. */
export type DatasetLinkPermissions = {
  __typename?: 'DatasetLinkPermissions';
  /** Permissions to delete the link between the workspace and the dataset */
  delete: Scalars['Boolean']['output'];
  /** Permissions to pin the dataset for the workspace */
  pin: Scalars['Boolean']['output'];
};

/** A page of datasets. */
export type DatasetPage = {
  __typename?: 'DatasetPage';
  items: Array<Dataset>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Permissions of a dataset. */
export type DatasetPermissions = {
  __typename?: 'DatasetPermissions';
  /** Permissions to create a new version of the dataset */
  createVersion: Scalars['Boolean']['output'];
  /** Permissions to delete the dataset */
  delete: Scalars['Boolean']['output'];
  /** Permissions to edit the dataset */
  update: Scalars['Boolean']['output'];
};

/** A version of a dataset. A version is a snapshot of the dataset at a point in time. */
export type DatasetVersion = MetadataObject & {
  __typename?: 'DatasetVersion';
  attributes: Array<MetadataAttribute>;
  changelog?: Maybe<Scalars['String']['output']>;
  createdAt: Scalars['DateTime']['output'];
  createdBy?: Maybe<User>;
  dataset: Dataset;
  /** @deprecated use changelog instead */
  description?: Maybe<Scalars['String']['output']>;
  fileByName?: Maybe<DatasetVersionFile>;
  files: DatasetVersionFilePage;
  id: Scalars['ID']['output'];
  name: Scalars['String']['output'];
  permissions: DatasetVersionPermissions;
  targetId: Scalars['OpaqueID']['output'];
};


/** A version of a dataset. A version is a snapshot of the dataset at a point in time. */
export type DatasetVersionFileByNameArgs = {
  name: Scalars['String']['input'];
};


/** A version of a dataset. A version is a snapshot of the dataset at a point in time. */
export type DatasetVersionFilesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

/** A file in a dataset version. */
export type DatasetVersionFile = MetadataObject & {
  __typename?: 'DatasetVersionFile';
  attributes: Array<MetadataAttribute>;
  contentType: Scalars['String']['output'];
  createdAt: Scalars['DateTime']['output'];
  createdBy?: Maybe<User>;
  downloadUrl?: Maybe<Scalars['String']['output']>;
  fileSample?: Maybe<DatasetFileSample>;
  filename: Scalars['String']['output'];
  id: Scalars['ID']['output'];
  properties?: Maybe<Scalars['JSON']['output']>;
  size: Scalars['BigInt']['output'];
  targetId: Scalars['OpaqueID']['output'];
  uri: Scalars['String']['output'];
};


/** A file in a dataset version. */
export type DatasetVersionFileDownloadUrlArgs = {
  attachment?: InputMaybe<Scalars['Boolean']['input']>;
};

/** A page of dataset version files. */
export type DatasetVersionFilePage = {
  __typename?: 'DatasetVersionFilePage';
  items: Array<DatasetVersionFile>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** A page of dataset versions. */
export type DatasetVersionPage = {
  __typename?: 'DatasetVersionPage';
  items: Array<DatasetVersion>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Permissions of a dataset version. */
export type DatasetVersionPermissions = {
  __typename?: 'DatasetVersionPermissions';
  /** Permissions to delete the dataset version */
  delete: Scalars['Boolean']['output'];
  /** Permissions to download the content of the dataset version */
  download: Scalars['Boolean']['output'];
  /** Permissions to update the dataset version */
  update: Scalars['Boolean']['output'];
};

/** Represents the error types for declining a workspace invitation. */
export enum DeclineWorkspaceInvitationError {
  InvitationNotFound = 'INVITATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for declining a workspace invitation. */
export type DeclineWorkspaceInvitationInput = {
  invitationId: Scalars['UUID']['input'];
};

/** Represents the result of declining a workspace invitation. */
export type DeclineWorkspaceInvitationResult = {
  __typename?: 'DeclineWorkspaceInvitationResult';
  errors: Array<DeclineWorkspaceInvitationError>;
  invitation?: Maybe<WorkspaceInvitation>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteAccessmodAnalysisError {
  DeleteFailed = 'DELETE_FAILED',
  NotFound = 'NOT_FOUND'
}

export type DeleteAccessmodAnalysisInput = {
  id: Scalars['String']['input'];
};

export type DeleteAccessmodAnalysisResult = {
  __typename?: 'DeleteAccessmodAnalysisResult';
  errors: Array<DeleteAccessmodAnalysisError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteAccessmodFilesetError {
  FilesetInUse = 'FILESET_IN_USE',
  NotFound = 'NOT_FOUND'
}

export type DeleteAccessmodFilesetInput = {
  id: Scalars['String']['input'];
};

export type DeleteAccessmodFilesetResult = {
  __typename?: 'DeleteAccessmodFilesetResult';
  errors: Array<DeleteAccessmodFilesetError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteAccessmodProjectError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteAccessmodProjectInput = {
  id: Scalars['String']['input'];
};

export enum DeleteAccessmodProjectMemberError {
  NotFound = 'NOT_FOUND',
  NotImplemented = 'NOT_IMPLEMENTED',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteAccessmodProjectMemberInput = {
  id: Scalars['String']['input'];
};

export type DeleteAccessmodProjectMemberResult = {
  __typename?: 'DeleteAccessmodProjectMemberResult';
  errors: Array<DeleteAccessmodProjectMemberError>;
  success: Scalars['Boolean']['output'];
};

export type DeleteAccessmodProjectResult = {
  __typename?: 'DeleteAccessmodProjectResult';
  errors: Array<DeleteAccessmodProjectError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when deleting an object from a workspace's bucket. */
export enum DeleteBucketObjectError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for deleting an object from a workspace's bucket. */
export type DeleteBucketObjectInput = {
  objectKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** The result of deleting an object from a workspace's bucket. */
export type DeleteBucketObjectResult = {
  __typename?: 'DeleteBucketObjectResult';
  errors: Array<DeleteBucketObjectError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the error types for deleting a connection. */
export enum DeleteConnectionError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for deleting a connection. */
export type DeleteConnectionInput = {
  id: Scalars['String']['input'];
};

/** Represents the result of deleting a connection. */
export type DeleteConnectionResult = {
  __typename?: 'DeleteConnectionResult';
  errors: Array<DeleteConnectionError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when deleting a dataset. */
export enum DeleteDatasetError {
  DatasetNotFound = 'DATASET_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for deleting a dataset. */
export type DeleteDatasetInput = {
  id: Scalars['ID']['input'];
};

/** Errors that can occur when deleting a dataset link. */
export enum DeleteDatasetLinkError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for deleting a dataset link. */
export type DeleteDatasetLinkInput = {
  id: Scalars['ID']['input'];
};

/** Result of deleting a dataset link. */
export type DeleteDatasetLinkResult = {
  __typename?: 'DeleteDatasetLinkResult';
  errors: Array<DeleteDatasetLinkError>;
  success: Scalars['Boolean']['output'];
};

/** Result of deleting a dataset. */
export type DeleteDatasetResult = {
  __typename?: 'DeleteDatasetResult';
  errors: Array<DeleteDatasetError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when deleting a dataset version. */
export enum DeleteDatasetVersionError {
  PermissionDenied = 'PERMISSION_DENIED',
  VersionNotFound = 'VERSION_NOT_FOUND'
}

/** Input for deleting a dataset version. */
export type DeleteDatasetVersionInput = {
  versionId: Scalars['ID']['input'];
};

/** Result of deleting a dataset version. */
export type DeleteDatasetVersionResult = {
  __typename?: 'DeleteDatasetVersionResult';
  errors: Array<DeleteDatasetVersionError>;
  success: Scalars['Boolean']['output'];
};

/** The DeleteMembershipError enum represents the possible errors that can occur during the deleteMembership mutation. */
export enum DeleteMembershipError {
  /** Indicates that the membership was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to delete the membership. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The DeleteMembershipInput type represents the input for the deleteMembership mutation. */
export type DeleteMembershipInput = {
  /** The unique identifier of the membership to delete. */
  id: Scalars['UUID']['input'];
};

/** The DeleteMembershipResult type represents the result of the deleteMembership mutation. */
export type DeleteMembershipResult = {
  __typename?: 'DeleteMembershipResult';
  /** The list of errors that occurred during the deleteMembership mutation. */
  errors: Array<DeleteMembershipError>;
  /** Indicates whether the deleteMembership mutation was successful. */
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when deleting an attribute. */
export enum DeleteMetadataAttributeError {
  MetadataAttributeNotFound = 'METADATA_ATTRIBUTE_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED',
  TargetNotFound = 'TARGET_NOT_FOUND'
}

/** Input to delete custom attribute */
export type DeleteMetadataAttributeInput = {
  key: Scalars['String']['input'];
  targetId: Scalars['OpaqueID']['input'];
};

export type DeleteMetadataAttributeResult = {
  __typename?: 'DeleteMetadataAttributeResult';
  errors: Array<DeleteMetadataAttributeError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for deleting a pipeline. */
export type DeletePipelineInput = {
  id: Scalars['UUID']['input'];
};

/** Represents the input for deleting a pipeline recipient. */
export type DeletePipelineRecipientInput = {
  recipientId: Scalars['UUID']['input'];
};

export type DeletePipelineRecipientResult = {
  __typename?: 'DeletePipelineRecipientResult';
  errors: Array<PipelineRecipientError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the result of deleting a pipeline. */
export type DeletePipelineResult = {
  __typename?: 'DeletePipelineResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for deleting a pipeline template. */
export type DeletePipelineTemplateInput = {
  id: Scalars['UUID']['input'];
};

/** Represents the result of deleting a pipeline. */
export type DeletePipelineTemplateResult = {
  __typename?: 'DeletePipelineTemplateResult';
  errors: Array<PipelineTemplateError>;
  success: Scalars['Boolean']['output'];
};

export enum DeletePipelineVersionError {
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineVersionNotFound = 'PIPELINE_VERSION_NOT_FOUND'
}

/** Represents the input for deleting a pipeline version. */
export type DeletePipelineVersionInput = {
  id: Scalars['UUID']['input'];
};

/** Represents the result of deleting a pipeline version. */
export type DeletePipelineVersionResult = {
  __typename?: 'DeletePipelineVersionResult';
  errors: Array<DeletePipelineVersionError>;
  success: Scalars['Boolean']['output'];
};

/** The DeleteTeamError enum represents the possible errors that can occur during the deleteTeam mutation. */
export enum DeleteTeamError {
  /** Indicates that the team was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to delete the team. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The DeleteTeamInput type represents the input for the deleteTeam mutation. */
export type DeleteTeamInput = {
  /** The unique identifier of the team to delete. */
  id: Scalars['UUID']['input'];
};

/** The DeleteTeamResult type represents the result of the deleteTeam mutation. */
export type DeleteTeamResult = {
  __typename?: 'DeleteTeamResult';
  /** The list of errors that occurred during the deleteTeam mutation. */
  errors: Array<DeleteTeamError>;
  /** Indicates whether the deleteTeam mutation was successful. */
  success: Scalars['Boolean']['output'];
};

export enum DeleteTemplateVersionError {
  PermissionDenied = 'PERMISSION_DENIED',
  TemplateNotFound = 'TEMPLATE_NOT_FOUND',
  TemplateVersionNotFound = 'TEMPLATE_VERSION_NOT_FOUND'
}

/** Represents the input for deleting a template version. */
export type DeleteTemplateVersionInput = {
  id: Scalars['UUID']['input'];
};

/** Represents the result of deleting a template version. */
export type DeleteTemplateVersionResult = {
  __typename?: 'DeleteTemplateVersionResult';
  errors: Array<DeleteTemplateVersionError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteWorkspaceDatabaseTableError {
  PermissionDenied = 'PERMISSION_DENIED',
  TableNotFound = 'TABLE_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the input for deleting a database table in a workspace. */
export type DeleteWorkspaceDatabaseTableInput = {
  table: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of deleting a database table in a workspace. */
export type DeleteWorkspaceDatabaseTableResult = {
  __typename?: 'DeleteWorkspaceDatabaseTableResult';
  errors: Array<DeleteWorkspaceDatabaseTableError>;
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when deleting a workspace. */
export enum DeleteWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for deleting a workspace. */
export type DeleteWorkspaceInput = {
  slug: Scalars['String']['input'];
};

/** Represents the error types for deleting a workspace invitation. */
export enum DeleteWorkspaceInvitationError {
  InvitationNotFound = 'INVITATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for deleting a workspace invitation. */
export type DeleteWorkspaceInvitationInput = {
  invitationId: Scalars['UUID']['input'];
};

/** Represents the result of deleting a workspace invitation. */
export type DeleteWorkspaceInvitationResult = {
  __typename?: 'DeleteWorkspaceInvitationResult';
  errors: Array<DeleteWorkspaceInvitationError>;
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when deleting a workspace member. */
export enum DeleteWorkspaceMemberError {
  MembershipNotFound = 'MEMBERSHIP_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for deleting a workspace member. */
export type DeleteWorkspaceMemberInput = {
  membershipId: Scalars['UUID']['input'];
};

/** Represents the result of deleting a workspace member. */
export type DeleteWorkspaceMemberResult = {
  __typename?: 'DeleteWorkspaceMemberResult';
  errors: Array<DeleteWorkspaceMemberError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the result of deleting a workspace. */
export type DeleteWorkspaceResult = {
  __typename?: 'DeleteWorkspaceResult';
  errors: Array<DeleteWorkspaceError>;
  success: Scalars['Boolean']['output'];
};

export enum DenyAccessmodAccessRequestError {
  Invalid = 'INVALID'
}

export type DenyAccessmodAccessRequestInput = {
  id: Scalars['String']['input'];
};

export type DenyAccessmodAccessRequestResult = {
  __typename?: 'DenyAccessmodAccessRequestResult';
  errors: Array<DenyAccessmodAccessRequestError>;
  success: Scalars['Boolean']['output'];
};

/** The DisableTwoFactorError enum represents the possible errors that can occur during the disableTwoFactor mutation. */
export enum DisableTwoFactorError {
  InvalidOtp = 'INVALID_OTP',
  NotEnabled = 'NOT_ENABLED'
}

/** The DisableTwoFactorInput type represents the input for the disableTwoFactor mutation. */
export type DisableTwoFactorInput = {
  token: Scalars['String']['input'];
};

/** The DisableTwoFactorResult type represents the result of the disableTwoFactor mutation. */
export type DisableTwoFactorResult = {
  __typename?: 'DisableTwoFactorResult';
  errors?: Maybe<Array<DisableTwoFactorError>>;
  success: Scalars['Boolean']['output'];
};

/** The EnableTwoFactorError enum represents the possible errors that can occur during the enableTwoFactor mutation. */
export enum EnableTwoFactorError {
  AlreadyEnabled = 'ALREADY_ENABLED',
  EmailMismatch = 'EMAIL_MISMATCH'
}

/** The EnableTwoFactorInput type represents the input for the enableTwoFactor mutation. */
export type EnableTwoFactorInput = {
  email?: InputMaybe<Scalars['String']['input']>;
};

/** The EnableTwoFactorResult type represents the result of the enableTwoFactor mutation. */
export type EnableTwoFactorResult = {
  __typename?: 'EnableTwoFactorResult';
  errors?: Maybe<Array<EnableTwoFactorError>>;
  success: Scalars['Boolean']['output'];
  verified?: Maybe<Scalars['Boolean']['output']>;
};

/** The FeatureFlag type represents a feature flag in the system. */
export type FeatureFlag = {
  __typename?: 'FeatureFlag';
  /** The code of the feature flag. */
  code: Scalars['String']['output'];
  /** The configuration of the feature flag. */
  config: Scalars['JSON']['output'];
};

/** Statuses that can occur when generating file sample */
export enum FileSampleStatus {
  Failed = 'FAILED',
  Finished = 'FINISHED',
  Processing = 'PROCESSING'
}

/** GCS connection object */
export type GcsConnection = Connection & {
  __typename?: 'GCSConnection';
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};

/** The GenerateChallengeError enum represents the possible errors that can occur during the generateChallenge mutation. */
export enum GenerateChallengeError {
  ChallengeError = 'CHALLENGE_ERROR',
  DeviceNotFound = 'DEVICE_NOT_FOUND'
}

/** The GenerateChallengeResult type represents the result of the generateChallenge mutation. */
export type GenerateChallengeResult = {
  __typename?: 'GenerateChallengeResult';
  errors?: Maybe<Array<GenerateChallengeError>>;
  success: Scalars['Boolean']['output'];
};

/** Input for creating un upload link for the file */
export type GenerateDatasetUploadUrlInput = {
  contentType: Scalars['String']['input'];
  uri: Scalars['String']['input'];
  versionId: Scalars['ID']['input'];
};

/** Result of creating an upload url */
export type GenerateDatasetUploadUrlResult = {
  __typename?: 'GenerateDatasetUploadUrlResult';
  errors: Array<CreateDatasetVersionFileError>;
  success: Scalars['Boolean']['output'];
  uploadUrl?: Maybe<Scalars['String']['output']>;
};

/** Possible errors when generating a new database password. */
export enum GenerateNewDatabasePasswordError {
  /** The database was not found. */
  NotFound = 'NOT_FOUND',
  /** The user does not have permission to generate a new password. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for generating a new database password. */
export type GenerateNewDatabasePasswordInput = {
  /** The slug of the workspace. */
  workspaceSlug: Scalars['String']['input'];
};

/** The result of generating a new database password. */
export type GenerateNewDatabasePasswordResult = {
  __typename?: 'GenerateNewDatabasePasswordResult';
  /** The errors that occurred during password generation. */
  errors: Array<GenerateNewDatabasePasswordError>;
  /** Indicates if the password generation was successful. */
  success: Scalars['Boolean']['output'];
  /** The workspace associated with the generated password. */
  workspace?: Maybe<Workspace>;
};

export enum GeneratePipelineWebhookUrlError {
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  WebhookNotEnabled = 'WEBHOOK_NOT_ENABLED'
}

export type GeneratePipelineWebhookUrlInput = {
  id: Scalars['UUID']['input'];
};

export type GeneratePipelineWebhookUrlResult = {
  __typename?: 'GeneratePipelineWebhookUrlResult';
  errors: Array<GeneratePipelineWebhookUrlError>;
  pipeline?: Maybe<Pipeline>;
  success: Scalars['Boolean']['output'];
};

/** Represents the error types for generating a workspace token. */
export enum GenerateWorkspaceTokenError {
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the input for generating a workspace token. */
export type GenerateWorkspaceTokenInput = {
  slug: Scalars['String']['input'];
};

/** Represents the result of generating a workspace token. */
export type GenerateWorkspaceTokenResult = {
  __typename?: 'GenerateWorkspaceTokenResult';
  errors: Array<GenerateWorkspaceTokenError>;
  success: Scalars['Boolean']['output'];
  token?: Maybe<Scalars['String']['output']>;
};

/** Represents a generic output of a pipeline run. */
export type GenericOutput = {
  __typename?: 'GenericOutput';
  name?: Maybe<Scalars['String']['output']>;
  type: Scalars['String']['output'];
  uri: Scalars['String']['output'];
};

/** IASO connection object */
export type IasoConnection = Connection & {
  __typename?: 'IASOConnection';
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};

/** Represents the input for inviting a member to a workspace. */
export type InviteWorkspaceMemberInput = {
  role: WorkspaceMembershipRole;
  userEmail: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of inviting a member to a workspace. */
export type InviteWorkspaceMemberResult = {
  __typename?: 'InviteWorkspaceMemberResult';
  errors: Array<InviteWorkspaceMembershipError>;
  success: Scalars['Boolean']['output'];
  workspaceMembership?: Maybe<WorkspaceMembership>;
};

/** Enum representing the possible errors that can occur when inviting a user to a workspace. */
export enum InviteWorkspaceMembershipError {
  AlreadyExists = 'ALREADY_EXISTS',
  PermissionDenied = 'PERMISSION_DENIED',
  UserNotFound = 'USER_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the error types for joining a workspace. */
export enum JoinWorkspaceError {
  AlreadyAccepted = 'ALREADY_ACCEPTED',
  AlreadyExists = 'ALREADY_EXISTS',
  InvitationNotFound = 'INVITATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for joining a workspace. */
export type JoinWorkspaceInput = {
  invitationId: Scalars['UUID']['input'];
};

/** Represents the result of joining a workspace. */
export type JoinWorkspaceResult = {
  __typename?: 'JoinWorkspaceResult';
  errors: Array<JoinWorkspaceError>;
  invitation?: Maybe<WorkspaceInvitation>;
  success: Scalars['Boolean']['output'];
  workspace?: Maybe<Workspace>;
};

export enum LaunchAccessmodAnalysisError {
  LaunchFailed = 'LAUNCH_FAILED'
}

export type LaunchAccessmodAnalysisInput = {
  id: Scalars['String']['input'];
};

export type LaunchAccessmodAnalysisResult = {
  __typename?: 'LaunchAccessmodAnalysisResult';
  analysis?: Maybe<AccessmodAnalysis>;
  errors: Array<LaunchAccessmodAnalysisError>;
  success: Scalars['Boolean']['output'];
};

export enum LaunchNotebookServerError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type LaunchNotebookServerInput = {
  workspaceSlug: Scalars['String']['input'];
};

export type LaunchNotebookServerResult = {
  __typename?: 'LaunchNotebookServerResult';
  errors: Array<LaunchNotebookServerError>;
  server?: Maybe<NotebookServer>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when linking a dataset with a workspace. */
export enum LinkDatasetError {
  AlreadyLinked = 'ALREADY_LINKED',
  DatasetNotFound = 'DATASET_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Input for linking a dataset with a workspace. */
export type LinkDatasetInput = {
  datasetId: Scalars['ID']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Result of linking a dataset with a workspace. */
export type LinkDatasetResult = {
  __typename?: 'LinkDatasetResult';
  errors: Array<LinkDatasetError>;
  link?: Maybe<DatasetLink>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for logging a pipeline message. */
export type LogPipelineMessageInput = {
  message: Scalars['String']['input'];
  priority: MessagePriority;
};

/** Represents the result of logging a pipeline message. */
export type LogPipelineMessageResult = {
  __typename?: 'LogPipelineMessageResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

/** The LoginError enum represents the possible errors that can occur during the login process. */
export enum LoginError {
  /** Indicates that the provided credentials are invalid. */
  InvalidCredentials = 'INVALID_CREDENTIALS',
  /** Indicates that the provided OTP is invalid. */
  InvalidOtp = 'INVALID_OTP',
  /** Indicates that an OTP (one-time password) is required for login. */
  OtpRequired = 'OTP_REQUIRED'
}

/** The LoginInput type represents the input for the login mutation. */
export type LoginInput = {
  /** The email address of the user. */
  email: Scalars['String']['input'];
  /** The password of the user. */
  password: Scalars['String']['input'];
  /** The token for two-factor authentication. */
  token?: InputMaybe<Scalars['String']['input']>;
};

/** The LoginResult type represents the result of the login mutation. */
export type LoginResult = {
  __typename?: 'LoginResult';
  /** The list of errors that occurred during the login process. */
  errors?: Maybe<Array<LoginError>>;
  /** Indicates whether the login was successful. */
  success: Scalars['Boolean']['output'];
};

/** The LogoutResult type represents the result of the logout mutation. */
export type LogoutResult = {
  __typename?: 'LogoutResult';
  /** Indicates whether the logout was successful. */
  success: Scalars['Boolean']['output'];
};

/** The Me type represents the currently authenticated user. */
export type Me = {
  __typename?: 'Me';
  /** The feature flags assigned to the currently authenticated user. */
  features: Array<FeatureFlag>;
  hasTwoFactorEnabled: Scalars['Boolean']['output'];
  /** The permissions assigned to the currently authenticated user. */
  permissions: MePermissions;
  /** The user object representing the currently authenticated user. */
  user?: Maybe<User>;
};

/** The MePermissions type represents the permissions of the currently authenticated user. */
export type MePermissions = {
  __typename?: 'MePermissions';
  /** Indicates whether the user has permission to access the admin panel. */
  adminPanel: Scalars['Boolean']['output'];
  createAccessmodProject: Scalars['Boolean']['output'];
  /** Indicates whether the user has permission to create a team. */
  createTeam: Scalars['Boolean']['output'];
  createWorkspace: Scalars['Boolean']['output'];
  manageAccessmodAccessRequests: Scalars['Boolean']['output'];
  /** Indicates whether the user has superuser privileges. */
  superUser: Scalars['Boolean']['output'];
};

/** The Membership type represents a membership of a user in a team. */
export type Membership = {
  __typename?: 'Membership';
  /** The date when the membership was created. */
  createdAt: Scalars['DateTime']['output'];
  /** The unique identifier of the membership. */
  id: Scalars['UUID']['output'];
  /** The permissions assigned to the membership. */
  permissions: MembershipPermissions;
  /** The role of the user in the team. */
  role: MembershipRole;
  /** The team associated with the membership. */
  team: Team;
  /** The date when the membership was last updated. */
  updatedAt: Scalars['DateTime']['output'];
  /** The user associated with the membership. */
  user: User;
};

/** The MembershipPage type represents a paginated list of memberships. */
export type MembershipPage = {
  __typename?: 'MembershipPage';
  /** The list of memberships on the current page. */
  items: Array<Membership>;
  /** The current page number. */
  pageNumber: Scalars['Int']['output'];
  /** The total number of items. */
  totalItems: Scalars['Int']['output'];
  /** The total number of pages. */
  totalPages: Scalars['Int']['output'];
};

/** The MembershipPermissions type represents the permissions of a membership. */
export type MembershipPermissions = {
  __typename?: 'MembershipPermissions';
  /** Indicates whether the user has permission to delete the membership. */
  delete: Scalars['Boolean']['output'];
  /** Indicates whether the user has permission to update the membership. */
  update: Scalars['Boolean']['output'];
};

/** The MembershipRole enum represents the role of a user in a team. */
export enum MembershipRole {
  /** Indicates that the user is an admin of the team. */
  Admin = 'ADMIN',
  /** Indicates that the user is a regular member of the team. */
  Regular = 'REGULAR'
}

/** An enumeration representing the priority levels of a message. */
export enum MessagePriority {
  Critical = 'CRITICAL',
  Debug = 'DEBUG',
  Error = 'ERROR',
  Info = 'INFO',
  Warning = 'WARNING'
}

/** Generic metadata attribute */
export type MetadataAttribute = {
  __typename?: 'MetadataAttribute';
  createdAt: Scalars['DateTime']['output'];
  createdBy?: Maybe<User>;
  id: Scalars['UUID']['output'];
  key: Scalars['String']['output'];
  label?: Maybe<Scalars['String']['output']>;
  system: Scalars['Boolean']['output'];
  updatedAt: Scalars['DateTime']['output'];
  updatedBy?: Maybe<User>;
  value?: Maybe<Scalars['JSON']['output']>;
};

/** Interface for type implementing metadata */
export type MetadataObject = {
  attributes: Array<MetadataAttribute>;
  targetId: Scalars['OpaqueID']['output'];
};

export type Mutation = {
  __typename?: 'Mutation';
  /** Adds an output to a pipeline. */
  addPipelineOutput: AddPipelineOutputResult;
  /** Adds a recipient to a pipeline. */
  addPipelineRecipient: AddPipelineRecipientResult;
  approveAccessmodAccessRequest: ApproveAccessmodAccessRequestResult;
  archiveWorkspace: ArchiveWorkspaceResult;
  createAccessmodAccessibilityAnalysis: CreateAccessmodAccessibilityAnalysisResult;
  createAccessmodFile: CreateAccessmodFileResult;
  createAccessmodFileset: CreateAccessmodFilesetResult;
  createAccessmodProject: CreateAccessmodProjectResult;
  createAccessmodProjectMember: CreateAccessmodProjectMemberResult;
  createAccessmodZonalStatistics: CreateAccessmodZonalStatisticsResult;
  /** Create a folder in a workspace's bucket. */
  createBucketFolder: CreateBucketFolderResult;
  createConnection: CreateConnectionResult;
  /** Create a new dataset. */
  createDataset: CreateDatasetResult;
  /** Create a new dataset version. */
  createDatasetVersion: CreateDatasetVersionResult;
  /** Create a new file in a dataset version. */
  createDatasetVersionFile: CreateDatasetVersionFileResult;
  createMembership: CreateMembershipResult;
  /** Creates a new pipeline. */
  createPipeline: CreatePipelineResult;
  createPipelineFromTemplateVersion: CreatePipelineFromTemplateVersionResult;
  /** Creates a new pipeline template version. */
  createPipelineTemplateVersion: CreatePipelineTemplateVersionResult;
  createTeam: CreateTeamResult;
  createWorkspace: CreateWorkspaceResult;
  declineWorkspaceInvitation: DeclineWorkspaceInvitationResult;
  deleteAccessmodAnalysis: DeleteAccessmodAnalysisResult;
  deleteAccessmodFileset: DeleteAccessmodFilesetResult;
  deleteAccessmodProject: DeleteAccessmodProjectResult;
  deleteAccessmodProjectMember: DeleteAccessmodProjectMemberResult;
  /** Delete an object from a workspace's bucket. */
  deleteBucketObject: DeleteBucketObjectResult;
  deleteConnection: DeleteConnectionResult;
  /** Delete a dataset. */
  deleteDataset: DeleteDatasetResult;
  /** Delete a dataset link. */
  deleteDatasetLink: DeleteDatasetLinkResult;
  /** Delete a dataset version. */
  deleteDatasetVersion: DeleteDatasetVersionResult;
  deleteMembership: DeleteMembershipResult;
  /** Delete an metadata attribute from an object instance */
  deleteMetadataAttribute: DeleteMetadataAttributeResult;
  /** Deletes a pipeline. */
  deletePipeline: DeletePipelineResult;
  /** Deletes a pipeline recipient. */
  deletePipelineRecipient: DeletePipelineRecipientResult;
  deletePipelineTemplate: DeletePipelineTemplateResult;
  /** Deletes a pipeline version. */
  deletePipelineVersion: DeletePipelineVersionResult;
  deleteTeam: DeleteTeamResult;
  deleteTemplateVersion: DeleteTemplateVersionResult;
  deleteWorkspace: DeleteWorkspaceResult;
  deleteWorkspaceDatabaseTable?: Maybe<DeleteWorkspaceDatabaseTableResult>;
  deleteWorkspaceInvitation: DeleteWorkspaceInvitationResult;
  deleteWorkspaceMember: DeleteWorkspaceMemberResult;
  denyAccessmodAccessRequest: DenyAccessmodAccessRequestResult;
  /** Disables two-factor authentication for the currently authenticated user. */
  disableTwoFactor: DisableTwoFactorResult;
  /** Enables two-factor authentication for the currently authenticated user. */
  enableTwoFactor: EnableTwoFactorResult;
  /** Generates a challenge for two-factor authentication. */
  generateChallenge: GenerateChallengeResult;
  /** Create dataset version file upload url. */
  generateDatasetUploadUrl: GenerateDatasetUploadUrlResult;
  /** Generates a new password for a database. */
  generateNewDatabasePassword: GenerateNewDatabasePasswordResult;
  /** Generates a webhook URL for a pipeline. */
  generatePipelineWebhookUrl: GeneratePipelineWebhookUrlResult;
  generateWorkspaceToken: GenerateWorkspaceTokenResult;
  inviteWorkspaceMember: InviteWorkspaceMemberResult;
  joinWorkspace: JoinWorkspaceResult;
  launchAccessmodAnalysis: LaunchAccessmodAnalysisResult;
  launchNotebookServer: LaunchNotebookServerResult;
  /** Link a dataset with a workspace. */
  linkDataset: LinkDatasetResult;
  /** Logs a message for a pipeline. */
  logPipelineMessage: LogPipelineMessageResult;
  /** Authenticates a user and generates an access token. */
  login: LoginResult;
  /** Logs out the currently authenticated user. */
  logout: LogoutResult;
  /** Pin or unpin a dataset for a workspace. */
  pinDataset: PinDatasetResult;
  /** Retrieves a token for a pipeline. */
  pipelineToken: PipelineTokenResult;
  prepareAccessmodFileDownload: PrepareAccessmodFileDownloadResult;
  prepareAccessmodFileUpload: PrepareAccessmodFileUploadResult;
  prepareAccessmodFilesetVisualizationDownload: PrepareAccessmodFilesetVisualizationDownloadResult;
  prepareDownloadURL?: Maybe<PrepareDownloadUrlResult>;
  /** Prepare to download an object from a workspace's bucket. */
  prepareObjectDownload: PrepareObjectDownloadResult;
  /** Prepare to upload an object to a workspace's bucket. */
  prepareObjectUpload: PrepareObjectUploadResult;
  /** Prepare to download a file in a dataset version. */
  prepareVersionFileDownload: PrepareVersionFileDownloadResult;
  /** Registers a new user. */
  register: RegisterResult;
  requestAccessmodAccess: RequestAccessmodAccessInputResult;
  resendWorkspaceInvitation: ResendWorkspaceInvitationResult;
  /** Sends a password reset email to the user. */
  resetPassword: ResetPasswordResult;
  runDAG: RunDagResult;
  /** Runs a pipeline. */
  runPipeline: RunPipelineResult;
  setDAGRunFavorite?: Maybe<SetDagRunFavoriteResult>;
  /** Set a custom metadata attribute to an object instance */
  setMetadataAttribute: SetMetadataAttributeResult;
  /** Sets a new password for the user. */
  setPassword: SetPasswordResult;
  /** Stops a pipeline. */
  stopPipeline: StopPipelineResult;
  updateAccessmodAccessibilityAnalysis: UpdateAccessmodAccessibilityAnalysisResult;
  updateAccessmodFileset: UpdateAccessmodFilesetResult;
  updateAccessmodProject: UpdateAccessmodProjectResult;
  updateAccessmodProjectMember: UpdateAccessmodProjectMemberResult;
  updateAccessmodZonalStatistics: UpdateAccessmodZonalStatisticsResult;
  updateConnection: UpdateConnectionResult;
  updateDAG: UpdateDagResult;
  /** Update a dataset. */
  updateDataset: UpdateDatasetResult;
  /** Update a dataset version. */
  updateDatasetVersion: UpdateDatasetVersionResult;
  updateMembership: UpdateMembershipResult;
  /** Updates an existing pipeline. */
  updatePipeline: UpdatePipelineResult;
  /** Updates the progress of a pipeline. */
  updatePipelineProgress: UpdatePipelineProgressResult;
  /** Updates a pipeline recipient. */
  updatePipelineRecipient: UpdatePipelineRecipientResult;
  /** Updates an existing template. */
  updatePipelineTemplate: UpdateTemplateResult;
  /** Updates a pipeline version. */
  updatePipelineVersion: UpdatePipelineVersionResult;
  updateTeam: UpdateTeamResult;
  updateTemplateVersion: UpdateTemplateVersionResult;
  /** Updates the profile of the currently authenticated user. */
  updateUser: UpdateUserResult;
  updateWorkspace: UpdateWorkspaceResult;
  updateWorkspaceMember: UpdateWorkspaceMemberResult;
  /** Upgrades a pipeline version using the latest template version. */
  upgradePipelineVersionFromTemplate: UpgradePipelineVersionFromTemplateResult;
  /** Uploads a pipeline. */
  uploadPipeline: UploadPipelineResult;
  /** Verifies a device for two-factor authentication. */
  verifyDevice: VerifyDeviceResult;
};


export type MutationAddPipelineOutputArgs = {
  input: AddPipelineOutputInput;
};


export type MutationAddPipelineRecipientArgs = {
  input: CreatePipelineRecipientInput;
};


export type MutationApproveAccessmodAccessRequestArgs = {
  input: ApproveAccessmodAccessRequestInput;
};


export type MutationArchiveWorkspaceArgs = {
  input: ArchiveWorkspaceInput;
};


export type MutationCreateAccessmodAccessibilityAnalysisArgs = {
  input?: InputMaybe<CreateAccessmodAccessibilityAnalysisInput>;
};


export type MutationCreateAccessmodFileArgs = {
  input: CreateAccessmodFileInput;
};


export type MutationCreateAccessmodFilesetArgs = {
  input: CreateAccessmodFilesetInput;
};


export type MutationCreateAccessmodProjectArgs = {
  input: CreateAccessmodProjectInput;
};


export type MutationCreateAccessmodProjectMemberArgs = {
  input: CreateAccessmodProjectMemberInput;
};


export type MutationCreateAccessmodZonalStatisticsArgs = {
  input?: InputMaybe<CreateAccessmodZonalStatisticsInput>;
};


export type MutationCreateBucketFolderArgs = {
  input: CreateBucketFolderInput;
};


export type MutationCreateConnectionArgs = {
  input: CreateConnectionInput;
};


export type MutationCreateDatasetArgs = {
  input: CreateDatasetInput;
};


export type MutationCreateDatasetVersionArgs = {
  input: CreateDatasetVersionInput;
};


export type MutationCreateDatasetVersionFileArgs = {
  input: CreateDatasetVersionFileInput;
};


export type MutationCreateMembershipArgs = {
  input: CreateMembershipInput;
};


export type MutationCreatePipelineArgs = {
  input: CreatePipelineInput;
};


export type MutationCreatePipelineFromTemplateVersionArgs = {
  input: CreatePipelineFromTemplateVersionInput;
};


export type MutationCreatePipelineTemplateVersionArgs = {
  input: CreatePipelineTemplateVersionInput;
};


export type MutationCreateTeamArgs = {
  input: CreateTeamInput;
};


export type MutationCreateWorkspaceArgs = {
  input: CreateWorkspaceInput;
};


export type MutationDeclineWorkspaceInvitationArgs = {
  input: DeclineWorkspaceInvitationInput;
};


export type MutationDeleteAccessmodAnalysisArgs = {
  input?: InputMaybe<DeleteAccessmodAnalysisInput>;
};


export type MutationDeleteAccessmodFilesetArgs = {
  input: DeleteAccessmodFilesetInput;
};


export type MutationDeleteAccessmodProjectArgs = {
  input: DeleteAccessmodProjectInput;
};


export type MutationDeleteAccessmodProjectMemberArgs = {
  input: DeleteAccessmodProjectMemberInput;
};


export type MutationDeleteBucketObjectArgs = {
  input: DeleteBucketObjectInput;
};


export type MutationDeleteConnectionArgs = {
  input: DeleteConnectionInput;
};


export type MutationDeleteDatasetArgs = {
  input: DeleteDatasetInput;
};


export type MutationDeleteDatasetLinkArgs = {
  input: DeleteDatasetLinkInput;
};


export type MutationDeleteDatasetVersionArgs = {
  input: DeleteDatasetVersionInput;
};


export type MutationDeleteMembershipArgs = {
  input: DeleteMembershipInput;
};


export type MutationDeleteMetadataAttributeArgs = {
  input: DeleteMetadataAttributeInput;
};


export type MutationDeletePipelineArgs = {
  input?: InputMaybe<DeletePipelineInput>;
};


export type MutationDeletePipelineRecipientArgs = {
  input: DeletePipelineRecipientInput;
};


export type MutationDeletePipelineTemplateArgs = {
  input?: InputMaybe<DeletePipelineTemplateInput>;
};


export type MutationDeletePipelineVersionArgs = {
  input: DeletePipelineVersionInput;
};


export type MutationDeleteTeamArgs = {
  input: DeleteTeamInput;
};


export type MutationDeleteTemplateVersionArgs = {
  input: DeleteTemplateVersionInput;
};


export type MutationDeleteWorkspaceArgs = {
  input: DeleteWorkspaceInput;
};


export type MutationDeleteWorkspaceDatabaseTableArgs = {
  input: DeleteWorkspaceDatabaseTableInput;
};


export type MutationDeleteWorkspaceInvitationArgs = {
  input: DeleteWorkspaceInvitationInput;
};


export type MutationDeleteWorkspaceMemberArgs = {
  input: DeleteWorkspaceMemberInput;
};


export type MutationDenyAccessmodAccessRequestArgs = {
  input: DenyAccessmodAccessRequestInput;
};


export type MutationDisableTwoFactorArgs = {
  input?: InputMaybe<DisableTwoFactorInput>;
};


export type MutationEnableTwoFactorArgs = {
  input?: InputMaybe<EnableTwoFactorInput>;
};


export type MutationGenerateDatasetUploadUrlArgs = {
  input: GenerateDatasetUploadUrlInput;
};


export type MutationGenerateNewDatabasePasswordArgs = {
  input: GenerateNewDatabasePasswordInput;
};


export type MutationGeneratePipelineWebhookUrlArgs = {
  input: GeneratePipelineWebhookUrlInput;
};


export type MutationGenerateWorkspaceTokenArgs = {
  input: GenerateWorkspaceTokenInput;
};


export type MutationInviteWorkspaceMemberArgs = {
  input: InviteWorkspaceMemberInput;
};


export type MutationJoinWorkspaceArgs = {
  input: JoinWorkspaceInput;
};


export type MutationLaunchAccessmodAnalysisArgs = {
  input?: InputMaybe<LaunchAccessmodAnalysisInput>;
};


export type MutationLaunchNotebookServerArgs = {
  input: LaunchNotebookServerInput;
};


export type MutationLinkDatasetArgs = {
  input: LinkDatasetInput;
};


export type MutationLogPipelineMessageArgs = {
  input: LogPipelineMessageInput;
};


export type MutationLoginArgs = {
  input: LoginInput;
};


export type MutationPinDatasetArgs = {
  input: PinDatasetInput;
};


export type MutationPipelineTokenArgs = {
  input: PipelineTokenInput;
};


export type MutationPrepareAccessmodFileDownloadArgs = {
  input: PrepareAccessmodFileDownloadInput;
};


export type MutationPrepareAccessmodFileUploadArgs = {
  input: PrepareAccessmodFileUploadInput;
};


export type MutationPrepareAccessmodFilesetVisualizationDownloadArgs = {
  input: PrepareAccessmodFilesetVisualizationDownloadInput;
};


export type MutationPrepareDownloadUrlArgs = {
  input: PrepareDownloadUrlInput;
};


export type MutationPrepareObjectDownloadArgs = {
  input: PrepareObjectDownloadInput;
};


export type MutationPrepareObjectUploadArgs = {
  input: PrepareObjectUploadInput;
};


export type MutationPrepareVersionFileDownloadArgs = {
  input: PrepareVersionFileDownloadInput;
};


export type MutationRegisterArgs = {
  input: RegisterInput;
};


export type MutationRequestAccessmodAccessArgs = {
  input: RequestAccessmodAccessInput;
};


export type MutationResendWorkspaceInvitationArgs = {
  input: ResendWorkspaceInvitationInput;
};


export type MutationResetPasswordArgs = {
  input: ResetPasswordInput;
};


export type MutationRunDagArgs = {
  input: RunDagInput;
};


export type MutationRunPipelineArgs = {
  input?: InputMaybe<RunPipelineInput>;
};


export type MutationSetDagRunFavoriteArgs = {
  input: SetDagRunFavoriteInput;
};


export type MutationSetMetadataAttributeArgs = {
  input: SetMetadataAttributeInput;
};


export type MutationSetPasswordArgs = {
  input: SetPasswordInput;
};


export type MutationStopPipelineArgs = {
  input: StopPipelineInput;
};


export type MutationUpdateAccessmodAccessibilityAnalysisArgs = {
  input?: InputMaybe<UpdateAccessmodAccessibilityAnalysisInput>;
};


export type MutationUpdateAccessmodFilesetArgs = {
  input: UpdateAccessmodFilesetInput;
};


export type MutationUpdateAccessmodProjectArgs = {
  input: UpdateAccessmodProjectInput;
};


export type MutationUpdateAccessmodProjectMemberArgs = {
  input: UpdateAccessmodProjectMemberInput;
};


export type MutationUpdateAccessmodZonalStatisticsArgs = {
  input?: InputMaybe<UpdateAccessmodZonalStatisticsInput>;
};


export type MutationUpdateConnectionArgs = {
  input: UpdateConnectionInput;
};


export type MutationUpdateDagArgs = {
  input: UpdateDagInput;
};


export type MutationUpdateDatasetArgs = {
  input: UpdateDatasetInput;
};


export type MutationUpdateDatasetVersionArgs = {
  input: UpdateDatasetVersionInput;
};


export type MutationUpdateMembershipArgs = {
  input: UpdateMembershipInput;
};


export type MutationUpdatePipelineArgs = {
  input: UpdatePipelineInput;
};


export type MutationUpdatePipelineProgressArgs = {
  input: UpdatePipelineProgressInput;
};


export type MutationUpdatePipelineRecipientArgs = {
  input: UpdatePipelineRecipientInput;
};


export type MutationUpdatePipelineTemplateArgs = {
  input: UpdateTemplateInput;
};


export type MutationUpdatePipelineVersionArgs = {
  input: UpdatePipelineVersionInput;
};


export type MutationUpdateTeamArgs = {
  input: UpdateTeamInput;
};


export type MutationUpdateTemplateVersionArgs = {
  input: UpdateTemplateVersionInput;
};


export type MutationUpdateUserArgs = {
  input: UpdateUserInput;
};


export type MutationUpdateWorkspaceArgs = {
  input: UpdateWorkspaceInput;
};


export type MutationUpdateWorkspaceMemberArgs = {
  input: UpdateWorkspaceMemberInput;
};


export type MutationUpgradePipelineVersionFromTemplateArgs = {
  input: UpgradePipelineVersionFromTemplateInput;
};


export type MutationUploadPipelineArgs = {
  input: UploadPipelineInput;
};


export type MutationVerifyDeviceArgs = {
  input: VerifyDeviceInput;
};

export type NotebookServer = {
  __typename?: 'NotebookServer';
  name: Scalars['String']['output'];
  ready: Scalars['Boolean']['output'];
  url: Scalars['String']['output'];
};

/** The direction in which to order a list of items. */
export enum OrderByDirection {
  Asc = 'ASC',
  Desc = 'DESC'
}

/** The Organization type represents an organization in the system. */
export type Organization = {
  __typename?: 'Organization';
  /** The contact information of the organization. */
  contactInfo: Scalars['String']['output'];
  /** The unique identifier of the organization. */
  id: Scalars['UUID']['output'];
  /** The name of the organization. */
  name: Scalars['String']['output'];
  /** The type of the organization. */
  type: Scalars['String']['output'];
  /** The URL of the organization. */
  url: Scalars['String']['output'];
};

/** The OrganizationInput type represents the input for creating or updating an organization. */
export type OrganizationInput = {
  /** The updated contact information of the organization. */
  contactInfo?: InputMaybe<Scalars['String']['input']>;
  /** The unique identifier of the organization. */
  id: Scalars['UUID']['input'];
  /** The updated name of the organization. */
  name?: InputMaybe<Scalars['String']['input']>;
  /** The updated type of the organization. */
  type?: InputMaybe<Scalars['String']['input']>;
  /** The updated URL of the organization. */
  url?: InputMaybe<Scalars['String']['input']>;
};

/** Represents an input parameter of a pipeline. */
export type ParameterInput = {
  choices?: InputMaybe<Array<Scalars['Generic']['input']>>;
  code: Scalars['String']['input'];
  default?: InputMaybe<Scalars['Generic']['input']>;
  help?: InputMaybe<Scalars['String']['input']>;
  multiple?: InputMaybe<Scalars['Boolean']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  required?: InputMaybe<Scalars['Boolean']['input']>;
  type: Scalars['String']['input'];
};

/** Enum representing the type of a parameter. */
export enum ParameterType {
  Bool = 'bool',
  Custom = 'custom',
  Dataset = 'dataset',
  Dhis2 = 'dhis2',
  Float = 'float',
  Gcs = 'gcs',
  Iaso = 'iaso',
  Int = 'int',
  Postgresql = 'postgresql',
  S3 = 's3',
  Str = 'str'
}

/** The PermissionMode enum represents the mode of permissions for a team. */
export enum PermissionMode {
  /** Indicates that the user is an editor of the team. */
  Editor = 'EDITOR',
  /** Indicates that the user is the owner of the team. */
  Owner = 'OWNER',
  /** Indicates that the user is a viewer of the team. */
  Viewer = 'VIEWER'
}

/** Errors that can occur when pinning or unpinning a dataset for a workspace. */
export enum PinDatasetError {
  LinkNotFound = 'LINK_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Input for pinning or unpinning a dataset for a workspace. */
export type PinDatasetInput = {
  linkId: Scalars['ID']['input'];
  pinned: Scalars['Boolean']['input'];
};

/** Result of pinning or unpinning a dataset for a workspace. */
export type PinDatasetResult = {
  __typename?: 'PinDatasetResult';
  errors: Array<PinDatasetError>;
  link?: Maybe<DatasetLink>;
  success: Scalars['Boolean']['output'];
};

/** Represents a pipeline. */
export type Pipeline = {
  __typename?: 'Pipeline';
  code: Scalars['String']['output'];
  config: Scalars['JSON']['output'];
  createdAt: Scalars['DateTime']['output'];
  currentVersion?: Maybe<PipelineVersion>;
  description?: Maybe<Scalars['String']['output']>;
  hasNewTemplateVersions: Scalars['Boolean']['output'];
  id: Scalars['UUID']['output'];
  name?: Maybe<Scalars['String']['output']>;
  newTemplateVersions?: Maybe<Array<PipelineTemplateVersion>>;
  notebookPath?: Maybe<Scalars['String']['output']>;
  permissions: PipelinePermissions;
  recipients: Array<PipelineRecipient>;
  runs: PipelineRunPage;
  schedule?: Maybe<Scalars['String']['output']>;
  sourceTemplate?: Maybe<PipelineTemplate>;
  template?: Maybe<PipelineTemplate>;
  type: PipelineType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  versions: PipelineVersionPage;
  webhookEnabled: Scalars['Boolean']['output'];
  webhookUrl?: Maybe<Scalars['String']['output']>;
  workspace: Workspace;
};


/** Represents a pipeline. */
export type PipelineRunsArgs = {
  orderBy?: InputMaybe<PipelineRunOrderBy>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


/** Represents a pipeline. */
export type PipelineVersionsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export enum PipelineError {
  CannotUpdateNotebookPipeline = 'CANNOT_UPDATE_NOTEBOOK_PIPELINE',
  DuplicatePipelineVersionName = 'DUPLICATE_PIPELINE_VERSION_NAME',
  FileNotFound = 'FILE_NOT_FOUND',
  InvalidConfig = 'INVALID_CONFIG',
  InvalidTimeoutValue = 'INVALID_TIMEOUT_VALUE',
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineAlreadyCompleted = 'PIPELINE_ALREADY_COMPLETED',
  PipelineAlreadyExists = 'PIPELINE_ALREADY_EXISTS',
  PipelineAlreadyStopped = 'PIPELINE_ALREADY_STOPPED',
  PipelineDoesNotSupportParameters = 'PIPELINE_DOES_NOT_SUPPORT_PARAMETERS',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineVersionNotFound = 'PIPELINE_VERSION_NOT_FOUND',
  TableNotFound = 'TABLE_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the notification level for a pipeline recipient. */
export enum PipelineNotificationLevel {
  All = 'ALL',
  Error = 'ERROR'
}

/** Represents a parameter of a pipeline. */
export type PipelineParameter = {
  __typename?: 'PipelineParameter';
  choices?: Maybe<Array<Scalars['Generic']['output']>>;
  code: Scalars['String']['output'];
  default?: Maybe<Scalars['Generic']['output']>;
  help?: Maybe<Scalars['String']['output']>;
  multiple: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  required: Scalars['Boolean']['output'];
  type: ParameterType;
};

/** Represents the permissions for a pipeline. */
export type PipelinePermissions = {
  __typename?: 'PipelinePermissions';
  createTemplateVersion: Scalars['Boolean']['output'];
  createVersion: Scalars['Boolean']['output'];
  delete: Scalars['Boolean']['output'];
  run: Scalars['Boolean']['output'];
  schedule: Scalars['Boolean']['output'];
  stopPipeline: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

/** Represents a recipient of a pipeline. */
export type PipelineRecipient = {
  __typename?: 'PipelineRecipient';
  id: Scalars['UUID']['output'];
  notificationLevel: PipelineNotificationLevel;
  pipeline: Pipeline;
  user: User;
};

export enum PipelineRecipientError {
  AlreadyExists = 'ALREADY_EXISTS',
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  RecipientNotFound = 'RECIPIENT_NOT_FOUND',
  UserNotFound = 'USER_NOT_FOUND'
}

/** Represents a pipeline run. */
export type PipelineRun = {
  __typename?: 'PipelineRun';
  code: Scalars['String']['output'];
  config: Scalars['JSON']['output'];
  datasetVersions: Array<DatasetVersion>;
  duration?: Maybe<Scalars['Int']['output']>;
  enableDebugLogs: Scalars['Boolean']['output'];
  executionDate?: Maybe<Scalars['DateTime']['output']>;
  id: Scalars['UUID']['output'];
  logs?: Maybe<Scalars['String']['output']>;
  messages: Array<PipelineRunMessage>;
  outputs: Array<PipelineRunOutput>;
  pipeline: Pipeline;
  progress: Scalars['Int']['output'];
  run_id: Scalars['UUID']['output'];
  sendMailNotifications: Scalars['Boolean']['output'];
  status: PipelineRunStatus;
  stoppedBy?: Maybe<User>;
  timeout?: Maybe<Scalars['Int']['output']>;
  triggerMode?: Maybe<PipelineRunTrigger>;
  user?: Maybe<User>;
  version?: Maybe<PipelineVersion>;
};

/** Represents a message associated with a pipeline run. */
export type PipelineRunMessage = {
  __typename?: 'PipelineRunMessage';
  message: Scalars['String']['output'];
  priority: MessagePriority;
  timestamp?: Maybe<Scalars['DateTime']['output']>;
};

/** Enum representing the possible orderings for pipeline runs. */
export enum PipelineRunOrderBy {
  ExecutionDateAsc = 'EXECUTION_DATE_ASC',
  ExecutionDateDesc = 'EXECUTION_DATE_DESC'
}

/** Represents an output of a pipeline run, which can be either a BucketObject, GenericOutput, or DatabaseTable. */
export type PipelineRunOutput = BucketObject | DatabaseTable | GenericOutput;

/** Represents a page of pipeline runs. */
export type PipelineRunPage = {
  __typename?: 'PipelineRunPage';
  items: Array<PipelineRun>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Enum representing the status of a pipeline run. */
export enum PipelineRunStatus {
  Failed = 'failed',
  Queued = 'queued',
  Running = 'running',
  Stopped = 'stopped',
  Success = 'success',
  Terminating = 'terminating'
}

export enum PipelineRunTrigger {
  Manual = 'manual',
  Scheduled = 'scheduled',
  Webhook = 'webhook'
}

/** Represents a pipeline template. */
export type PipelineTemplate = {
  __typename?: 'PipelineTemplate';
  code: Scalars['String']['output'];
  config?: Maybe<Scalars['String']['output']>;
  currentVersion?: Maybe<PipelineTemplateVersion>;
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
  permissions: PipelineTemplatePermissions;
  sourcePipeline?: Maybe<Pipeline>;
  versions: TemplateVersionPage;
};


/** Represents a pipeline template. */
export type PipelineTemplateVersionsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export enum PipelineTemplateError {
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineTemplateNotFound = 'PIPELINE_TEMPLATE_NOT_FOUND'
}

/** Represents paged result of fetching pipeline templates. */
export type PipelineTemplatePage = {
  __typename?: 'PipelineTemplatePage';
  items: Array<PipelineTemplate>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the permissions for a pipeline template. */
export type PipelineTemplatePermissions = {
  __typename?: 'PipelineTemplatePermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

/** Represents a version of a pipeline template. */
export type PipelineTemplateVersion = {
  __typename?: 'PipelineTemplateVersion';
  changelog?: Maybe<Scalars['String']['output']>;
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  isLatestVersion: Scalars['Boolean']['output'];
  permissions: PipelineTemplateVersionPermissions;
  template: PipelineTemplate;
  user?: Maybe<User>;
  versionNumber: Scalars['Int']['output'];
};

/** Represents the permissions for a pipeline template version. */
export type PipelineTemplateVersionPermissions = {
  __typename?: 'PipelineTemplateVersionPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

/** Represents the input for retrieving a pipeline token. */
export type PipelineTokenInput = {
  pipelineCode: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of retrieving a pipeline token. */
export type PipelineTokenResult = {
  __typename?: 'PipelineTokenResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
  token?: Maybe<Scalars['String']['output']>;
};

/** Represents the type of a pipeline. */
export enum PipelineType {
  Notebook = 'notebook',
  ZipFile = 'zipFile'
}

/** Represents a version of a pipeline. */
export type PipelineVersion = {
  __typename?: 'PipelineVersion';
  config?: Maybe<Scalars['JSON']['output']>;
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  externalLink?: Maybe<Scalars['URL']['output']>;
  id: Scalars['UUID']['output'];
  isLatestVersion: Scalars['Boolean']['output'];
  name?: Maybe<Scalars['String']['output']>;
  /** @deprecated Use 'versionNumber' instead */
  number?: Maybe<Scalars['Int']['output']>;
  parameters: Array<PipelineParameter>;
  permissions: PipelineVersionPermissions;
  pipeline: Pipeline;
  templateVersion?: Maybe<PipelineTemplateVersion>;
  timeout?: Maybe<Scalars['Int']['output']>;
  user?: Maybe<User>;
  versionName: Scalars['String']['output'];
  versionNumber: Scalars['Int']['output'];
  zipfile: Scalars['String']['output'];
};

/** Represents a page of pipeline versions. */
export type PipelineVersionPage = {
  __typename?: 'PipelineVersionPage';
  items: Array<PipelineVersion>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the permissions for a pipeline version. */
export type PipelineVersionPermissions = {
  __typename?: 'PipelineVersionPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

/** Represents a page of pipelines. */
export type PipelinesPage = {
  __typename?: 'PipelinesPage';
  items: Array<Pipeline>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** PostgreSQL connection object */
export type PostgreSqlConnection = Connection & {
  __typename?: 'PostgreSQLConnection';
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};

export type PrepareAccessmodFileDownloadInput = {
  fileId: Scalars['String']['input'];
};

export type PrepareAccessmodFileDownloadResult = {
  __typename?: 'PrepareAccessmodFileDownloadResult';
  downloadUrl?: Maybe<Scalars['String']['output']>;
  success: Scalars['Boolean']['output'];
};

export type PrepareAccessmodFileUploadInput = {
  filesetId: Scalars['String']['input'];
  mimeType: Scalars['String']['input'];
};

export type PrepareAccessmodFileUploadResult = {
  __typename?: 'PrepareAccessmodFileUploadResult';
  fileUri?: Maybe<Scalars['String']['output']>;
  success: Scalars['Boolean']['output'];
  uploadUrl?: Maybe<Scalars['String']['output']>;
};

export type PrepareAccessmodFilesetVisualizationDownloadInput = {
  id: Scalars['String']['input'];
};

export type PrepareAccessmodFilesetVisualizationDownloadResult = {
  __typename?: 'PrepareAccessmodFilesetVisualizationDownloadResult';
  success: Scalars['Boolean']['output'];
  url?: Maybe<Scalars['String']['output']>;
};

export type PrepareDownloadUrlInput = {
  uri: Scalars['URL']['input'];
};

export type PrepareDownloadUrlResult = {
  __typename?: 'PrepareDownloadURLResult';
  success: Scalars['Boolean']['output'];
  url?: Maybe<Scalars['URL']['output']>;
};

/** Errors that can occur when preparing to download an object from a workspace's bucket. */
export enum PrepareObjectDownloadError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type PrepareObjectDownloadInput = {
  objectKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** The result of preparing to download an object from a workspace's bucket. */
export type PrepareObjectDownloadResult = {
  __typename?: 'PrepareObjectDownloadResult';
  downloadUrl?: Maybe<Scalars['URL']['output']>;
  errors: Array<PrepareObjectDownloadError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when preparing to upload an object to a workspace's bucket. */
export enum PrepareObjectUploadError {
  PermissionDenied = 'PERMISSION_DENIED'
}

/**
 * Input for preparing to upload an object to a workspace's bucket.
 * The `contentType`
 */
export type PrepareObjectUploadInput = {
  contentType?: InputMaybe<Scalars['String']['input']>;
  objectKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/**
 * The result of preparing to upload an object to a workspace's bucket. It contains
 * a URL that can be used to upload the object using a PUT request.
 */
export type PrepareObjectUploadResult = {
  __typename?: 'PrepareObjectUploadResult';
  errors: Array<PrepareObjectUploadError>;
  success: Scalars['Boolean']['output'];
  /** Url to upload the object to. The contentType passed with the PUT request should match the one passed in the input. */
  uploadUrl?: Maybe<Scalars['URL']['output']>;
};

/** Errors that can occur when preparing a dataset version file download. */
export enum PrepareVersionFileDownloadError {
  FileNotFound = 'FILE_NOT_FOUND',
  FileNotUploaded = 'FILE_NOT_UPLOADED',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for preparing a dataset version file download. */
export type PrepareVersionFileDownloadInput = {
  fileId: Scalars['ID']['input'];
};

/** Result of preparing a dataset version file download. */
export type PrepareVersionFileDownloadResult = {
  __typename?: 'PrepareVersionFileDownloadResult';
  downloadUrl?: Maybe<Scalars['String']['output']>;
  errors: Array<PrepareVersionFileDownloadError>;
  success: Scalars['Boolean']['output'];
};

export type Query = {
  __typename?: 'Query';
  accessmodAccessRequests: AccessmodAccessRequestPage;
  accessmodAnalyses: AccessmodAnalysisPage;
  accessmodAnalysis?: Maybe<AccessmodAnalysis>;
  accessmodFileset?: Maybe<AccessmodFileset>;
  accessmodFilesetRole?: Maybe<AccessmodFilesetRole>;
  accessmodFilesetRoles: Array<AccessmodFilesetRole>;
  accessmodFilesets: AccessmodFilesetPage;
  accessmodProject?: Maybe<AccessmodProject>;
  accessmodProjects: AccessmodProjectPage;
  boundaries: Array<WhoBoundary>;
  /** Retrieves the configuration of the system. */
  config: Config;
  connection?: Maybe<Connection>;
  connectionBySlug?: Maybe<Connection>;
  countries: Array<Country>;
  country?: Maybe<Country>;
  dag?: Maybe<Dag>;
  dagRun?: Maybe<DagRun>;
  dags: DagPage;
  databaseTable?: Maybe<DatabaseTable>;
  /** Get a dataset by its ID. */
  dataset?: Maybe<Dataset>;
  /** Get a dataset link by its id. */
  datasetLink?: Maybe<DatasetLink>;
  /** Get a dataset link by its slug. */
  datasetLinkBySlug?: Maybe<DatasetLink>;
  /** Get a dataset by its slug. */
  datasetVersion?: Maybe<DatasetVersion>;
  /** Get a dataset file by its id  */
  datasetVersionFile?: Maybe<DatasetVersionFile>;
  /** Search datasets. */
  datasets: DatasetPage;
  /** Retrieves the currently authenticated user. */
  me: Me;
  metadataAttributes: Array<Maybe<MetadataAttribute>>;
  notebooksUrl: Scalars['URL']['output'];
  /** Retrieves a list of organizations. */
  organizations: Array<Organization>;
  pendingWorkspaceInvitations: WorkspaceInvitationPage;
  /** Retrieves a pipeline by ID. */
  pipeline?: Maybe<Pipeline>;
  /** Retrieves a pipeline by workspace slug and code. */
  pipelineByCode?: Maybe<Pipeline>;
  /** Retrieves a pipeline run by ID. */
  pipelineRun?: Maybe<PipelineRun>;
  pipelineTemplates: PipelineTemplatePage;
  /** Retrieves a pipeline version by ID. */
  pipelineVersion?: Maybe<PipelineVersion>;
  /** Retrieves a page of pipelines. */
  pipelines: PipelinesPage;
  team?: Maybe<Team>;
  teams: TeamPage;
  /** Retrieves a template by code. */
  templateByCode?: Maybe<PipelineTemplate>;
  workspace?: Maybe<Workspace>;
  workspaces: WorkspacePage;
};


export type QueryAccessmodAccessRequestsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryAccessmodAnalysesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  projectId: Scalars['String']['input'];
};


export type QueryAccessmodAnalysisArgs = {
  id?: InputMaybe<Scalars['String']['input']>;
};


export type QueryAccessmodFilesetArgs = {
  id?: InputMaybe<Scalars['String']['input']>;
};


export type QueryAccessmodFilesetRoleArgs = {
  id: Scalars['String']['input'];
};


export type QueryAccessmodFilesetsArgs = {
  mode?: InputMaybe<AccessmodFilesetMode>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  projectId: Scalars['String']['input'];
  roleId?: InputMaybe<Scalars['String']['input']>;
  term?: InputMaybe<Scalars['String']['input']>;
};


export type QueryAccessmodProjectArgs = {
  id?: InputMaybe<Scalars['String']['input']>;
};


export type QueryAccessmodProjectsArgs = {
  countries?: InputMaybe<Array<Scalars['String']['input']>>;
  orderBy?: InputMaybe<AccessmodProjectOrder>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  teams?: InputMaybe<Array<Scalars['String']['input']>>;
  term?: InputMaybe<Scalars['String']['input']>;
};


export type QueryBoundariesArgs = {
  country_code: Scalars['String']['input'];
  level: Scalars['String']['input'];
};


export type QueryConnectionArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryConnectionBySlugArgs = {
  connectionSlug: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};


export type QueryCountryArgs = {
  alpha3?: InputMaybe<Scalars['String']['input']>;
  code?: InputMaybe<Scalars['String']['input']>;
};


export type QueryDagArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryDagRunArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryDagsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryDatabaseTableArgs = {
  id: Scalars['String']['input'];
};


export type QueryDatasetArgs = {
  id: Scalars['ID']['input'];
};


export type QueryDatasetLinkArgs = {
  id: Scalars['ID']['input'];
};


export type QueryDatasetLinkBySlugArgs = {
  datasetSlug: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};


export type QueryDatasetVersionArgs = {
  id: Scalars['ID']['input'];
};


export type QueryDatasetVersionFileArgs = {
  id: Scalars['ID']['input'];
};


export type QueryDatasetsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
};


export type QueryMetadataAttributesArgs = {
  targetId: Scalars['OpaqueID']['input'];
};


export type QueryPendingWorkspaceInvitationsArgs = {
  page?: Scalars['Int']['input'];
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryPipelineArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryPipelineByCodeArgs = {
  code: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};


export type QueryPipelineRunArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryPipelineTemplatesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QueryPipelineVersionArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryPipelinesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QueryTeamArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryTeamsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  term?: InputMaybe<Scalars['String']['input']>;
};


export type QueryTemplateByCodeArgs = {
  code: Scalars['String']['input'];
};


export type QueryWorkspaceArgs = {
  slug: Scalars['String']['input'];
};


export type QueryWorkspacesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
};

/** The RegisterError enum represents the possible errors that can occur during the register mutation. */
export enum RegisterError {
  /** Indicates that the user is already logged in. */
  AlreadyLoggedIn = 'ALREADY_LOGGED_IN',
  /** Indicates that the email address is already taken. */
  EmailTaken = 'EMAIL_TAKEN',
  /** Indicates that the provided password is invalid. */
  InvalidPassword = 'INVALID_PASSWORD',
  /** Indicates that the invitation token is invalid. */
  InvalidToken = 'INVALID_TOKEN',
  /** Indicates that the provided passwords do not match. */
  PasswordMismatch = 'PASSWORD_MISMATCH'
}

/** The RegisterInput type represents the input for the register mutation. */
export type RegisterInput = {
  /** The first name of the user. */
  firstName: Scalars['String']['input'];
  /** The invitation token for registration. */
  invitationToken: Scalars['String']['input'];
  /** The last name of the user. */
  lastName: Scalars['String']['input'];
  /** The first password for registration. */
  password1: Scalars['String']['input'];
  /** The second password for registration (confirmation). */
  password2: Scalars['String']['input'];
};

/** The RegisterResult type represents the result of the register mutation. */
export type RegisterResult = {
  __typename?: 'RegisterResult';
  /** The list of errors that occurred during the registration process. */
  errors?: Maybe<Array<RegisterError>>;
  /** Indicates whether the registration was successful. */
  success: Scalars['Boolean']['output'];
};

export enum RequestAccessmodAccessError {
  AlreadyExists = 'ALREADY_EXISTS',
  Invalid = 'INVALID',
  MustAcceptTos = 'MUST_ACCEPT_TOS'
}

export type RequestAccessmodAccessInput = {
  acceptTos: Scalars['Boolean']['input'];
  email: Scalars['String']['input'];
  firstName: Scalars['String']['input'];
  lastName: Scalars['String']['input'];
};

export type RequestAccessmodAccessInputResult = {
  __typename?: 'RequestAccessmodAccessInputResult';
  errors: Array<RequestAccessmodAccessError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the error types for resending a workspace invitation. */
export enum ResendWorkspaceInvitationError {
  InvitationNotFound = 'INVITATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for resending a workspace invitation. */
export type ResendWorkspaceInvitationInput = {
  invitationId: Scalars['UUID']['input'];
};

/** Represents the result of resending a workspace invitation. */
export type ResendWorkspaceInvitationResult = {
  __typename?: 'ResendWorkspaceInvitationResult';
  errors: Array<ResendWorkspaceInvitationError>;
  success: Scalars['Boolean']['output'];
};

/** The ResetPasswordInput type represents the input for the resetPassword mutation. */
export type ResetPasswordInput = {
  /** The email address of the user. */
  email: Scalars['String']['input'];
};

/** The ResetPasswordResult type represents the result of the resetPassword mutation. */
export type ResetPasswordResult = {
  __typename?: 'ResetPasswordResult';
  /** Indicates whether the password reset was successful. */
  success: Scalars['Boolean']['output'];
};

export enum RunDagError {
  DagNotFound = 'DAG_NOT_FOUND',
  InvalidConfig = 'INVALID_CONFIG'
}

export type RunDagInput = {
  config: Scalars['JSON']['input'];
  dagId: Scalars['UUID']['input'];
};

export type RunDagResult = {
  __typename?: 'RunDAGResult';
  dag?: Maybe<Dag>;
  dagRun?: Maybe<DagRun>;
  errors: Array<RunDagError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for running a pipeline. */
export type RunPipelineInput = {
  config: Scalars['JSON']['input'];
  enableDebugLogs?: InputMaybe<Scalars['Boolean']['input']>;
  id: Scalars['UUID']['input'];
  sendMailNotifications?: InputMaybe<Scalars['Boolean']['input']>;
  versionId?: InputMaybe<Scalars['UUID']['input']>;
};

/** Represents the result of running a pipeline. */
export type RunPipelineResult = {
  __typename?: 'RunPipelineResult';
  errors: Array<PipelineError>;
  run?: Maybe<PipelineRun>;
  success: Scalars['Boolean']['output'];
};

export type S3Bucket = {
  __typename?: 'S3Bucket';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  updatedAt: Scalars['DateTime']['output'];
};

/** S3 connection object */
export type S3Connection = Connection & {
  __typename?: 'S3Connection';
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  fields: Array<ConnectionField>;
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  permissions: ConnectionPermissions;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};

export type S3Object = {
  __typename?: 'S3Object';
  bucket: S3Bucket;
  createdAt: Scalars['DateTime']['output'];
  etag: Scalars['String']['output'];
  filename: Scalars['String']['output'];
  id: Scalars['String']['output'];
  key: Scalars['String']['output'];
  lastModified: Scalars['DateTime']['output'];
  parentKey: Scalars['String']['output'];
  size: Scalars['Int']['output'];
  storageClass: Scalars['String']['output'];
  type: Scalars['String']['output'];
  updatedAt: Scalars['DateTime']['output'];
};

export type S3ObjectPage = {
  __typename?: 'S3ObjectPage';
  items: Array<S3Object>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export enum SetDagRunFavoriteError {
  Invalid = 'INVALID',
  MissingLabel = 'MISSING_LABEL',
  NotFound = 'NOT_FOUND'
}

export type SetDagRunFavoriteInput = {
  id: Scalars['UUID']['input'];
  isFavorite: Scalars['Boolean']['input'];
  label?: InputMaybe<Scalars['String']['input']>;
};

export type SetDagRunFavoriteResult = {
  __typename?: 'SetDAGRunFavoriteResult';
  dagRun?: Maybe<DagRun>;
  errors: Array<SetDagRunFavoriteError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when setting an attribute. */
export enum SetMetadataAttributeError {
  PermissionDenied = 'PERMISSION_DENIED',
  TargetNotFound = 'TARGET_NOT_FOUND'
}

/** Input to set a custom attribute, empty field for value is accepted */
export type SetMetadataAttributeInput = {
  key: Scalars['String']['input'];
  label?: InputMaybe<Scalars['String']['input']>;
  targetId: Scalars['OpaqueID']['input'];
  value?: InputMaybe<Scalars['JSON']['input']>;
};

export type SetMetadataAttributeResult = {
  __typename?: 'SetMetadataAttributeResult';
  attribute?: Maybe<MetadataAttribute>;
  errors: Array<SetMetadataAttributeError>;
  success: Scalars['Boolean']['output'];
};

/** The SetPasswordError enum represents the possible errors that can occur during the setPassword mutation. */
export enum SetPasswordError {
  /** Indicates that the provided password is invalid. */
  InvalidPassword = 'INVALID_PASSWORD',
  /** Indicates that the provided token is invalid. */
  InvalidToken = 'INVALID_TOKEN',
  /** Indicates that the provided passwords do not match. */
  PasswordMismatch = 'PASSWORD_MISMATCH',
  /** Indicates that the user was not found. */
  UserNotFound = 'USER_NOT_FOUND'
}

/** The SetPasswordInput type represents the input for the setPassword mutation. */
export type SetPasswordInput = {
  /** The new password. */
  password1: Scalars['String']['input'];
  /** The confirmation of the new password. */
  password2: Scalars['String']['input'];
  /** The token for password reset. */
  token: Scalars['String']['input'];
  /** The base64-encoded user ID. */
  uidb64: Scalars['String']['input'];
};

/** The SetPasswordResult type represents the result of the setPassword mutation. */
export type SetPasswordResult = {
  __typename?: 'SetPasswordResult';
  /** The error that occurred during the setPassword mutation. */
  error?: Maybe<SetPasswordError>;
  /** Indicates whether the password was set successfully. */
  success: Scalars['Boolean']['output'];
};

/** Represents the input for stopping a pipeline. */
export type StopPipelineInput = {
  runId: Scalars['UUID']['input'];
};

/** Represents the result of stopping a pipeline. */
export type StopPipelineResult = {
  __typename?: 'StopPipelineResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

export type TableColumn = {
  __typename?: 'TableColumn';
  name: Scalars['String']['output'];
  type: Scalars['String']['output'];
};

/** Represents a paginated list of rows from a database table. */
export type TableRowsPage = {
  __typename?: 'TableRowsPage';
  /** Indicates if there is a next page available. */
  hasNextPage: Scalars['Boolean']['output'];
  /** Indicates if there is a previous page available. */
  hasPreviousPage: Scalars['Boolean']['output'];
  /** The rows in the current page. */
  items: Array<Scalars['JSON']['output']>;
  /** The page number of the result. */
  pageNumber: Scalars['Int']['output'];
};

/** A tag is a label. */
export type Tag = {
  __typename?: 'Tag';
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

/** The Team type represents a team in the system. */
export type Team = {
  __typename?: 'Team';
  /** The date when the team was created. */
  createdAt: Scalars['DateTime']['output'];
  /** The unique identifier of the team. */
  id: Scalars['UUID']['output'];
  /** Retrieves the memberships of the team. */
  memberships: MembershipPage;
  /** The name of the team. */
  name: Scalars['String']['output'];
  /** The permissions assigned to the team. */
  permissions: TeamPermissions;
  /** The date when the team was last updated. */
  updatedAt: Scalars['DateTime']['output'];
};


/** The Team type represents a team in the system. */
export type TeamMembershipsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

/** The TeamPage type represents a paginated list of teams. */
export type TeamPage = {
  __typename?: 'TeamPage';
  /** The list of teams on the current page. */
  items: Array<Team>;
  /** The current page number. */
  pageNumber: Scalars['Int']['output'];
  /** The total number of items. */
  totalItems: Scalars['Int']['output'];
  /** The total number of pages. */
  totalPages: Scalars['Int']['output'];
};

/** The TeamPermissions type represents the permissions of a team. */
export type TeamPermissions = {
  __typename?: 'TeamPermissions';
  /** Indicates whether the user has permission to create a membership in the team. */
  createMembership: Scalars['Boolean']['output'];
  /** Indicates whether the user has permission to delete the team. */
  delete: Scalars['Boolean']['output'];
  /** Indicates whether the user has permission to update the team. */
  update: Scalars['Boolean']['output'];
};

/** Represents a page of template versions. */
export type TemplateVersionPage = {
  __typename?: 'TemplateVersionPage';
  items: Array<PipelineTemplateVersion>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export enum UpdateAccessmodAccessibilityAnalysisError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND'
}

export type UpdateAccessmodAccessibilityAnalysisInput = {
  algorithm?: InputMaybe<AccessmodAccessibilityAnalysisAlgorithm>;
  barrierId?: InputMaybe<Scalars['String']['input']>;
  demId?: InputMaybe<Scalars['String']['input']>;
  healthFacilitiesId?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['String']['input'];
  invertDirection?: InputMaybe<Scalars['Boolean']['input']>;
  knightMove?: InputMaybe<Scalars['Boolean']['input']>;
  landCoverId?: InputMaybe<Scalars['String']['input']>;
  maxTravelTime?: InputMaybe<Scalars['Int']['input']>;
  movingSpeeds?: InputMaybe<Scalars['MovingSpeeds']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  stackId?: InputMaybe<Scalars['String']['input']>;
  stackPriorities?: InputMaybe<Scalars['StackPriorities']['input']>;
  transportNetworkId?: InputMaybe<Scalars['String']['input']>;
  waterAllTouched?: InputMaybe<Scalars['Boolean']['input']>;
  waterId?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateAccessmodAccessibilityAnalysisResult = {
  __typename?: 'UpdateAccessmodAccessibilityAnalysisResult';
  analysis?: Maybe<AccessmodAccessibilityAnalysis>;
  errors: Array<UpdateAccessmodAccessibilityAnalysisError>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateAccessmodFilesetError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodFilesetInput = {
  id: Scalars['String']['input'];
  metadata?: InputMaybe<Scalars['AccessmodFilesetMetadata']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateAccessmodFilesetResult = {
  __typename?: 'UpdateAccessmodFilesetResult';
  errors: Array<UpdateAccessmodFilesetError>;
  fileset?: Maybe<AccessmodFileset>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateAccessmodProjectError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodProjectInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['String']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
};

export enum UpdateAccessmodProjectMemberError {
  NotFound = 'NOT_FOUND',
  NotImplemented = 'NOT_IMPLEMENTED',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodProjectMemberInput = {
  id: Scalars['String']['input'];
  mode: PermissionMode;
};

export type UpdateAccessmodProjectMemberResult = {
  __typename?: 'UpdateAccessmodProjectMemberResult';
  errors: Array<UpdateAccessmodProjectMemberError>;
  member?: Maybe<AccessmodProjectMember>;
  success: Scalars['Boolean']['output'];
};

export type UpdateAccessmodProjectResult = {
  __typename?: 'UpdateAccessmodProjectResult';
  errors: Array<UpdateAccessmodProjectError>;
  project?: Maybe<AccessmodProject>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateAccessmodZonalStatisticsError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND'
}

export type UpdateAccessmodZonalStatisticsInput = {
  boundariesId?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['String']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  populationId?: InputMaybe<Scalars['String']['input']>;
  timeThresholds?: InputMaybe<Scalars['TimeThresholds']['input']>;
  travelTimesId?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateAccessmodZonalStatisticsResult = {
  __typename?: 'UpdateAccessmodZonalStatisticsResult';
  analysis?: Maybe<AccessmodZonalStatistics>;
  errors: Array<UpdateAccessmodZonalStatisticsError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the error types for updating a connection. */
export enum UpdateConnectionError {
  InvalidSlug = 'INVALID_SLUG',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a connection. */
export type UpdateConnectionInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  fields?: InputMaybe<Array<ConnectionFieldInput>>;
  id: Scalars['String']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
};

/** Represents the result of updating a connection. */
export type UpdateConnectionResult = {
  __typename?: 'UpdateConnectionResult';
  connection?: Maybe<Connection>;
  errors: Array<UpdateConnectionError>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateDagError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type UpdateDagInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  label?: InputMaybe<Scalars['String']['input']>;
  schedule?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateDagResult = {
  __typename?: 'UpdateDAGResult';
  dag?: Maybe<Dag>;
  errors: Array<UpdateDagError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when updating a dataset. */
export enum UpdateDatasetError {
  DatasetNotFound = 'DATASET_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Input for updating a dataset. */
export type UpdateDatasetInput = {
  datasetId: Scalars['ID']['input'];
  description?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

/** Result of updating a dataset. */
export type UpdateDatasetResult = {
  __typename?: 'UpdateDatasetResult';
  dataset?: Maybe<Dataset>;
  errors: Array<UpdateDatasetError>;
  success: Scalars['Boolean']['output'];
};

/** Errors that can occur when updating a dataset version. */
export enum UpdateDatasetVersionError {
  PermissionDenied = 'PERMISSION_DENIED',
  VersionNotFound = 'VERSION_NOT_FOUND'
}

/** Input for updating a dataset version. */
export type UpdateDatasetVersionInput = {
  changelog?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  versionId: Scalars['ID']['input'];
};

/** Result of updating a dataset version. */
export type UpdateDatasetVersionResult = {
  __typename?: 'UpdateDatasetVersionResult';
  errors: Array<UpdateDatasetVersionError>;
  success: Scalars['Boolean']['output'];
  version?: Maybe<DatasetVersion>;
};

/** The UpdateMembershipError enum represents the possible errors that can occur during the updateMembership mutation. */
export enum UpdateMembershipError {
  /** Indicates that the provided role is invalid. */
  InvalidRole = 'INVALID_ROLE',
  /** Indicates that the membership was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to update the membership. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The UpdateMembershipInput type represents the input for the updateMembership mutation. */
export type UpdateMembershipInput = {
  /** The unique identifier of the membership to update. */
  id: Scalars['UUID']['input'];
  /** The updated role of the user in the team. */
  role: MembershipRole;
};

/** The UpdateMembershipResult type represents the result of the updateMembership mutation. */
export type UpdateMembershipResult = {
  __typename?: 'UpdateMembershipResult';
  /** The list of errors that occurred during the updateMembership mutation. */
  errors: Array<UpdateMembershipError>;
  /** The updated membership object. */
  membership?: Maybe<Membership>;
  /** Indicates whether the updateMembership mutation was successful. */
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when updating a pipeline. */
export enum UpdatePipelineError {
  InvalidConfig = 'INVALID_CONFIG',
  MissingVersionConfig = 'MISSING_VERSION_CONFIG',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a pipeline. */
export type UpdatePipelineInput = {
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  schedule?: InputMaybe<Scalars['String']['input']>;
  webhookEnabled?: InputMaybe<Scalars['Boolean']['input']>;
};

/** Represents the input for updating the progress of a pipeline. */
export type UpdatePipelineProgressInput = {
  percent: Scalars['Int']['input'];
};

/** Represents the result of updating the progress of a pipeline. */
export type UpdatePipelineProgressResult = {
  __typename?: 'UpdatePipelineProgressResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for updating a recipient. */
export type UpdatePipelineRecipientInput = {
  notificationLevel: PipelineNotificationLevel;
  recipientId: Scalars['UUID']['input'];
};

export type UpdatePipelineRecipientResult = {
  __typename?: 'UpdatePipelineRecipientResult';
  errors: Array<PipelineRecipientError>;
  recipient?: Maybe<PipelineRecipient>;
  success: Scalars['Boolean']['output'];
};

/** Represents the result of updating a pipeline. */
export type UpdatePipelineResult = {
  __typename?: 'UpdatePipelineResult';
  errors: Array<UpdatePipelineError>;
  pipeline?: Maybe<Pipeline>;
  success: Scalars['Boolean']['output'];
};

/** Enum representing the possible errors that can occur when updating a pipeline version. */
export enum UpdatePipelineVersionError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a pipeline version. */
export type UpdatePipelineVersionInput = {
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  externalLink?: InputMaybe<Scalars['URL']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
};

/** Represents the result of updating a pipeline version. */
export type UpdatePipelineVersionResult = {
  __typename?: 'UpdatePipelineVersionResult';
  errors: Array<UpdatePipelineVersionError>;
  pipelineVersion?: Maybe<PipelineVersion>;
  success: Scalars['Boolean']['output'];
};

/** The UpdateTeamError enum represents the possible errors that can occur during the updateTeam mutation. */
export enum UpdateTeamError {
  /** Indicates that a team with the same name already exists. */
  NameDuplicate = 'NAME_DUPLICATE',
  /** Indicates that the team was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to update the team. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The UpdateTeamInput type represents the input for the updateTeam mutation. */
export type UpdateTeamInput = {
  /** The unique identifier of the team to update. */
  id: Scalars['UUID']['input'];
  /** The updated name of the team. */
  name?: InputMaybe<Scalars['String']['input']>;
};

/** The UpdateTeamResult type represents the result of the updateTeam mutation. */
export type UpdateTeamResult = {
  __typename?: 'UpdateTeamResult';
  /** The list of errors that occurred during the updateTeam mutation. */
  errors: Array<UpdateTeamError>;
  /** Indicates whether the updateTeam mutation was successful. */
  success: Scalars['Boolean']['output'];
  /** The updated team object. */
  team?: Maybe<Team>;
};

/** Enum representing the possible errors that can occur when updating a template. */
export enum UpdateTemplateError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a template. */
export type UpdateTemplateInput = {
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
};

/** Represents the result of updating a template. */
export type UpdateTemplateResult = {
  __typename?: 'UpdateTemplateResult';
  errors: Array<UpdateTemplateError>;
  success: Scalars['Boolean']['output'];
  template?: Maybe<PipelineTemplate>;
};

/** Enum representing the possible errors that can occur when updating a template version. */
export enum UpdateTemplateVersionError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a template version. */
export type UpdateTemplateVersionInput = {
  changelog?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
};

/** Represents the result of updating a template version. */
export type UpdateTemplateVersionResult = {
  __typename?: 'UpdateTemplateVersionResult';
  errors: Array<UpdateTemplateVersionError>;
  success: Scalars['Boolean']['output'];
  templateVersion?: Maybe<PipelineTemplateVersion>;
};

/** The UpdateUserError enum represents the possible errors that can occur during the updateUser mutation. */
export enum UpdateUserError {
  /** Indicates that the provided language is invalid. */
  InvalidLanguage = 'INVALID_LANGUAGE',
  /** Indicates that the user does not have permission to update their profile. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The UpdateUserInput type represents the input for the updateUser mutation. */
export type UpdateUserInput = {
  /** The updated first name of the user. */
  firstName?: InputMaybe<Scalars['String']['input']>;
  /** The updated language preference of the user. */
  language?: InputMaybe<Scalars['String']['input']>;
  /** The updated last name of the user. */
  lastName?: InputMaybe<Scalars['String']['input']>;
};

/** The UpdateUserResult type represents the result of the updateUser mutation. */
export type UpdateUserResult = {
  __typename?: 'UpdateUserResult';
  /** The list of errors that occurred during the updateUser mutation. */
  errors: Array<UpdateUserError>;
  /** Indicates whether the user update was successful. */
  success: Scalars['Boolean']['output'];
  /** The updated user object. */
  user?: Maybe<User>;
};

/** Enum representing the possible errors that can occur when updating a workspace. */
export enum UpdateWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a workspace. */
export type UpdateWorkspaceInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  dockerImage?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  slug: Scalars['String']['input'];
};

/** Enum representing the possible errors that can occur when updating a workspace member. */
export enum UpdateWorkspaceMemberError {
  MembershipNotFound = 'MEMBERSHIP_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a workspace member. */
export type UpdateWorkspaceMemberInput = {
  membershipId: Scalars['UUID']['input'];
  role: WorkspaceMembershipRole;
};

/** Represents the result of updating a workspace member. */
export type UpdateWorkspaceMemberResult = {
  __typename?: 'UpdateWorkspaceMemberResult';
  errors: Array<UpdateWorkspaceMemberError>;
  success: Scalars['Boolean']['output'];
  workspaceMembership?: Maybe<WorkspaceMembership>;
};

/** Represents the result of updating a workspace. */
export type UpdateWorkspaceResult = {
  __typename?: 'UpdateWorkspaceResult';
  errors: Array<UpdateWorkspaceError>;
  success: Scalars['Boolean']['output'];
  workspace?: Maybe<Workspace>;
};

/** Enum representing the possible errors that can occur when upgrading a pipeline version from the latest template version. */
export enum UpgradePipelineVersionFromTemplateError {
  NoNewTemplateVersionAvailable = 'NO_NEW_TEMPLATE_VERSION_AVAILABLE',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineNotFromTemplate = 'PIPELINE_NOT_FROM_TEMPLATE'
}

/** Represents the input for upgrading a pipeline version from the latest template version. */
export type UpgradePipelineVersionFromTemplateInput = {
  pipelineId: Scalars['UUID']['input'];
};

/** Represents the result of upgrading a pipeline version from the latest template version. */
export type UpgradePipelineVersionFromTemplateResult = {
  __typename?: 'UpgradePipelineVersionFromTemplateResult';
  errors: Array<UpgradePipelineVersionFromTemplateError>;
  pipelineVersion?: Maybe<PipelineVersion>;
  success: Scalars['Boolean']['output'];
};

/** Represents the input for uploading a pipeline. */
export type UploadPipelineInput = {
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  externalLink?: InputMaybe<Scalars['URL']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  parameters: Array<ParameterInput>;
  pipelineCode?: InputMaybe<Scalars['String']['input']>;
  timeout?: InputMaybe<Scalars['Int']['input']>;
  workspaceSlug: Scalars['String']['input'];
  zipfile: Scalars['String']['input'];
};

/** Represents the result of uploading a pipeline. */
export type UploadPipelineResult = {
  __typename?: 'UploadPipelineResult';
  errors: Array<PipelineError>;
  pipelineVersion?: Maybe<PipelineVersion>;
  success: Scalars['Boolean']['output'];
};

/** The User type represents a user in the system. */
export type User = {
  __typename?: 'User';
  /** The avatar of the user. */
  avatar: Avatar;
  /** The date when the user joined the system. */
  dateJoined: Scalars['DateTime']['output'];
  /** The display name of the user. */
  displayName: Scalars['String']['output'];
  /** The email address of the user. */
  email: Scalars['String']['output'];
  /** The first name of the user. */
  firstName?: Maybe<Scalars['String']['output']>;
  /** The unique identifier of the user. */
  id: Scalars['UUID']['output'];
  /** The language preference of the user. */
  language: Scalars['String']['output'];
  /** The date of the user's last login. */
  lastLogin?: Maybe<Scalars['DateTime']['output']>;
  /** The last name of the user. */
  lastName?: Maybe<Scalars['String']['output']>;
};

/** The VerifyDeviceError enum represents the possible errors that can occur during the verifyDevice mutation. */
export enum VerifyDeviceError {
  InvalidOtp = 'INVALID_OTP',
  NoDevice = 'NO_DEVICE'
}

/** The VerifyDeviceInput type represents the input for the verifyDevice mutation. */
export type VerifyDeviceInput = {
  token?: InputMaybe<Scalars['String']['input']>;
};

/** The VerifyDeviceResult type represents the result of the verifyDevice mutation. */
export type VerifyDeviceResult = {
  __typename?: 'VerifyDeviceResult';
  errors?: Maybe<Array<VerifyDeviceError>>;
  success: Scalars['Boolean']['output'];
};

export type WhoBoundary = {
  __typename?: 'WHOBoundary';
  administrative_level: Scalars['Int']['output'];
  country: Country;
  extent: Scalars['String']['output'];
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  parent?: Maybe<Scalars['String']['output']>;
};

export type WhoInfo = {
  __typename?: 'WHOInfo';
  defaultCRS: Scalars['Int']['output'];
  region?: Maybe<WhoRegion>;
  simplifiedExtent?: Maybe<Scalars['SimplifiedExtentType']['output']>;
};

export type WhoRegion = {
  __typename?: 'WHORegion';
  code: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

/** Represents a workspace. A workspace is a shared environment where users can collaborate on data projects. */
export type Workspace = {
  __typename?: 'Workspace';
  /** File storage of the workspace represented as a bucket */
  bucket: Bucket;
  connections: Array<Connection>;
  countries: Array<Country>;
  createdAt: Scalars['DateTime']['output'];
  createdBy: User;
  database: Database;
  /** Linked datasets of the workspace */
  datasets: DatasetLinkPage;
  description?: Maybe<Scalars['String']['output']>;
  dockerImage?: Maybe<Scalars['String']['output']>;
  invitations: WorkspaceInvitationPage;
  members: WorkspaceMembershipPage;
  name: Scalars['String']['output'];
  permissions: WorkspacePermissions;
  slug: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


/** Represents a workspace. A workspace is a shared environment where users can collaborate on data projects. */
export type WorkspaceDatasetsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  pinned?: InputMaybe<Scalars['Boolean']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
};


/** Represents a workspace. A workspace is a shared environment where users can collaborate on data projects. */
export type WorkspaceInvitationsArgs = {
  includeAccepted?: InputMaybe<Scalars['Boolean']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


/** Represents a workspace. A workspace is a shared environment where users can collaborate on data projects. */
export type WorkspaceMembersArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

/** Represents an invitation to join a workspace. */
export type WorkspaceInvitation = {
  __typename?: 'WorkspaceInvitation';
  createdAt: Scalars['DateTime']['output'];
  email: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  invitedBy?: Maybe<User>;
  role: WorkspaceMembershipRole;
  status: WorkspaceInvitationStatus;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  workspace: Workspace;
};

/** Represents a page of workspace invitations. */
export type WorkspaceInvitationPage = {
  __typename?: 'WorkspaceInvitationPage';
  items: Array<WorkspaceInvitation>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the status of a workspace invitation. */
export enum WorkspaceInvitationStatus {
  Accepted = 'ACCEPTED',
  Declined = 'DECLINED',
  Pending = 'PENDING'
}

/** Represents a membership in a workspace. */
export type WorkspaceMembership = {
  __typename?: 'WorkspaceMembership';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  role: WorkspaceMembershipRole;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user: User;
  workspace: Workspace;
};

/** Represents a page of workspace memberships. */
export type WorkspaceMembershipPage = {
  __typename?: 'WorkspaceMembershipPage';
  items: Array<WorkspaceMembership>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the role of a workspace membership. */
export enum WorkspaceMembershipRole {
  Admin = 'ADMIN',
  Editor = 'EDITOR',
  Viewer = 'VIEWER'
}

/** Represents a page of workspaces. */
export type WorkspacePage = {
  __typename?: 'WorkspacePage';
  items: Array<Workspace>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the permissions of a workspace. */
export type WorkspacePermissions = {
  __typename?: 'WorkspacePermissions';
  createConnection: Scalars['Boolean']['output'];
  /** Permissions to create a dataset in the workspace */
  createDataset: Scalars['Boolean']['output'];
  /** User can create objects in the workspace's bucket. */
  createObject: Scalars['Boolean']['output'];
  createPipeline: Scalars['Boolean']['output'];
  createPipelineTemplateVersion: Scalars['Boolean']['output'];
  delete: Scalars['Boolean']['output'];
  deleteDatabaseTable: Scalars['Boolean']['output'];
  /** User can delete objects in the workspace's bucket. */
  deleteObject: Scalars['Boolean']['output'];
  /** User can download objects from the workspace's bucket. */
  downloadObject: Scalars['Boolean']['output'];
  launchNotebookServer: Scalars['Boolean']['output'];
  manageMembers: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};
