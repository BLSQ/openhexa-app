export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string | number; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  AccessmodFilesetMetadata: { input: any; output: any; }
  Date: { input: any; output: any; }
  DateTime: { input: any; output: any; }
  Generic: { input: any; output: any; }
  JSON: { input: any; output: any; }
  MovingSpeeds: { input: any; output: any; }
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

export type Activity = {
  __typename?: 'Activity';
  description: Scalars['String']['output'];
  occurredAt: Scalars['DateTime']['output'];
  status: ActivityStatus;
  url: Scalars['URL']['output'];
};

export enum ActivityStatus {
  Error = 'ERROR',
  Pending = 'PENDING',
  Running = 'RUNNING',
  Success = 'SUCCESS',
  Unknown = 'UNKNOWN'
}

export type AddPipelineOutputInput = {
  name?: InputMaybe<Scalars['String']['input']>;
  type: Scalars['String']['input'];
  uri: Scalars['String']['input'];
};

export type AddPipelineOutputResult = {
  __typename?: 'AddPipelineOutputResult';
  errors: Array<PipelineError>;
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

export enum ArchiveWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type ArchiveWorkspaceInput = {
  slug: Scalars['String']['input'];
};

export type ArchiveWorkspaceResult = {
  __typename?: 'ArchiveWorkspaceResult';
  errors: Array<ArchiveWorkspaceError>;
  success: Scalars['Boolean']['output'];
};

export type Avatar = {
  __typename?: 'Avatar';
  color: Scalars['String']['output'];
  initials: Scalars['String']['output'];
};

export type Bucket = {
  __typename?: 'Bucket';
  name: Scalars['String']['output'];
  object?: Maybe<BucketObject>;
  objects: BucketObjectPage;
};


export type BucketObjectArgs = {
  key: Scalars['String']['input'];
};


export type BucketObjectsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  prefix?: InputMaybe<Scalars['String']['input']>;
};

export type BucketObject = {
  __typename?: 'BucketObject';
  key: Scalars['String']['output'];
  name: Scalars['String']['output'];
  path: Scalars['String']['output'];
  size?: Maybe<Scalars['Int']['output']>;
  type: BucketObjectType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

export type BucketObjectPage = {
  __typename?: 'BucketObjectPage';
  hasNextPage: Scalars['Boolean']['output'];
  hasPreviousPage: Scalars['Boolean']['output'];
  items: Array<BucketObject>;
  pageNumber: Scalars['Int']['output'];
};

export enum BucketObjectType {
  Directory = 'DIRECTORY',
  File = 'FILE'
}

export type CatalogEntry = {
  __typename?: 'CatalogEntry';
  countries: Array<Country>;
  datasource?: Maybe<Datasource>;
  description?: Maybe<Scalars['String']['output']>;
  externalDescription?: Maybe<Scalars['String']['output']>;
  externalId?: Maybe<Scalars['String']['output']>;
  externalName?: Maybe<Scalars['String']['output']>;
  externalSubtype?: Maybe<Scalars['String']['output']>;
  externalType?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  lastSyncedAt?: Maybe<Scalars['DateTime']['output']>;
  name: Scalars['String']['output'];
  objectId: Scalars['String']['output'];
  objectUrl: Scalars['URL']['output'];
  symbol?: Maybe<Scalars['URL']['output']>;
  type: CatalogEntryType;
};

export type CatalogEntryType = {
  __typename?: 'CatalogEntryType';
  app: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  model: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

export type CatalogPage = {
  __typename?: 'CatalogPage';
  items: Array<CatalogEntry>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type Collection = {
  __typename?: 'Collection';
  author?: Maybe<User>;
  countries: Array<Country>;
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  elements: CollectionElementPage;
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
  permissions: CollectionPermissions;
  summary?: Maybe<Scalars['String']['output']>;
  tags: Array<Tag>;
  updatedAt: Scalars['DateTime']['output'];
};


export type CollectionElementsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export type CollectionElement = {
  __typename?: 'CollectionElement';
  app: Scalars['String']['output'];
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  model: Scalars['String']['output'];
  name: Scalars['String']['output'];
  objectId: Scalars['String']['output'];
  type: Scalars['String']['output'];
  updatedAt: Scalars['DateTime']['output'];
  url?: Maybe<Scalars['URL']['output']>;
};

export type CollectionElementPage = {
  __typename?: 'CollectionElementPage';
  items: Array<CollectionElement>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type CollectionPage = {
  __typename?: 'CollectionPage';
  items: Array<Collection>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type CollectionPermissions = {
  __typename?: 'CollectionPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export type Connection = {
  __typename?: 'Connection';
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

export type ConnectionField = {
  __typename?: 'ConnectionField';
  code: Scalars['String']['output'];
  createdAt: Scalars['DateTime']['output'];
  secret: Scalars['Boolean']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  value?: Maybe<Scalars['String']['output']>;
};

export type ConnectionFieldInput = {
  code: Scalars['String']['input'];
  secret: Scalars['Boolean']['input'];
  value?: InputMaybe<Scalars['String']['input']>;
};

export type ConnectionPermissions = {
  __typename?: 'ConnectionPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

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

export enum CreateBucketFolderError {
  AlreadyExists = 'ALREADY_EXISTS',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateBucketFolderInput = {
  folderKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

export type CreateBucketFolderResult = {
  __typename?: 'CreateBucketFolderResult';
  errors: Array<CreateBucketFolderError>;
  folder?: Maybe<BucketObject>;
  success: Scalars['Boolean']['output'];
};

export enum CreateCollectionElementError {
  CollectionNotFound = 'COLLECTION_NOT_FOUND',
  Invalid = 'INVALID',
  ObjectNotFound = 'OBJECT_NOT_FOUND'
}

export type CreateCollectionElementInput = {
  app: Scalars['String']['input'];
  collectionId: Scalars['UUID']['input'];
  model: Scalars['String']['input'];
  objectId: Scalars['String']['input'];
};

export type CreateCollectionElementResult = {
  __typename?: 'CreateCollectionElementResult';
  element?: Maybe<CollectionElement>;
  errors: Array<CreateCollectionElementError>;
  success: Scalars['Boolean']['output'];
};

export enum CreateCollectionError {
  Invalid = 'INVALID'
}

export type CreateCollectionInput = {
  authorId?: InputMaybe<Scalars['String']['input']>;
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  name: Scalars['String']['input'];
  summary?: InputMaybe<Scalars['String']['input']>;
  tagIds?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type CreateCollectionResult = {
  __typename?: 'CreateCollectionResult';
  collection?: Maybe<Collection>;
  errors: Array<CreateCollectionError>;
  success: Scalars['Boolean']['output'];
};

export enum CreateConnectionError {
  InvalidSlug = 'INVALID_SLUG',
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

export type CreateConnectionInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  fields?: InputMaybe<Array<ConnectionFieldInput>>;
  name: Scalars['String']['input'];
  slug?: InputMaybe<Scalars['String']['input']>;
  type: ConnectionType;
  workspaceSlug: Scalars['String']['input'];
};

export type CreateConnectionResult = {
  __typename?: 'CreateConnectionResult';
  connection?: Maybe<Connection>;
  errors: Array<CreateConnectionError>;
  success: Scalars['Boolean']['output'];
};

export enum CreateMembershipError {
  AlreadyExists = 'ALREADY_EXISTS',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateMembershipInput = {
  role: MembershipRole;
  teamId: Scalars['UUID']['input'];
  userEmail: Scalars['String']['input'];
};

export type CreateMembershipResult = {
  __typename?: 'CreateMembershipResult';
  errors: Array<CreateMembershipError>;
  membership?: Maybe<Membership>;
  success: Scalars['Boolean']['output'];
};

export type CreatePipelineInput = {
  code: Scalars['String']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  workspaceSlug: Scalars['String']['input'];
};

export type CreatePipelineResult = {
  __typename?: 'CreatePipelineResult';
  errors: Array<PipelineError>;
  pipeline?: Maybe<Pipeline>;
  success: Scalars['Boolean']['output'];
};

export enum CreateTeamError {
  NameDuplicate = 'NAME_DUPLICATE',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateTeamInput = {
  name: Scalars['String']['input'];
};

export type CreateTeamResult = {
  __typename?: 'CreateTeamResult';
  errors: Array<CreateTeamError>;
  success: Scalars['Boolean']['output'];
  team?: Maybe<Team>;
};

export enum CreateWorkspaceError {
  InvalidSlug = 'INVALID_SLUG',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateWorkspaceInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  name: Scalars['String']['input'];
  slug?: InputMaybe<Scalars['String']['input']>;
};

export type CreateWorkspaceResult = {
  __typename?: 'CreateWorkspaceResult';
  errors: Array<CreateWorkspaceError>;
  success: Scalars['Boolean']['output'];
  workspace?: Maybe<Workspace>;
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
  Success = 'success'
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

export type Dhis2DataElement = {
  __typename?: 'DHIS2DataElement';
  code: Scalars['String']['output'];
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['String']['output'];
  instance: Dhis2Instance;
  name: Scalars['String']['output'];
  updatedAt: Scalars['DateTime']['output'];
};

export type Dhis2DataElementPage = {
  __typename?: 'DHIS2DataElementPage';
  items: Array<Dhis2DataElement>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type Dhis2Instance = {
  __typename?: 'DHIS2Instance';
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  url?: Maybe<Scalars['String']['output']>;
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

export type DatabaseTable = {
  __typename?: 'DatabaseTable';
  columns: Array<TableColumn>;
  count?: Maybe<Scalars['Int']['output']>;
  name: Scalars['String']['output'];
  rows: TableRowsPage;
  sample: Scalars['JSON']['output'];
};


export type DatabaseTableRowsArgs = {
  direction: OrderByDirection;
  orderBy: Scalars['String']['input'];
  page: Scalars['Int']['input'];
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export type DatabaseTablePage = {
  __typename?: 'DatabaseTablePage';
  items: Array<DatabaseTable>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type Datasource = {
  __typename?: 'Datasource';
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
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

export enum DeleteBucketObjectError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteBucketObjectInput = {
  objectKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

export type DeleteBucketObjectResult = {
  __typename?: 'DeleteBucketObjectResult';
  errors: Array<DeleteBucketObjectError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteCollectionElementError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type DeleteCollectionElementInput = {
  id: Scalars['UUID']['input'];
};

export type DeleteCollectionElementResult = {
  __typename?: 'DeleteCollectionElementResult';
  collection?: Maybe<Collection>;
  errors: Array<DeleteCollectionElementError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteCollectionError {
  Invalid = 'INVALID'
}

export type DeleteCollectionInput = {
  id: Scalars['UUID']['input'];
};

export type DeleteCollectionResult = {
  __typename?: 'DeleteCollectionResult';
  errors: Array<DeleteCollectionError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteConnectionError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteConnectionInput = {
  id: Scalars['String']['input'];
};

export type DeleteConnectionResult = {
  __typename?: 'DeleteConnectionResult';
  errors: Array<DeleteConnectionError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteMembershipError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteMembershipInput = {
  id: Scalars['UUID']['input'];
};

export type DeleteMembershipResult = {
  __typename?: 'DeleteMembershipResult';
  errors: Array<DeleteMembershipError>;
  success: Scalars['Boolean']['output'];
};

export type DeletePipelineInput = {
  id: Scalars['UUID']['input'];
};

export type DeletePipelineResult = {
  __typename?: 'DeletePipelineResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

export enum DeletePipelineVersionError {
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineVersionNotFound = 'PIPELINE_VERSION_NOT_FOUND'
}

export type DeletePipelineVersionInput = {
  pipelineId: Scalars['UUID']['input'];
  versionId: Scalars['UUID']['input'];
};

export type DeletePipelineVersionResult = {
  __typename?: 'DeletePipelineVersionResult';
  errors: Array<DeletePipelineVersionError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteTeamError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteTeamInput = {
  id: Scalars['UUID']['input'];
};

export type DeleteTeamResult = {
  __typename?: 'DeleteTeamResult';
  errors: Array<DeleteTeamError>;
  success: Scalars['Boolean']['output'];
};

export enum DeleteWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteWorkspaceInput = {
  slug: Scalars['String']['input'];
};

export enum DeleteWorkspaceMemberError {
  MembershipNotFound = 'MEMBERSHIP_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteWorkspaceMemberInput = {
  membershipId: Scalars['UUID']['input'];
};

export type DeleteWorkspaceMemberResult = {
  __typename?: 'DeleteWorkspaceMemberResult';
  errors: Array<DeleteWorkspaceMemberError>;
  success: Scalars['Boolean']['output'];
};

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

export enum DisableTwoFactorError {
  InvalidOtp = 'INVALID_OTP',
  NotEnabled = 'NOT_ENABLED'
}

export type DisableTwoFactorInput = {
  token: Scalars['String']['input'];
};

export type DisableTwoFactorResult = {
  __typename?: 'DisableTwoFactorResult';
  errors?: Maybe<Array<DisableTwoFactorError>>;
  success: Scalars['Boolean']['output'];
};

export enum EnableTwoFactorError {
  AlreadyEnabled = 'ALREADY_ENABLED',
  EmailMismatch = 'EMAIL_MISMATCH'
}

export type EnableTwoFactorInput = {
  email?: InputMaybe<Scalars['String']['input']>;
};

export type EnableTwoFactorResult = {
  __typename?: 'EnableTwoFactorResult';
  errors?: Maybe<Array<EnableTwoFactorError>>;
  success: Scalars['Boolean']['output'];
  verified?: Maybe<Scalars['Boolean']['output']>;
};

export type ExternalDashboard = {
  __typename?: 'ExternalDashboard';
  countries: Array<Country>;
  createdAt: Scalars['DateTime']['output'];
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
  pictureUrl: Scalars['URL']['output'];
  tags: Array<Tag>;
  updatedAt: Scalars['DateTime']['output'];
  url: Scalars['URL']['output'];
};

export type ExternalDashboardPage = {
  __typename?: 'ExternalDashboardPage';
  items: Array<ExternalDashboard>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type FeatureFlag = {
  __typename?: 'FeatureFlag';
  code: Scalars['String']['output'];
  config: Scalars['JSON']['output'];
};

export enum GenerateChallengeError {
  ChallengeError = 'CHALLENGE_ERROR',
  DeviceNotFound = 'DEVICE_NOT_FOUND'
}

export type GenerateChallengeResult = {
  __typename?: 'GenerateChallengeResult';
  errors?: Maybe<Array<GenerateChallengeError>>;
  success: Scalars['Boolean']['output'];
};

export enum GenerateNewDatabasePasswordError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type GenerateNewDatabasePasswordInput = {
  workspaceSlug: Scalars['String']['input'];
};

export type GenerateNewDatabasePasswordResult = {
  __typename?: 'GenerateNewDatabasePasswordResult';
  errors: Array<GenerateNewDatabasePasswordError>;
  success: Scalars['Boolean']['output'];
  workspace?: Maybe<Workspace>;
};

export enum GenerateWorkspaceTokenError {
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

export type GenerateWorkspaceTokenInput = {
  slug: Scalars['String']['input'];
};

export type GenerateWorkspaceTokenResult = {
  __typename?: 'GenerateWorkspaceTokenResult';
  errors: Array<GenerateWorkspaceTokenError>;
  success: Scalars['Boolean']['output'];
  token?: Maybe<Scalars['String']['output']>;
};

export type InviteWorkspaceMemberInput = {
  role: WorkspaceMembershipRole;
  userEmail: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

export type InviteWorkspaceMemberResult = {
  __typename?: 'InviteWorkspaceMemberResult';
  errors: Array<InviteWorkspaceMembershipError>;
  success: Scalars['Boolean']['output'];
  workspaceMembership?: Maybe<WorkspaceMembership>;
};

export enum InviteWorkspaceMembershipError {
  AlreadyExists = 'ALREADY_EXISTS',
  PermissionDenied = 'PERMISSION_DENIED',
  UserNotFound = 'USER_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

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

export type LogPipelineMessageInput = {
  message: Scalars['String']['input'];
  priority: MessagePriority;
};

export type LogPipelineMessageResult = {
  __typename?: 'LogPipelineMessageResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

export enum LoginError {
  InvalidCredentials = 'INVALID_CREDENTIALS',
  InvalidOtp = 'INVALID_OTP',
  OtpRequired = 'OTP_REQUIRED'
}

export type LoginInput = {
  email: Scalars['String']['input'];
  password: Scalars['String']['input'];
  token?: InputMaybe<Scalars['String']['input']>;
};

export type LoginResult = {
  __typename?: 'LoginResult';
  errors?: Maybe<Array<LoginError>>;
  success: Scalars['Boolean']['output'];
};

export type LogoutResult = {
  __typename?: 'LogoutResult';
  success: Scalars['Boolean']['output'];
};

export type Me = {
  __typename?: 'Me';
  features: Array<FeatureFlag>;
  hasTwoFactorEnabled: Scalars['Boolean']['output'];
  permissions: MePermissions;
  user?: Maybe<User>;
};

export type MePermissions = {
  __typename?: 'MePermissions';
  adminPanel: Scalars['Boolean']['output'];
  createAccessmodProject: Scalars['Boolean']['output'];
  createCollection: Scalars['Boolean']['output'];
  createTeam: Scalars['Boolean']['output'];
  createWorkspace: Scalars['Boolean']['output'];
  manageAccessmodAccessRequests: Scalars['Boolean']['output'];
  superUser: Scalars['Boolean']['output'];
};

export type Membership = {
  __typename?: 'Membership';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  permissions: MembershipPermissions;
  role: MembershipRole;
  team: Team;
  updatedAt: Scalars['DateTime']['output'];
  user: User;
};

export type MembershipPage = {
  __typename?: 'MembershipPage';
  items: Array<Membership>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type MembershipPermissions = {
  __typename?: 'MembershipPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export enum MembershipRole {
  Admin = 'ADMIN',
  Regular = 'REGULAR'
}

export enum MessagePriority {
  Critical = 'CRITICAL',
  Debug = 'DEBUG',
  Error = 'ERROR',
  Info = 'INFO',
  Warning = 'WARNING'
}

export type Mutation = {
  __typename?: 'Mutation';
  addPipelineOutput: AddPipelineOutputResult;
  approveAccessmodAccessRequest: ApproveAccessmodAccessRequestResult;
  archiveWorkspace: ArchiveWorkspaceResult;
  createAccessmodAccessibilityAnalysis: CreateAccessmodAccessibilityAnalysisResult;
  createAccessmodFile: CreateAccessmodFileResult;
  createAccessmodFileset: CreateAccessmodFilesetResult;
  createAccessmodProject: CreateAccessmodProjectResult;
  createAccessmodProjectMember: CreateAccessmodProjectMemberResult;
  createAccessmodZonalStatistics: CreateAccessmodZonalStatisticsResult;
  createBucketFolder: CreateBucketFolderResult;
  createCollection: CreateCollectionResult;
  createCollectionElement: CreateCollectionElementResult;
  createConnection: CreateConnectionResult;
  createMembership: CreateMembershipResult;
  createPipeline: CreatePipelineResult;
  createTeam: CreateTeamResult;
  createWorkspace: CreateWorkspaceResult;
  deleteAccessmodAnalysis: DeleteAccessmodAnalysisResult;
  deleteAccessmodFileset: DeleteAccessmodFilesetResult;
  deleteAccessmodProject: DeleteAccessmodProjectResult;
  deleteAccessmodProjectMember: DeleteAccessmodProjectMemberResult;
  deleteBucketObject: DeleteBucketObjectResult;
  deleteCollection: DeleteCollectionResult;
  deleteCollectionElement: DeleteCollectionElementResult;
  deleteConnection: DeleteConnectionResult;
  deleteMembership: DeleteMembershipResult;
  deletePipeline: DeletePipelineResult;
  deletePipelineVersion: DeletePipelineVersionResult;
  deleteTeam: DeleteTeamResult;
  deleteWorkspace: DeleteWorkspaceResult;
  deleteWorkspaceMember: DeleteWorkspaceMemberResult;
  denyAccessmodAccessRequest: DenyAccessmodAccessRequestResult;
  disableTwoFactor: DisableTwoFactorResult;
  enableTwoFactor: EnableTwoFactorResult;
  generateChallenge: GenerateChallengeResult;
  generateNewDatabasePassword: GenerateNewDatabasePasswordResult;
  generateWorkspaceToken: GenerateWorkspaceTokenResult;
  inviteWorkspaceMember: InviteWorkspaceMemberResult;
  launchAccessmodAnalysis: LaunchAccessmodAnalysisResult;
  launchNotebookServer: LaunchNotebookServerResult;
  logPipelineMessage: LogPipelineMessageResult;
  login: LoginResult;
  logout: LogoutResult;
  pipelineToken: PipelineTokenResult;
  prepareAccessmodFileDownload: PrepareAccessmodFileDownloadResult;
  prepareAccessmodFileUpload: PrepareAccessmodFileUploadResult;
  prepareAccessmodFilesetVisualizationDownload: PrepareAccessmodFilesetVisualizationDownloadResult;
  prepareDownloadURL?: Maybe<PrepareDownloadUrlResult>;
  prepareObjectDownload: PrepareObjectDownloadResult;
  prepareObjectUpload: PrepareObjectUploadResult;
  requestAccessmodAccess: RequestAccessmodAccessInputResult;
  resetPassword: ResetPasswordResult;
  runDAG: RunDagResult;
  runPipeline: RunPipelineResult;
  setDAGRunFavorite?: Maybe<SetDagRunFavoriteResult>;
  setPassword: SetPasswordResult;
  updateAccessmodAccessibilityAnalysis: UpdateAccessmodAccessibilityAnalysisResult;
  updateAccessmodFileset: UpdateAccessmodFilesetResult;
  updateAccessmodProject: UpdateAccessmodProjectResult;
  updateAccessmodProjectMember: UpdateAccessmodProjectMemberResult;
  updateAccessmodZonalStatistics: UpdateAccessmodZonalStatisticsResult;
  updateCollection: UpdateCollectionResult;
  updateConnection: UpdateConnectionResult;
  updateDAG: UpdateDagResult;
  updateExternalDashboard: UpdateExternalDashboardResult;
  updateMembership: UpdateMembershipResult;
  updatePipeline: UpdatePipelineResult;
  updatePipelineProgress: UpdatePipelineProgressResult;
  updateTeam: UpdateTeamResult;
  updateWorkspace: UpdateWorkspaceResult;
  updateWorkspaceMember: UpdateWorkspaceMemberResult;
  uploadPipeline: UploadPipelineResult;
  verifyDevice: VerifyDeviceResult;
};


export type MutationAddPipelineOutputArgs = {
  input?: InputMaybe<AddPipelineOutputInput>;
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


export type MutationCreateCollectionArgs = {
  input: CreateCollectionInput;
};


export type MutationCreateCollectionElementArgs = {
  input: CreateCollectionElementInput;
};


export type MutationCreateConnectionArgs = {
  input: CreateConnectionInput;
};


export type MutationCreateMembershipArgs = {
  input: CreateMembershipInput;
};


export type MutationCreatePipelineArgs = {
  input: CreatePipelineInput;
};


export type MutationCreateTeamArgs = {
  input: CreateTeamInput;
};


export type MutationCreateWorkspaceArgs = {
  input: CreateWorkspaceInput;
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


export type MutationDeleteCollectionArgs = {
  input: DeleteCollectionInput;
};


export type MutationDeleteCollectionElementArgs = {
  input: DeleteCollectionElementInput;
};


export type MutationDeleteConnectionArgs = {
  input: DeleteConnectionInput;
};


export type MutationDeleteMembershipArgs = {
  input: DeleteMembershipInput;
};


export type MutationDeletePipelineArgs = {
  input?: InputMaybe<DeletePipelineInput>;
};


export type MutationDeletePipelineVersionArgs = {
  input: DeletePipelineVersionInput;
};


export type MutationDeleteTeamArgs = {
  input: DeleteTeamInput;
};


export type MutationDeleteWorkspaceArgs = {
  input: DeleteWorkspaceInput;
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


export type MutationGenerateNewDatabasePasswordArgs = {
  input: GenerateNewDatabasePasswordInput;
};


export type MutationGenerateWorkspaceTokenArgs = {
  input: GenerateWorkspaceTokenInput;
};


export type MutationInviteWorkspaceMemberArgs = {
  input: InviteWorkspaceMemberInput;
};


export type MutationLaunchAccessmodAnalysisArgs = {
  input?: InputMaybe<LaunchAccessmodAnalysisInput>;
};


export type MutationLaunchNotebookServerArgs = {
  input: LaunchNotebookServerInput;
};


export type MutationLogPipelineMessageArgs = {
  input?: InputMaybe<LogPipelineMessageInput>;
};


export type MutationLoginArgs = {
  input: LoginInput;
};


export type MutationPipelineTokenArgs = {
  input?: InputMaybe<PipelineTokenInput>;
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


export type MutationRequestAccessmodAccessArgs = {
  input: RequestAccessmodAccessInput;
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


export type MutationSetPasswordArgs = {
  input: SetPasswordInput;
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


export type MutationUpdateCollectionArgs = {
  input: UpdateCollectionInput;
};


export type MutationUpdateConnectionArgs = {
  input: UpdateConnectionInput;
};


export type MutationUpdateDagArgs = {
  input: UpdateDagInput;
};


export type MutationUpdateExternalDashboardArgs = {
  input: UpdateExternalDashboardInput;
};


export type MutationUpdateMembershipArgs = {
  input: UpdateMembershipInput;
};


export type MutationUpdatePipelineArgs = {
  input: UpdatePipelineInput;
};


export type MutationUpdatePipelineProgressArgs = {
  input?: InputMaybe<UpdatePipelineProgressInput>;
};


export type MutationUpdateTeamArgs = {
  input: UpdateTeamInput;
};


export type MutationUpdateWorkspaceArgs = {
  input: UpdateWorkspaceInput;
};


export type MutationUpdateWorkspaceMemberArgs = {
  input: UpdateWorkspaceMemberInput;
};


export type MutationUploadPipelineArgs = {
  input?: InputMaybe<UploadPipelineInput>;
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

export enum OrderByDirection {
  Asc = 'ASC',
  Desc = 'DESC'
}

export type Organization = {
  __typename?: 'Organization';
  contactInfo: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
  type: Scalars['String']['output'];
  url: Scalars['String']['output'];
};

export type OrganizationInput = {
  contactInfo?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  type?: InputMaybe<Scalars['String']['input']>;
  url?: InputMaybe<Scalars['String']['input']>;
};

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

export enum PermissionMode {
  Editor = 'EDITOR',
  Owner = 'OWNER',
  Viewer = 'VIEWER'
}

export type Pipeline = {
  __typename?: 'Pipeline';
  code: Scalars['String']['output'];
  config: Scalars['JSON']['output'];
  createdAt: Scalars['DateTime']['output'];
  currentVersion?: Maybe<PipelineVersion>;
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  name?: Maybe<Scalars['String']['output']>;
  permissions: PipelinePermissions;
  runs: PipelineRunPage;
  schedule?: Maybe<Scalars['String']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  versions: PipelineVersionPage;
  workspace?: Maybe<Workspace>;
};


export type PipelineRunsArgs = {
  orderBy?: InputMaybe<PipelineRunOrderBy>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


export type PipelineVersionsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export enum PipelineError {
  InvalidConfig = 'INVALID_CONFIG',
  PipelineAlreadyCompleted = 'PIPELINE_ALREADY_COMPLETED',
  PipelineAlreadyExists = 'PIPELINE_ALREADY_EXISTS',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineVersionNotFound = 'PIPELINE_VERSION_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

export type PipelineParameter = {
  __typename?: 'PipelineParameter';
  choices?: Maybe<Array<Scalars['Generic']['output']>>;
  code: Scalars['String']['output'];
  default?: Maybe<Scalars['Generic']['output']>;
  help?: Maybe<Scalars['String']['output']>;
  multiple: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  required: Scalars['Boolean']['output'];
  type: Scalars['String']['output'];
};

export type PipelinePermissions = {
  __typename?: 'PipelinePermissions';
  delete: Scalars['Boolean']['output'];
  deleteVersion: Scalars['Boolean']['output'];
  run: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

export type PipelineRun = {
  __typename?: 'PipelineRun';
  code: Scalars['String']['output'];
  config: Scalars['JSON']['output'];
  duration?: Maybe<Scalars['Int']['output']>;
  executionDate?: Maybe<Scalars['DateTime']['output']>;
  id: Scalars['UUID']['output'];
  logs?: Maybe<Scalars['String']['output']>;
  messages: Array<PipelineRunMessage>;
  outputs: Array<PipelineRunOutput>;
  pipeline: Pipeline;
  progress: Scalars['Int']['output'];
  run_id: Scalars['UUID']['output'];
  status: PipelineRunStatus;
  triggerMode?: Maybe<PipelineRunTrigger>;
  user?: Maybe<User>;
  version: PipelineVersion;
};

export type PipelineRunMessage = {
  __typename?: 'PipelineRunMessage';
  message: Scalars['String']['output'];
  priority: MessagePriority;
  timestamp?: Maybe<Scalars['DateTime']['output']>;
};

export enum PipelineRunOrderBy {
  ExecutionDateAsc = 'EXECUTION_DATE_ASC',
  ExecutionDateDesc = 'EXECUTION_DATE_DESC'
}

export type PipelineRunOutput = {
  __typename?: 'PipelineRunOutput';
  name?: Maybe<Scalars['String']['output']>;
  type: Scalars['String']['output'];
  uri: Scalars['String']['output'];
};

export type PipelineRunPage = {
  __typename?: 'PipelineRunPage';
  items: Array<PipelineRun>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export enum PipelineRunStatus {
  Failed = 'failed',
  Queued = 'queued',
  Running = 'running',
  Success = 'success'
}

export enum PipelineRunTrigger {
  Manual = 'manual',
  Scheduled = 'scheduled'
}

export type PipelineTokenInput = {
  pipelineCode: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

export type PipelineTokenResult = {
  __typename?: 'PipelineTokenResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
  token?: Maybe<Scalars['String']['output']>;
};

export type PipelineVersion = {
  __typename?: 'PipelineVersion';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  number: Scalars['Int']['output'];
  parameters: Array<PipelineParameter>;
  pipeline: Pipeline;
  user?: Maybe<User>;
  zipfile: Scalars['String']['output'];
};

export type PipelineVersionPage = {
  __typename?: 'PipelineVersionPage';
  items: Array<PipelineVersion>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type PipelinesPage = {
  __typename?: 'PipelinesPage';
  items: Array<Pipeline>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
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

export enum PrepareObjectDownloadError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type PrepareObjectDownloadInput = {
  objectKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

export type PrepareObjectDownloadResult = {
  __typename?: 'PrepareObjectDownloadResult';
  downloadUrl?: Maybe<Scalars['URL']['output']>;
  errors: Array<PrepareObjectDownloadError>;
  success: Scalars['Boolean']['output'];
};

export enum PrepareObjectUploadError {
  PermissionDenied = 'PERMISSION_DENIED'
}

export type PrepareObjectUploadInput = {
  contentType?: InputMaybe<Scalars['String']['input']>;
  objectKey: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

export type PrepareObjectUploadResult = {
  __typename?: 'PrepareObjectUploadResult';
  errors: Array<PrepareObjectUploadError>;
  success: Scalars['Boolean']['output'];
  uploadUrl?: Maybe<Scalars['URL']['output']>;
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
  catalog: CatalogPage;
  collection?: Maybe<Collection>;
  collections: CollectionPage;
  connection?: Maybe<Connection>;
  countries: Array<Country>;
  country?: Maybe<Country>;
  dag?: Maybe<Dag>;
  dagRun?: Maybe<DagRun>;
  dags: DagPage;
  databaseTable?: Maybe<DatabaseTable>;
  externalDashboard?: Maybe<ExternalDashboard>;
  externalDashboards: ExternalDashboardPage;
  lastActivities: Array<Activity>;
  me: Me;
  notebooksUrl: Scalars['URL']['output'];
  organizations: Array<Organization>;
  pipeline?: Maybe<Pipeline>;
  pipelineByCode?: Maybe<Pipeline>;
  pipelineRun?: Maybe<PipelineRun>;
  pipelines: PipelinesPage;
  search: SearchQueryResult;
  team?: Maybe<Team>;
  teams: TeamPage;
  totalNotebooks: Scalars['Int']['output'];
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


export type QueryCatalogArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  path?: InputMaybe<Scalars['String']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryCollectionArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryCollectionsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


export type QueryConnectionArgs = {
  id: Scalars['UUID']['input'];
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


export type QueryExternalDashboardArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryExternalDashboardsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
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


export type QueryPipelinesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QuerySearchArgs = {
  datasourceIds?: InputMaybe<Array<Scalars['UUID']['input']>>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
  types?: InputMaybe<Array<Scalars['String']['input']>>;
};


export type QueryTeamArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryTeamsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  term?: InputMaybe<Scalars['String']['input']>;
};


export type QueryWorkspaceArgs = {
  slug: Scalars['String']['input'];
};


export type QueryWorkspacesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
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

export type ResetPasswordInput = {
  email: Scalars['String']['input'];
};

export type ResetPasswordResult = {
  __typename?: 'ResetPasswordResult';
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

export type RunPipelineInput = {
  config: Scalars['JSON']['input'];
  id: Scalars['UUID']['input'];
  version?: InputMaybe<Scalars['Int']['input']>;
};

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

export type S3Object = {
  __typename?: 'S3Object';
  bucket: S3Bucket;
  collections: Array<Collection>;
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

export type SearchQueryResult = {
  __typename?: 'SearchQueryResult';
  results: Array<SearchResult>;
  types: Array<SearchType>;
};

export type SearchResult = {
  __typename?: 'SearchResult';
  object: SearchResultObject;
  rank: Scalars['Float']['output'];
};

export type SearchResultObject = CatalogEntry | Collection;

export type SearchType = {
  __typename?: 'SearchType';
  label: Scalars['String']['output'];
  value: Scalars['String']['output'];
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

export enum SetPasswordError {
  InvalidPassword = 'INVALID_PASSWORD',
  InvalidToken = 'INVALID_TOKEN',
  PasswordMismatch = 'PASSWORD_MISMATCH',
  UserNotFound = 'USER_NOT_FOUND'
}

export type SetPasswordInput = {
  password1: Scalars['String']['input'];
  password2: Scalars['String']['input'];
  token: Scalars['String']['input'];
  uidb64: Scalars['String']['input'];
};

export type SetPasswordResult = {
  __typename?: 'SetPasswordResult';
  error?: Maybe<SetPasswordError>;
  success: Scalars['Boolean']['output'];
};

export type TableColumn = {
  __typename?: 'TableColumn';
  name: Scalars['String']['output'];
  type: Scalars['String']['output'];
};

export type TableRowsPage = {
  __typename?: 'TableRowsPage';
  hasNextPage: Scalars['Boolean']['output'];
  hasPreviousPage: Scalars['Boolean']['output'];
  items: Array<Scalars['JSON']['output']>;
  pageNumber: Scalars['Int']['output'];
};

export type Tag = {
  __typename?: 'Tag';
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
};

export type Team = {
  __typename?: 'Team';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  memberships: MembershipPage;
  name: Scalars['String']['output'];
  permissions: TeamPermissions;
  updatedAt: Scalars['DateTime']['output'];
};


export type TeamMembershipsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export type TeamPage = {
  __typename?: 'TeamPage';
  items: Array<Team>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type TeamPermissions = {
  __typename?: 'TeamPermissions';
  createMembership: Scalars['Boolean']['output'];
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
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

export enum UpdateCollectionError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type UpdateCollectionInput = {
  authorId?: InputMaybe<Scalars['String']['input']>;
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  summary?: InputMaybe<Scalars['String']['input']>;
  tagIds?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type UpdateCollectionResult = {
  __typename?: 'UpdateCollectionResult';
  collection?: Maybe<Collection>;
  errors: Array<CreateCollectionError>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateConnectionError {
  InvalidSlug = 'INVALID_SLUG',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateConnectionInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  fields?: InputMaybe<Array<ConnectionFieldInput>>;
  id: Scalars['String']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  slug?: InputMaybe<Scalars['String']['input']>;
};

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

export enum UpdateExternalDashboardError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type UpdateExternalDashboardInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateExternalDashboardResult = {
  __typename?: 'UpdateExternalDashboardResult';
  errors: Array<UpdateExternalDashboardError>;
  externalDashboard?: Maybe<ExternalDashboard>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateMembershipError {
  InvalidRole = 'INVALID_ROLE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateMembershipInput = {
  id: Scalars['UUID']['input'];
  role: MembershipRole;
};

export type UpdateMembershipResult = {
  __typename?: 'UpdateMembershipResult';
  errors: Array<UpdateMembershipError>;
  membership?: Maybe<Membership>;
  success: Scalars['Boolean']['output'];
};

export enum UpdatePipelineError {
  InvalidConfig = 'INVALID_CONFIG',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdatePipelineInput = {
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  schedule?: InputMaybe<Scalars['String']['input']>;
};

export type UpdatePipelineProgressInput = {
  percent: Scalars['Int']['input'];
};

export type UpdatePipelineProgressResult = {
  __typename?: 'UpdatePipelineProgressResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
};

export type UpdatePipelineResult = {
  __typename?: 'UpdatePipelineResult';
  errors: Array<UpdatePipelineError>;
  pipeline?: Maybe<Pipeline>;
  success: Scalars['Boolean']['output'];
};

export enum UpdateTeamError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateTeamInput = {
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateTeamResult = {
  __typename?: 'UpdateTeamResult';
  errors: Array<UpdateTeamError>;
  success: Scalars['Boolean']['output'];
  team?: Maybe<Team>;
};

export enum UpdateWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateWorkspaceInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  slug: Scalars['String']['input'];
};

export enum UpdateWorkspaceMemberError {
  MembershipNotFound = 'MEMBERSHIP_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateWorkspaceMemberInput = {
  membershipId: Scalars['UUID']['input'];
  role: WorkspaceMembershipRole;
};

export type UpdateWorkspaceMemberResult = {
  __typename?: 'UpdateWorkspaceMemberResult';
  errors: Array<UpdateWorkspaceMemberError>;
  success: Scalars['Boolean']['output'];
  workspaceMembership?: Maybe<WorkspaceMembership>;
};

export type UpdateWorkspaceResult = {
  __typename?: 'UpdateWorkspaceResult';
  errors: Array<UpdateWorkspaceError>;
  success: Scalars['Boolean']['output'];
  workspace?: Maybe<Workspace>;
};

export type UploadPipelineInput = {
  code: Scalars['String']['input'];
  parameters: Array<ParameterInput>;
  workspaceSlug: Scalars['String']['input'];
  zipfile: Scalars['String']['input'];
};

export type UploadPipelineResult = {
  __typename?: 'UploadPipelineResult';
  errors: Array<PipelineError>;
  success: Scalars['Boolean']['output'];
  version?: Maybe<Scalars['Int']['output']>;
};

export type User = {
  __typename?: 'User';
  avatar: Avatar;
  dateJoined: Scalars['DateTime']['output'];
  displayName: Scalars['String']['output'];
  email: Scalars['String']['output'];
  firstName?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  lastLogin?: Maybe<Scalars['DateTime']['output']>;
  lastName?: Maybe<Scalars['String']['output']>;
};

export enum VerifyDeviceError {
  InvalidOtp = 'INVALID_OTP',
  NoDevice = 'NO_DEVICE'
}

export type VerifyDeviceInput = {
  token?: InputMaybe<Scalars['String']['input']>;
};

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

export type Workspace = {
  __typename?: 'Workspace';
  bucket: Bucket;
  connections: Array<Connection>;
  countries: Array<Country>;
  createdAt: Scalars['DateTime']['output'];
  createdBy: User;
  database: Database;
  description?: Maybe<Scalars['String']['output']>;
  members: WorkspaceMembershipPage;
  name: Scalars['String']['output'];
  permissions: WorkspacePermissions;
  slug: Scalars['String']['output'];
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};


export type WorkspaceMembersArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};

export type WorkspaceMembership = {
  __typename?: 'WorkspaceMembership';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  role: WorkspaceMembershipRole;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user: User;
  workspace: Workspace;
};

export type WorkspaceMembershipPage = {
  __typename?: 'WorkspaceMembershipPage';
  items: Array<WorkspaceMembership>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export enum WorkspaceMembershipRole {
  Admin = 'ADMIN',
  Editor = 'EDITOR',
  Viewer = 'VIEWER'
}

export type WorkspacePage = {
  __typename?: 'WorkspacePage';
  items: Array<Workspace>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type WorkspacePermissions = {
  __typename?: 'WorkspacePermissions';
  createConnection: Scalars['Boolean']['output'];
  createObject: Scalars['Boolean']['output'];
  createPipeline: Scalars['Boolean']['output'];
  delete: Scalars['Boolean']['output'];
  deleteObject: Scalars['Boolean']['output'];
  downloadObject: Scalars['Boolean']['output'];
  launchNotebookServer: Scalars['Boolean']['output'];
  manageMembers: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};
