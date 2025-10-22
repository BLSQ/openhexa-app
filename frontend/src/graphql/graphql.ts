/* eslint-disable */
import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
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
  UUID: { input: string; output: string; }
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

/** The AddOrganizationMemberError enum represents the possible errors that can occur during the addOrganizationMember mutation. */
export enum AddOrganizationMemberError {
  /** Indicates that the user does not have permission to add members to the organization. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The AddOrganizationMemberInput type represents the input for the addOrganizationMember mutation. */
export type AddOrganizationMemberInput = {
  /** The unique identifier of the organization. */
  organizationId: Scalars['UUID']['input'];
  /** The role of the user in the organization. */
  role: OrganizationMembershipRole;
  /** The email address of the user to add to the organization. */
  userEmail: Scalars['String']['input'];
};

/** The AddOrganizationMemberResult type represents the result of the addOrganizationMember mutation. */
export type AddOrganizationMemberResult = {
  __typename?: 'AddOrganizationMemberResult';
  /** The list of errors that occurred during the addOrganizationMember mutation. */
  errors: Array<AddOrganizationMemberError>;
  /** The created organization membership object. */
  membership?: Maybe<OrganizationMembership>;
  /** Indicates whether the addOrganizationMember mutation was successful. */
  success: Scalars['Boolean']['output'];
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

/** Represents the error message for adding a web app to favorites. */
export enum AddToFavoritesError {
  WebappNotFound = 'WEBAPP_NOT_FOUND'
}

/** Represents the input for adding a web app to favorites. */
export type AddToFavoritesInput = {
  webappId: Scalars['ID']['input'];
};

/** Represents the result of adding a web app to favorites. */
export type AddToFavoritesResult = {
  __typename?: 'AddToFavoritesResult';
  errors: Array<AddToFavoritesError>;
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
  /** @deprecated The code will be autogenerated */
  code?: InputMaybe<Scalars['String']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
  name: Scalars['String']['input'];
  notebookPath?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
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

/** Represents the permission details for creating a template version. */
export type CreateTemplateVersionPermission = {
  __typename?: 'CreateTemplateVersionPermission';
  isAllowed: Scalars['Boolean']['output'];
  reasons: Array<CreateTemplateVersionPermissionReason>;
};

/** Enum representing the possible reasons preventing the creation of a template version. */
export enum CreateTemplateVersionPermissionReason {
  NoNewTemplateVersionAvailable = 'NO_NEW_TEMPLATE_VERSION_AVAILABLE',
  PermissionDenied = 'PERMISSION_DENIED',
  PipelineIsAlreadyFromTemplate = 'PIPELINE_IS_ALREADY_FROM_TEMPLATE',
  PipelineIsNotebook = 'PIPELINE_IS_NOTEBOOK'
}

/** Represents the error message for a web app creation. */
export enum CreateWebappError {
  AlreadyExists = 'ALREADY_EXISTS',
  PermissionDenied = 'PERMISSION_DENIED',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** Represents the input for creating a web app. */
export type CreateWebappInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  icon?: InputMaybe<Scalars['String']['input']>;
  name: Scalars['String']['input'];
  url: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};

/** Represents the result of creating a web app. */
export type CreateWebappResult = {
  __typename?: 'CreateWebappResult';
  errors: Array<CreateWebappError>;
  success: Scalars['Boolean']['output'];
  webapp?: Maybe<Webapp>;
};

/** Enum representing the possible errors that can occur when creating a workspace. */
export enum CreateWorkspaceError {
  InvalidSlug = 'INVALID_SLUG',
  OrganizationNotFound = 'ORGANIZATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for creating a workspace. */
export type CreateWorkspaceInput = {
  configuration?: InputMaybe<Scalars['JSON']['input']>;
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']['input']>;
  loadSampleData?: InputMaybe<Scalars['Boolean']['input']>;
  name: Scalars['String']['input'];
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
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
  queryMetadata: Dhis2QueryResultPage;
  slug: Scalars['String']['output'];
  status: Dhis2ConnectionStatus;
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};


/** DHIS2 connection object */
export type Dhis2ConnectionQueryMetadataArgs = {
  filters?: InputMaybe<Array<Scalars['String']['input']>>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  type: Dhis2MetadataType;
};

/** DHIS2 connection error */
export enum Dhis2ConnectionError {
  RequestError = 'REQUEST_ERROR',
  UnknownError = 'UNKNOWN_ERROR'
}

/** DHIS2 connection status */
export enum Dhis2ConnectionStatus {
  Down = 'DOWN',
  Unknown = 'UNKNOWN',
  Up = 'UP'
}

/** DHIS2 metadata item */
export type Dhis2MetadataItem = {
  __typename?: 'DHIS2MetadataItem';
  id?: Maybe<Scalars['String']['output']>;
  label: Scalars['String']['output'];
};

/** Enum representing the type of a DHIS2 metadata item. */
export enum Dhis2MetadataType {
  Datasets = 'DATASETS',
  DataElements = 'DATA_ELEMENTS',
  DataElementGroups = 'DATA_ELEMENT_GROUPS',
  Indicators = 'INDICATORS',
  IndicatorGroups = 'INDICATOR_GROUPS',
  OrgUnits = 'ORG_UNITS',
  OrgUnitGroups = 'ORG_UNIT_GROUPS',
  OrgUnitLevels = 'ORG_UNIT_LEVELS'
}

/** DHIS2 metadata query result */
export type Dhis2QueryResultPage = {
  __typename?: 'DHIS2QueryResultPage';
  error?: Maybe<Dhis2ConnectionError>;
  items?: Maybe<Array<Dhis2MetadataItem>>;
  pageNumber: Scalars['Int']['output'];
  success: Scalars['Boolean']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
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

export type DatabaseTableResult = SearchResult & {
  __typename?: 'DatabaseTableResult';
  databaseTable: DatabaseTable;
  score: Scalars['Float']['output'];
  workspace: Workspace;
};

export type DatabaseTableResultPage = {
  __typename?: 'DatabaseTableResultPage';
  items: Array<DatabaseTableResult>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
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
  sharedWithOrganization: Scalars['Boolean']['output'];
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

export type DatasetResult = SearchResult & {
  __typename?: 'DatasetResult';
  dataset: Dataset;
  score: Scalars['Float']['output'];
};

export type DatasetResultPage = {
  __typename?: 'DatasetResultPage';
  items: Array<DatasetResult>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
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

/** The DeleteOrganizationInvitationError enum represents the possible errors that can occur during the deleteOrganizationInvitation mutation. */
export enum DeleteOrganizationInvitationError {
  InvitationNotFound = 'INVITATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The DeleteOrganizationInvitationInput type represents the input for the deleteOrganizationInvitation mutation. */
export type DeleteOrganizationInvitationInput = {
  /** The unique identifier of the organization invitation to delete. */
  id: Scalars['UUID']['input'];
};

/** The DeleteOrganizationInvitationResult type represents the result of the deleteOrganizationInvitation mutation. */
export type DeleteOrganizationInvitationResult = {
  __typename?: 'DeleteOrganizationInvitationResult';
  errors: Array<DeleteOrganizationInvitationError>;
  success: Scalars['Boolean']['output'];
};

/** The DeleteOrganizationMemberError enum represents the possible errors that can occur during the deleteOrganizationMember mutation. */
export enum DeleteOrganizationMemberError {
  /** Indicates that users cannot delete themselves from an organization. */
  CannotDeleteSelf = 'CANNOT_DELETE_SELF',
  /** Indicates that the organization membership was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to delete the organization membership. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The DeleteOrganizationMemberInput type represents the input for the deleteOrganizationMember mutation. */
export type DeleteOrganizationMemberInput = {
  /** The unique identifier of the organization membership to delete. */
  id: Scalars['UUID']['input'];
};

/** The DeleteOrganizationMemberResult type represents the result of the deleteOrganizationMember mutation. */
export type DeleteOrganizationMemberResult = {
  __typename?: 'DeleteOrganizationMemberResult';
  /** The list of errors that occurred during the deleteOrganizationMember mutation. */
  errors: Array<DeleteOrganizationMemberError>;
  /** Indicates whether the deleteOrganizationMember mutation was successful. */
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

/** Represents the result of deleting a template. */
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

/** Represents the error message for a web app deletion. */
export enum DeleteWebappError {
  PermissionDenied = 'PERMISSION_DENIED',
  WebappNotFound = 'WEBAPP_NOT_FOUND'
}

/** Represents the input for deleting a web app. */
export type DeleteWebappInput = {
  id: Scalars['UUID']['input'];
};

/** Represents the result of deleting a web app. */
export type DeleteWebappResult = {
  __typename?: 'DeleteWebappResult';
  errors: Array<DeleteWebappError>;
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
  /**
   * The configuration of the feature flag (deprecated).
   * @deprecated This field is deprecated and will be removed in the next version. In the meantime it always returns an empty object.
   */
  config: Scalars['JSON']['output'];
};

export type File = {
  __typename?: 'File';
  key: Scalars['String']['output'];
  name: Scalars['String']['output'];
  path: Scalars['String']['output'];
  size?: Maybe<Scalars['BigInt']['output']>;
  type: FileType;
  /** @deprecated Use updatedAt instead */
  updated?: Maybe<Scalars['DateTime']['output']>;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
};

/** Represents a file or directory node in a flattened structure. */
export type FileNode = {
  __typename?: 'FileNode';
  autoSelect: Scalars['Boolean']['output'];
  content?: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  language?: Maybe<Scalars['String']['output']>;
  lineCount?: Maybe<Scalars['Int']['output']>;
  name: Scalars['String']['output'];
  parentId?: Maybe<Scalars['String']['output']>;
  path: Scalars['String']['output'];
  type: FileType;
};

export type FileResult = SearchResult & {
  __typename?: 'FileResult';
  file: File;
  score: Scalars['Float']['output'];
  workspace: Workspace;
};

export type FileResultPage = {
  __typename?: 'FileResultPage';
  items: Array<FileResult>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Statuses that can occur when generating file sample */
export enum FileSampleStatus {
  Failed = 'FAILED',
  Finished = 'FINISHED',
  Processing = 'PROCESSING'
}

export enum FileType {
  Directory = 'directory',
  File = 'file'
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
  queryMetadata: IasoQueryResultPage;
  slug: Scalars['String']['output'];
  type: ConnectionType;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user?: Maybe<User>;
};


/** IASO connection object */
export type IasoConnectionQueryMetadataArgs = {
  filters?: InputMaybe<Array<IasoQueryFilterInput>>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  type: IasoMetadataType;
};

/** IASO connection error */
export enum IasoConnectionError {
  RequestError = 'REQUEST_ERROR',
  UnknownError = 'UNKNOWN_ERROR'
}

/** IASO metadata item */
export type IasoMetadataItem = {
  __typename?: 'IASOMetadataItem';
  id?: Maybe<Scalars['Int']['output']>;
  label: Scalars['String']['output'];
};

/** Enum representing the type for IASO metadata item. */
export enum IasoMetadataType {
  IasoForms = 'IASO_FORMS',
  IasoOrgUnits = 'IASO_ORG_UNITS',
  IasoProjects = 'IASO_PROJECTS'
}

export type IasoQueryFilterInput = {
  type: Scalars['String']['input'];
  value: Array<InputMaybe<Scalars['Int']['input']>>;
};

/** IASO metadata query result */
export type IasoQueryResultPage = {
  __typename?: 'IASOQueryResultPage';
  error?: Maybe<IasoConnectionError>;
  items?: Maybe<Array<IasoMetadataItem>>;
  pageNumber: Scalars['Int']['output'];
  success: Scalars['Boolean']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** The InviteOrganizationMemberError enum represents the possible errors that can occur during the inviteOrganizationMember mutation. */
export enum InviteOrganizationMemberError {
  /** Indicates that the user is already a member of the organization. */
  AlreadyMember = 'ALREADY_MEMBER',
  /** Indicates that the organization was not found. */
  OrganizationNotFound = 'ORGANIZATION_NOT_FOUND',
  /** Indicates that the user does not have permission to invite members to the organization. */
  PermissionDenied = 'PERMISSION_DENIED',
  /** Indicates that one or more workspaces were not found. */
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/** The InviteOrganizationMemberInput type represents the input for the inviteOrganizationMember mutation. */
export type InviteOrganizationMemberInput = {
  /** The unique identifier of the organization. */
  organizationId: Scalars['UUID']['input'];
  /** The role of the user in the organization. */
  organizationRole: OrganizationMembershipRole;
  /** The email address of the user to invite to the organization. */
  userEmail: Scalars['String']['input'];
  /** The list of workspaces to invite the user to. */
  workspaceInvitations: Array<WorkspaceInvitationInput>;
};

/** The InviteOrganizationMemberResult type represents the result of the inviteOrganizationMember mutation. */
export type InviteOrganizationMemberResult = {
  __typename?: 'InviteOrganizationMemberResult';
  /** The list of errors that occurred during the inviteOrganizationMember mutation. */
  errors: Array<InviteOrganizationMemberError>;
  /** Indicates whether the inviteOrganizationMember mutation was successful. */
  success: Scalars['Boolean']['output'];
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
  addToFavorites: AddToFavoritesResult;
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
  createWebapp: CreateWebappResult;
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
  deleteOrganizationInvitation: DeleteOrganizationInvitationResult;
  deleteOrganizationMember: DeleteOrganizationMemberResult;
  /** Deletes a pipeline. */
  deletePipeline: DeletePipelineResult;
  /** Deletes a pipeline recipient. */
  deletePipelineRecipient: DeletePipelineRecipientResult;
  /** Deletes a pipeline template. */
  deletePipelineTemplate: DeletePipelineTemplateResult;
  /** Deletes a pipeline version. */
  deletePipelineVersion: DeletePipelineVersionResult;
  deleteTeam: DeleteTeamResult;
  /** Deletes a template version. */
  deleteTemplateVersion: DeleteTemplateVersionResult;
  deleteWebapp: DeleteWebappResult;
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
  inviteOrganizationMember: InviteOrganizationMemberResult;
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
  removeFromFavorites: RemoveFromFavoritesResult;
  requestAccessmodAccess: RequestAccessmodAccessInputResult;
  resendOrganizationInvitation: ResendOrganizationInvitationResult;
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
  updateOrganizationMember: UpdateOrganizationMemberResult;
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
  /** Updates a template version. */
  updateTemplateVersion: UpdateTemplateVersionResult;
  /** Updates the profile of the currently authenticated user. */
  updateUser: UpdateUserResult;
  updateWebapp: UpdateWebappResult;
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


export type MutationAddToFavoritesArgs = {
  input: AddToFavoritesInput;
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


export type MutationCreateWebappArgs = {
  input: CreateWebappInput;
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


export type MutationDeleteOrganizationInvitationArgs = {
  input: DeleteOrganizationInvitationInput;
};


export type MutationDeleteOrganizationMemberArgs = {
  input: DeleteOrganizationMemberInput;
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


export type MutationDeleteWebappArgs = {
  input: DeleteWebappInput;
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


export type MutationInviteOrganizationMemberArgs = {
  input: InviteOrganizationMemberInput;
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


export type MutationRemoveFromFavoritesArgs = {
  input: RemoveFromFavoritesInput;
};


export type MutationRequestAccessmodAccessArgs = {
  input: RequestAccessmodAccessInput;
};


export type MutationResendOrganizationInvitationArgs = {
  input: ResendOrganizationInvitationInput;
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


export type MutationUpdateOrganizationMemberArgs = {
  input: UpdateOrganizationMemberInput;
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


export type MutationUpdateWebappArgs = {
  input: UpdateWebappInput;
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
  /** Dataset links available in the organization */
  datasetLinks: DatasetLinkPage;
  /** Datasets available in the organization */
  datasets: DatasetPage;
  /** The unique identifier of the organization. */
  id: Scalars['UUID']['output'];
  /** The invitations sent to join the organization. */
  invitations: OrganizationInvitationPage;
  /** The members of the organization. */
  members: OrganizationMembershipPage;
  /** The name of the organization. */
  name: Scalars['String']['output'];
  /** The direct invitations sent to join a specific workspace in the organization. */
  pendingWorkspaceInvitations: WorkspaceInvitationPage;
  /** The permissions the current user has in the organization. */
  permissions: OrganizationPermissions;
  /** Pipeline tags used within this organization. */
  pipelineTags: Array<Scalars['String']['output']>;
  /** Pipeline template tags used within this organization. */
  pipelineTemplateTags: Array<Scalars['String']['output']>;
  /** The short name of the organization. */
  shortName?: Maybe<Scalars['String']['output']>;
  /** The type of the organization. */
  type: Scalars['String']['output'];
  /** The URL of the organization. */
  url: Scalars['String']['output'];
  /** The workspaces associated with the organization. */
  workspaces: WorkspacePage;
};


/** The Organization type represents an organization in the system. */
export type OrganizationDatasetLinksArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
};


/** The Organization type represents an organization in the system. */
export type OrganizationDatasetsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
};


/** The Organization type represents an organization in the system. */
export type OrganizationInvitationsArgs = {
  includeAccepted?: InputMaybe<Scalars['Boolean']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


/** The Organization type represents an organization in the system. */
export type OrganizationMembersArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  role?: InputMaybe<OrganizationMembershipRole>;
  term?: InputMaybe<Scalars['String']['input']>;
};


/** The Organization type represents an organization in the system. */
export type OrganizationPendingWorkspaceInvitationsArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
};


/** The Organization type represents an organization in the system. */
export type OrganizationWorkspacesArgs = {
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
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

/** Represents an invitation to join an organization. */
export type OrganizationInvitation = {
  __typename?: 'OrganizationInvitation';
  createdAt: Scalars['DateTime']['output'];
  email: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  invitedBy?: Maybe<User>;
  organization: Organization;
  role: OrganizationMembershipRole;
  status: OrganizationInvitationStatus;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  workspaceInvitations: Array<OrganizationWorkspaceInvitation>;
};

/** Represents a page of organization invitations. */
export type OrganizationInvitationPage = {
  __typename?: 'OrganizationInvitationPage';
  items: Array<OrganizationInvitation>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the status of an organization invitation. */
export enum OrganizationInvitationStatus {
  Accepted = 'ACCEPTED',
  Declined = 'DECLINED',
  Pending = 'PENDING'
}

/** Represents a membership in an organization. */
export type OrganizationMembership = {
  __typename?: 'OrganizationMembership';
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  organization: Organization;
  role: OrganizationMembershipRole;
  updatedAt?: Maybe<Scalars['DateTime']['output']>;
  user: User;
  workspaceMemberships: Array<WorkspaceMembership>;
};

/** Represents a page of organization memberships. */
export type OrganizationMembershipPage = {
  __typename?: 'OrganizationMembershipPage';
  items: Array<OrganizationMembership>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents the role of a organization membership. */
export enum OrganizationMembershipRole {
  Admin = 'ADMIN',
  Member = 'MEMBER',
  Owner = 'OWNER'
}

export type OrganizationPermissions = {
  __typename?: 'OrganizationPermissions';
  archiveWorkspace: Scalars['Boolean']['output'];
  createWorkspace: Scalars['Boolean']['output'];
  manageMembers: Scalars['Boolean']['output'];
  manageOwners: Scalars['Boolean']['output'];
};

/** Represents a workspace invitation within an organization invitation. */
export type OrganizationWorkspaceInvitation = {
  __typename?: 'OrganizationWorkspaceInvitation';
  role: WorkspaceMembershipRole;
  workspace: Workspace;
};

/** Represents an input parameter of a pipeline. */
export type ParameterInput = {
  choices?: InputMaybe<Array<Scalars['Generic']['input']>>;
  code: Scalars['String']['input'];
  connection?: InputMaybe<Scalars['String']['input']>;
  default?: InputMaybe<Scalars['Generic']['input']>;
  directory?: InputMaybe<Scalars['String']['input']>;
  help?: InputMaybe<Scalars['String']['input']>;
  multiple?: InputMaybe<Scalars['Boolean']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
  required?: InputMaybe<Scalars['Boolean']['input']>;
  type: Scalars['String']['input'];
  widget?: InputMaybe<ParameterWidget>;
};

/** Enum representing the type of a parameter. */
export enum ParameterType {
  Bool = 'bool',
  Custom = 'custom',
  Dataset = 'dataset',
  Dhis2 = 'dhis2',
  File = 'file',
  Float = 'float',
  Gcs = 'gcs',
  Iaso = 'iaso',
  Int = 'int',
  Postgresql = 'postgresql',
  S3 = 's3',
  Str = 'str'
}

/** Enum representing the type of a parameter widget. */
export enum ParameterWidget {
  Dhis2Datasets = 'DHIS2_DATASETS',
  Dhis2DataElements = 'DHIS2_DATA_ELEMENTS',
  Dhis2DataElementGroups = 'DHIS2_DATA_ELEMENT_GROUPS',
  Dhis2Indicators = 'DHIS2_INDICATORS',
  Dhis2IndicatorGroups = 'DHIS2_INDICATOR_GROUPS',
  Dhis2OrgUnits = 'DHIS2_ORG_UNITS',
  Dhis2OrgUnitGroups = 'DHIS2_ORG_UNIT_GROUPS',
  Dhis2OrgUnitLevels = 'DHIS2_ORG_UNIT_LEVELS',
  IasoForms = 'IASO_FORMS',
  IasoOrgUnits = 'IASO_ORG_UNITS',
  IasoProjects = 'IASO_PROJECTS'
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
  autoUpdateFromTemplate: Scalars['Boolean']['output'];
  code: Scalars['String']['output'];
  config: Scalars['JSON']['output'];
  createdAt: Scalars['DateTime']['output'];
  currentVersion?: Maybe<PipelineVersion>;
  description?: Maybe<Scalars['String']['output']>;
  functionalType?: Maybe<PipelineFunctionalType>;
  hasNewTemplateVersions: Scalars['Boolean']['output'];
  id: Scalars['UUID']['output'];
  name?: Maybe<Scalars['String']['output']>;
  newTemplateVersions: Array<PipelineTemplateVersion>;
  notebookPath?: Maybe<Scalars['String']['output']>;
  permissions: PipelinePermissions;
  recipients: Array<PipelineRecipient>;
  runs: PipelineRunPage;
  schedule?: Maybe<Scalars['String']['output']>;
  sourceTemplate?: Maybe<PipelineTemplate>;
  tags: Array<Tag>;
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
  PipelineAlreadyStopped = 'PIPELINE_ALREADY_STOPPED',
  PipelineCodeParsingError = 'PIPELINE_CODE_PARSING_ERROR',
  PipelineDoesNotSupportParameters = 'PIPELINE_DOES_NOT_SUPPORT_PARAMETERS',
  PipelineNotFound = 'PIPELINE_NOT_FOUND',
  PipelineVersionNotFound = 'PIPELINE_VERSION_NOT_FOUND',
  TableNotFound = 'TABLE_NOT_FOUND',
  WorkspaceNotFound = 'WORKSPACE_NOT_FOUND'
}

/**
 * Represents the functional purpose of a pipeline in data workflows.
 *
 * Categorizes WHAT a pipeline does in terms of business purpose:
 * - extraction: Data ingestion from external sources
 * - transformation: Data processing operations
 * - loading: Data output to destinations
 * - computation: Analytics and computational workflows
 *
 * Used for pipeline categorization, filtering, and workflow organization.
 */
export enum PipelineFunctionalType {
  Computation = 'computation',
  Extraction = 'extraction',
  Loading = 'loading',
  Transformation = 'transformation'
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
  connection?: Maybe<Scalars['String']['output']>;
  default?: Maybe<Scalars['Generic']['output']>;
  directory?: Maybe<Scalars['String']['output']>;
  help?: Maybe<Scalars['String']['output']>;
  multiple: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  required: Scalars['Boolean']['output'];
  type: ParameterType;
  widget?: Maybe<ParameterWidget>;
};

/** Represents the permissions for a pipeline. */
export type PipelinePermissions = {
  __typename?: 'PipelinePermissions';
  createTemplateVersion: CreateTemplateVersionPermission;
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

export type PipelineResult = SearchResult & {
  __typename?: 'PipelineResult';
  pipeline: Pipeline;
  score: Scalars['Float']['output'];
};

export type PipelineResultPage = {
  __typename?: 'PipelineResultPage';
  items: Array<PipelineResult>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

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
  functionalType?: Maybe<PipelineFunctionalType>;
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
  permissions: PipelineTemplatePermissions;
  sourcePipeline?: Maybe<Pipeline>;
  tags: Array<Tag>;
  updatedAt: Scalars['DateTime']['output'];
  versions: TemplateVersionPage;
  workspace?: Maybe<Workspace>;
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

export type PipelineTemplateResult = SearchResult & {
  __typename?: 'PipelineTemplateResult';
  pipelineTemplate: PipelineTemplate;
  score: Scalars['Float']['output'];
};

export type PipelineTemplateResultPage = {
  __typename?: 'PipelineTemplateResultPage';
  items: Array<PipelineTemplateResult>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents a version of a pipeline template. */
export type PipelineTemplateVersion = {
  __typename?: 'PipelineTemplateVersion';
  changelog?: Maybe<Scalars['String']['output']>;
  createdAt: Scalars['DateTime']['output'];
  id: Scalars['UUID']['output'];
  isLatestVersion: Scalars['Boolean']['output'];
  permissions: PipelineTemplateVersionPermissions;
  sourcePipelineVersion: PipelineVersion;
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

/**
 * Represents the technical implementation format of a pipeline.
 *
 * This determines HOW a pipeline is packaged and executed:
 * - zipFile: Code archive with Python modules (.zip format)
 * - notebook: Jupyter notebook-based pipeline (.ipynb format)
 */
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
  files: Array<FileNode>;
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

/** The result of preparing to upload an object to a workspace's bucket. It contains a URL that can be used to upload the object using a PUT request. */
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
  /** Get a file by its path within a workspace. */
  getFileByPath?: Maybe<BucketObject>;
  /** Retrieves the currently authenticated user. */
  me: Me;
  metadataAttributes: Array<Maybe<MetadataAttribute>>;
  notebooksUrl: Scalars['URL']['output'];
  organization?: Maybe<Organization>;
  /** Retrieves a list of organizations. */
  organizations: Array<Organization>;
  pendingWorkspaceInvitations: WorkspaceInvitationPage;
  /** Retrieves a pipeline by ID. */
  pipeline?: Maybe<Pipeline>;
  /** Retrieves a pipeline by workspace slug and code. */
  pipelineByCode?: Maybe<Pipeline>;
  /** Retrieves a pipeline run by ID. */
  pipelineRun?: Maybe<PipelineRun>;
  /** Retrieves a pipeline template version by ID. */
  pipelineTemplateVersion?: Maybe<PipelineTemplateVersion>;
  /** Retrieves a page of pipeline templates. */
  pipelineTemplates: PipelineTemplatePage;
  /** Retrieves a pipeline version by ID. */
  pipelineVersion?: Maybe<PipelineVersion>;
  /** Retrieves a page of pipelines ordered by relevant name. */
  pipelines: PipelinesPage;
  searchDatabaseTables: DatabaseTableResultPage;
  searchDatasets: DatasetResultPage;
  searchFiles: FileResultPage;
  searchPipelineTemplates: PipelineTemplateResultPage;
  searchPipelines: PipelineResultPage;
  team?: Maybe<Team>;
  teams: TeamPage;
  /** Retrieves a template by workspace slug and code. */
  templateByCode?: Maybe<PipelineTemplate>;
  /** Search users. */
  users: Array<User>;
  webapp?: Maybe<Webapp>;
  webapps: WebappsPage;
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


export type QueryGetFileByPathArgs = {
  path: Scalars['String']['input'];
  workspaceSlug: Scalars['String']['input'];
};


export type QueryMetadataAttributesArgs = {
  targetId: Scalars['OpaqueID']['input'];
};


export type QueryOrganizationArgs = {
  id: Scalars['UUID']['input'];
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


export type QueryPipelineTemplateVersionArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryPipelineTemplatesArgs = {
  functionalType?: InputMaybe<PipelineFunctionalType>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QueryPipelineVersionArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryPipelinesArgs = {
  functionalType?: InputMaybe<PipelineFunctionalType>;
  name?: InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QuerySearchDatabaseTablesArgs = {
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
  workspaceSlugs?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySearchDatasetsArgs = {
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
  workspaceSlugs?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySearchFilesArgs = {
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  prefix?: InputMaybe<Scalars['String']['input']>;
  query: Scalars['String']['input'];
  workspaceSlugs?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySearchPipelineTemplatesArgs = {
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
  workspaceSlugs?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
};


export type QuerySearchPipelinesArgs = {
  functionalType?: InputMaybe<PipelineFunctionalType>;
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query: Scalars['String']['input'];
  workspaceSlugs?: InputMaybe<Array<InputMaybe<Scalars['String']['input']>>>;
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


export type QueryUsersArgs = {
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  query: Scalars['String']['input'];
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QueryWebappArgs = {
  id: Scalars['UUID']['input'];
};


export type QueryWebappsArgs = {
  favorite?: InputMaybe<Scalars['Boolean']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
};


export type QueryWorkspaceArgs = {
  slug: Scalars['String']['input'];
};


export type QueryWorkspacesArgs = {
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
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

/** Represents the error message for removing a web app from favorites. */
export enum RemoveFromFavoritesError {
  WebappNotFound = 'WEBAPP_NOT_FOUND'
}

/** Represents the input for removing a web app from favorites. */
export type RemoveFromFavoritesInput = {
  webappId: Scalars['ID']['input'];
};

/** Represents the result of removing a web app from favorites. */
export type RemoveFromFavoritesResult = {
  __typename?: 'RemoveFromFavoritesResult';
  errors: Array<RemoveFromFavoritesError>;
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

/** The ResendOrganizationInvitationError enum represents the possible errors that can occur during the resendOrganizationInvitation mutation. */
export enum ResendOrganizationInvitationError {
  InvitationNotFound = 'INVITATION_NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The ResendOrganizationInvitationInput type represents the input for the resendOrganizationInvitation mutation. */
export type ResendOrganizationInvitationInput = {
  /** The unique identifier of the organization invitation to resend. */
  id: Scalars['UUID']['input'];
};

/** The ResendOrganizationInvitationResult type represents the result of the resendOrganizationInvitation mutation. */
export type ResendOrganizationInvitationResult = {
  __typename?: 'ResendOrganizationInvitationResult';
  errors: Array<ResendOrganizationInvitationError>;
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

export type SearchResult = {
  score: Scalars['Float']['output'];
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
  sharedWithOrganization?: InputMaybe<Scalars['Boolean']['input']>;
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

/** The UpdateOrganizationMemberError enum represents the possible errors that can occur during the updateOrganizationMember mutation. */
export enum UpdateOrganizationMemberError {
  /** Indicates that the provided role is invalid. */
  InvalidRole = 'INVALID_ROLE',
  /** Indicates that the organization membership was not found. */
  NotFound = 'NOT_FOUND',
  /** Indicates that the user does not have permission to update the organization membership. */
  PermissionDenied = 'PERMISSION_DENIED'
}

/** The UpdateOrganizationMemberInput type represents the input for the updateOrganizationMember mutation. */
export type UpdateOrganizationMemberInput = {
  /** The unique identifier of the organization membership to update. */
  id: Scalars['UUID']['input'];
  /** The updated role of the user in the organization. */
  role: OrganizationMembershipRole;
  /** The list of workspace permissions to update for the user. */
  workspacePermissions?: InputMaybe<Array<WorkspacePermissionInput>>;
};

/** The UpdateOrganizationMemberResult type represents the result of the updateOrganizationMember mutation. */
export type UpdateOrganizationMemberResult = {
  __typename?: 'UpdateOrganizationMemberResult';
  /** The list of errors that occurred during the updateOrganizationMember mutation. */
  errors: Array<UpdateOrganizationMemberError>;
  /** The updated organization membership object. */
  membership?: Maybe<OrganizationMembership>;
  /** Indicates whether the updateOrganizationMember mutation was successful. */
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
  autoUpdateFromTemplate?: InputMaybe<Scalars['Boolean']['input']>;
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  schedule?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
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
  InvalidConfig = 'INVALID_CONFIG',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a template. */
export type UpdateTemplateInput = {
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
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

/** Represents the error message for a web app update. */
export enum UpdateWebappError {
  PermissionDenied = 'PERMISSION_DENIED',
  WebappNotFound = 'WEBAPP_NOT_FOUND'
}

/** Represents the input for updating a web app. */
export type UpdateWebappInput = {
  description?: InputMaybe<Scalars['String']['input']>;
  icon?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  name?: InputMaybe<Scalars['String']['input']>;
  url?: InputMaybe<Scalars['String']['input']>;
};

/** Represents the result of updating a web app. */
export type UpdateWebappResult = {
  __typename?: 'UpdateWebappResult';
  errors: Array<UpdateWebappError>;
  success: Scalars['Boolean']['output'];
  webapp?: Maybe<Webapp>;
};

/** Enum representing the possible errors that can occur when updating a workspace. */
export enum UpdateWorkspaceError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

/** Represents the input for updating a workspace. */
export type UpdateWorkspaceInput = {
  configuration?: InputMaybe<Scalars['JSON']['input']>;
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
  /** @deprecated Use 'pipelineCode' field instead */
  code?: InputMaybe<Scalars['String']['input']>;
  config?: InputMaybe<Scalars['JSON']['input']>;
  description?: InputMaybe<Scalars['String']['input']>;
  externalLink?: InputMaybe<Scalars['URL']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
  name?: InputMaybe<Scalars['String']['input']>;
  parameters?: InputMaybe<Array<ParameterInput>>;
  pipelineCode?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']>>;
  timeout?: InputMaybe<Scalars['Int']['input']>;
  workspaceSlug: Scalars['String']['input'];
  zipfile: Scalars['String']['input'];
};

/** Represents the result of uploading a pipeline. */
export type UploadPipelineResult = {
  __typename?: 'UploadPipelineResult';
  details?: Maybe<Scalars['String']['output']>;
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

/** Represents a web app. */
export type Webapp = {
  __typename?: 'Webapp';
  createdBy: User;
  description?: Maybe<Scalars['String']['output']>;
  icon?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  isFavorite: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  permissions: WebappPermissions;
  url: Scalars['String']['output'];
  workspace: Workspace;
};

/** Represents the permissions for a web app. */
export type WebappPermissions = {
  __typename?: 'WebappPermissions';
  delete: Scalars['Boolean']['output'];
  update: Scalars['Boolean']['output'];
};

/** Represents a page of webapps. */
export type WebappsPage = {
  __typename?: 'WebappsPage';
  items: Array<Webapp>;
  pageNumber: Scalars['Int']['output'];
  totalItems: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

/** Represents a workspace. A workspace is a shared environment where users can collaborate on data projects. */
export type Workspace = {
  __typename?: 'Workspace';
  /** File storage of the workspace represented as a bucket */
  bucket: Bucket;
  configuration: Scalars['JSON']['output'];
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
  organization?: Maybe<Organization>;
  permissions: WorkspacePermissions;
  pipelineTags: Array<Scalars['String']['output']>;
  pipelineTemplateTags: Array<Scalars['String']['output']>;
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

/** The WorkspaceInvitationInput type represents a workspace invitation within an organization member invitation. */
export type WorkspaceInvitationInput = {
  /** The role of the user in the workspace. */
  role: WorkspaceMembershipRole;
  /** The name of the workspace to invite the user to. */
  workspaceName: Scalars['String']['input'];
  /** The slug of the workspace to invite the user to. */
  workspaceSlug: Scalars['String']['input'];
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
  organizationMembership?: Maybe<OrganizationMembership>;
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

/** The WorkspacePermissionInput type represents workspace permission updates for an existing organization member. */
export type WorkspacePermissionInput = {
  /** The role of the user in the workspace. If null, the user will be removed from the workspace. */
  role?: InputMaybe<WorkspaceMembershipRole>;
  /** The slug of the workspace to update permissions for. */
  workspaceSlug: Scalars['String']['input'];
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

export type UserProperty_UserFragment = (
  { __typename?: 'User' }
  & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
) & { ' $fragmentName'?: 'UserProperty_UserFragment' };

export type UserColumn_UserFragment = (
  { __typename?: 'User' }
  & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
) & { ' $fragmentName'?: 'UserColumn_UserFragment' };

export type CountryBadge_CountryFragment = { __typename?: 'Country', code: string, name: string } & { ' $fragmentName'?: 'CountryBadge_CountryFragment' };

export type CountryPickerQueryVariables = Exact<{ [key: string]: never; }>;


export type CountryPickerQuery = { __typename?: 'Query', countries: Array<(
    { __typename?: 'Country' }
    & { ' $fragmentRefs'?: { 'CountryPicker_CountryFragment': CountryPicker_CountryFragment } }
  )> };

export type CountryPicker_CountryFragment = { __typename?: 'Country', code: string, alpha3: string, name: string } & { ' $fragmentName'?: 'CountryPicker_CountryFragment' };

export type DatabaseTablesPageFragment = { __typename?: 'DatabaseTableResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatabaseTableResult', score: number, databaseTable: { __typename?: 'DatabaseTable', name: string, count?: number | null }, workspace: (
      { __typename?: 'Workspace', slug: string }
      & { ' $fragmentRefs'?: { 'WorkspaceDisplayFragmentFragment': WorkspaceDisplayFragmentFragment } }
    ) }> } & { ' $fragmentName'?: 'DatabaseTablesPageFragment' };

export type DatasetsPageFragment = { __typename?: 'DatasetResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'DatasetResult', score: number, dataset: { __typename?: 'Dataset', id: string, slug: string, name: string, description?: string | null, updatedAt: any, workspace?: (
        { __typename?: 'Workspace', slug: string }
        & { ' $fragmentRefs'?: { 'WorkspaceDisplayFragmentFragment': WorkspaceDisplayFragmentFragment } }
      ) | null, createdBy?: (
        { __typename?: 'User', id: string, displayName: string }
        & { ' $fragmentRefs'?: { 'UserAvatar_UserFragment': UserAvatar_UserFragment } }
      ) | null } }> } & { ' $fragmentName'?: 'DatasetsPageFragment' };

export type FilesPageFragment = { __typename?: 'FileResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'FileResult', score: number, file: { __typename?: 'File', name: string, path: string, size?: any | null, updatedAt?: any | null, type: FileType }, workspace: (
      { __typename?: 'Workspace', slug: string }
      & { ' $fragmentRefs'?: { 'WorkspaceDisplayFragmentFragment': WorkspaceDisplayFragmentFragment } }
    ) }> } & { ' $fragmentName'?: 'FilesPageFragment' };

export type PipelinesPageFragment = { __typename?: 'PipelineResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'PipelineResult', score: number, pipeline: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, description?: string | null, updatedAt?: any | null, functionalType?: PipelineFunctionalType | null, tags: Array<(
        { __typename?: 'Tag' }
        & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
      )>, workspace: (
        { __typename?: 'Workspace', slug: string }
        & { ' $fragmentRefs'?: { 'WorkspaceDisplayFragmentFragment': WorkspaceDisplayFragmentFragment } }
      ), lastRuns: { __typename?: 'PipelineRunPage', items: Array<(
          { __typename?: 'PipelineRun' }
          & { ' $fragmentRefs'?: { 'PipelineRunStatusBadge_RunFragment': PipelineRunStatusBadge_RunFragment } }
        )> } } }> } & { ' $fragmentName'?: 'PipelinesPageFragment' };

export type PipelineTemplatesPageFragment = { __typename?: 'PipelineTemplateResultPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<{ __typename?: 'PipelineTemplateResult', score: number, pipelineTemplate: { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, updatedAt: any, workspace?: (
        { __typename?: 'Workspace', slug: string }
        & { ' $fragmentRefs'?: { 'WorkspaceDisplayFragmentFragment': WorkspaceDisplayFragmentFragment } }
      ) | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number } | null } }> } & { ' $fragmentName'?: 'PipelineTemplatesPageFragment' };

export type GetWorkspacesQueryVariables = Exact<{
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetWorkspacesQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<(
      { __typename?: 'Workspace', slug: string }
      & { ' $fragmentRefs'?: { 'WorkspaceDisplayFragmentFragment': WorkspaceDisplayFragmentFragment } }
    )> } };

export type SearchFilesQueryVariables = Exact<{
  query: Scalars['String']['input'];
  workspaceSlugs: Array<InputMaybe<Scalars['String']['input']>> | InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchFilesQuery = { __typename?: 'Query', files: (
    { __typename: 'FileResultPage' }
    & { ' $fragmentRefs'?: { 'FilesPageFragment': FilesPageFragment } }
  ) };

export type SearchPipelineTemplatesQueryVariables = Exact<{
  query: Scalars['String']['input'];
  workspaceSlugs: Array<InputMaybe<Scalars['String']['input']>> | InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchPipelineTemplatesQuery = { __typename?: 'Query', pipelineTemplates: (
    { __typename: 'PipelineTemplateResultPage' }
    & { ' $fragmentRefs'?: { 'PipelineTemplatesPageFragment': PipelineTemplatesPageFragment } }
  ) };

export type SearchPipelinesQueryVariables = Exact<{
  query: Scalars['String']['input'];
  workspaceSlugs: Array<InputMaybe<Scalars['String']['input']>> | InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
}>;


export type SearchPipelinesQuery = { __typename?: 'Query', pipelines: (
    { __typename: 'PipelineResultPage' }
    & { ' $fragmentRefs'?: { 'PipelinesPageFragment': PipelinesPageFragment } }
  ) };

export type SearchDatasetsQueryVariables = Exact<{
  query: Scalars['String']['input'];
  workspaceSlugs: Array<InputMaybe<Scalars['String']['input']>> | InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchDatasetsQuery = { __typename?: 'Query', datasets: (
    { __typename: 'DatasetResultPage' }
    & { ' $fragmentRefs'?: { 'DatasetsPageFragment': DatasetsPageFragment } }
  ) };

export type SearchDatabaseTablesQueryVariables = Exact<{
  query: Scalars['String']['input'];
  workspaceSlugs: Array<InputMaybe<Scalars['String']['input']>> | InputMaybe<Scalars['String']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SearchDatabaseTablesQuery = { __typename?: 'Query', databaseTables: (
    { __typename: 'DatabaseTableResultPage' }
    & { ' $fragmentRefs'?: { 'DatabaseTablesPageFragment': DatabaseTablesPageFragment } }
  ) };

export type WorkspaceDisplayFragmentFragment = { __typename?: 'Workspace', name: string, countries: Array<{ __typename?: 'Country', code: string }> } & { ' $fragmentName'?: 'WorkspaceDisplayFragmentFragment' };

export type Tag_TagFragment = { __typename?: 'Tag', id: string, name: string } & { ' $fragmentName'?: 'Tag_TagFragment' };

export type User_UserFragment = (
  { __typename?: 'User', id: string, email: string, displayName: string }
  & { ' $fragmentRefs'?: { 'UserAvatar_UserFragment': UserAvatar_UserFragment } }
) & { ' $fragmentName'?: 'User_UserFragment' };

export type ColumnMetadataDrawer_FileFragment = { __typename?: 'DatasetVersionFile', id: string, targetId: any, properties?: any | null, attributes: Array<{ __typename: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean }> } & { ' $fragmentName'?: 'ColumnMetadataDrawer_FileFragment' };

export type CreateDatasetDialogMutationVariables = Exact<{
  input: CreateDatasetInput;
}>;


export type CreateDatasetDialogMutation = { __typename?: 'Mutation', createDataset: { __typename?: 'CreateDatasetResult', success: boolean, errors: Array<CreateDatasetError>, dataset?: { __typename?: 'Dataset', id: string, slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null } | null, link?: { __typename?: 'DatasetLink', id: string } | null } };

export type CreateDatasetDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', createDataset: boolean } } & { ' $fragmentName'?: 'CreateDatasetDialog_WorkspaceFragment' };

export type DatasetCard_LinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', name: string, slug: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null }, workspace: { __typename?: 'Workspace', slug: string, name: string } } & { ' $fragmentName'?: 'DatasetCard_LinkFragment' };

export type DatasetExplorer_VersionFragment = (
  { __typename?: 'DatasetVersion', id: string, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, pageNumber: number, totalItems: number, items: Array<(
      { __typename?: 'DatasetVersionFile' }
      & { ' $fragmentRefs'?: { 'DatasetExplorer_FileFragment': DatasetExplorer_FileFragment } }
    )> } }
  & { ' $fragmentRefs'?: { 'DatasetVersionFileSample_VersionFragment': DatasetVersionFileSample_VersionFragment;'DatasetVersionFileColumns_VersionFragment': DatasetVersionFileColumns_VersionFragment } }
) & { ' $fragmentName'?: 'DatasetExplorer_VersionFragment' };

export type DatasetExplorer_FileFragment = (
  { __typename?: 'DatasetVersionFile', id: string, filename: string, createdAt: any, contentType: string, size: any, uri: string, createdBy?: { __typename?: 'User', displayName: string } | null }
  & { ' $fragmentRefs'?: { 'DownloadVersionFile_FileFragment': DownloadVersionFile_FileFragment;'DatasetVersionFileSample_FileFragment': DatasetVersionFileSample_FileFragment;'DatasetVersionFileColumns_FileFragment': DatasetVersionFileColumns_FileFragment } }
) & { ' $fragmentName'?: 'DatasetExplorer_FileFragment' };

export type DatasetLinksDataGridQueryVariables = Exact<{
  datasetId: Scalars['ID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
}>;


export type DatasetLinksDataGridQuery = { __typename?: 'Query', dataset?: { __typename?: 'Dataset', links: { __typename?: 'DatasetLinkPage', totalItems: number, items: Array<(
        { __typename?: 'DatasetLink', createdAt: any, permissions: { __typename?: 'DatasetLinkPermissions', delete: boolean }, workspace: { __typename?: 'Workspace', slug: string, name: string }, createdBy?: { __typename?: 'User', displayName: string } | null }
        & { ' $fragmentRefs'?: { 'DeleteDatasetLinkTrigger_DatasetLinkFragment': DeleteDatasetLinkTrigger_DatasetLinkFragment } }
      )> } } | null };

export type DatasetLinksDataGrid_DatasetFragment = { __typename?: 'Dataset', id: string, name: string } & { ' $fragmentName'?: 'DatasetLinksDataGrid_DatasetFragment' };

export type DatasetPickerQueryVariables = Exact<{
  slug: Scalars['String']['input'];
}>;


export type DatasetPickerQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string }
    & { ' $fragmentRefs'?: { 'DatasetPicker_WorkspaceFragment': DatasetPicker_WorkspaceFragment } }
  ) | null };

export type DatasetPicker_WorkspaceFragment = { __typename?: 'Workspace', datasets: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', slug: string, name: string } }> } } & { ' $fragmentName'?: 'DatasetPicker_WorkspaceFragment' };

export type DatasetVersionFileColumns_FileFragment = (
  { __typename?: 'DatasetVersionFile', id: string, filename: string }
  & { ' $fragmentRefs'?: { 'ColumnMetadataDrawer_FileFragment': ColumnMetadataDrawer_FileFragment } }
) & { ' $fragmentName'?: 'DatasetVersionFileColumns_FileFragment' };

export type DatasetVersionFileColumns_VersionFragment = { __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, permissions: { __typename?: 'DatasetPermissions', update: boolean }, workspace?: { __typename?: 'Workspace', slug: string } | null } } & { ' $fragmentName'?: 'DatasetVersionFileColumns_VersionFragment' };

export type GetDatasetVersionFileSampleQueryVariables = Exact<{
  id: Scalars['ID']['input'];
}>;


export type GetDatasetVersionFileSampleQuery = { __typename?: 'Query', datasetVersionFile?: { __typename?: 'DatasetVersionFile', id: string, properties?: any | null, fileSample?: { __typename?: 'DatasetFileSample', sample?: any | null, status: FileSampleStatus, statusReason?: string | null } | null } | null };

export type DatasetVersionFileSample_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string, contentType: string, size: any, downloadUrl?: string | null } & { ' $fragmentName'?: 'DatasetVersionFileSample_FileFragment' };

export type DatasetVersionFileSample_VersionFragment = { __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null } } & { ' $fragmentName'?: 'DatasetVersionFileSample_VersionFragment' };

export type DatasetVersionFilesDataGridQueryVariables = Exact<{
  versionId: Scalars['ID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage: Scalars['Int']['input'];
}>;


export type DatasetVersionFilesDataGridQuery = { __typename?: 'Query', datasetVersion?: { __typename?: 'DatasetVersion', id: string, files: { __typename?: 'DatasetVersionFilePage', totalPages: number, totalItems: number, pageNumber: number, items: Array<(
        { __typename?: 'DatasetVersionFile', id: string, contentType: string, createdAt: any, uri: string, filename: string }
        & { ' $fragmentRefs'?: { 'DownloadVersionFile_FileFragment': DownloadVersionFile_FileFragment } }
      )> } } | null };

export type DatasetVersionFilesDataGrid_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, permissions: { __typename?: 'DatasetVersionPermissions', download: boolean } } & { ' $fragmentName'?: 'DatasetVersionFilesDataGrid_VersionFragment' };

export type DatasetVersionPickerQueryVariables = Exact<{
  datasetId: Scalars['ID']['input'];
  perPage: Scalars['Int']['input'];
}>;


export type DatasetVersionPickerQuery = { __typename?: 'Query', dataset?: { __typename?: 'Dataset', versions: { __typename?: 'DatasetVersionPage', totalItems: number, items: Array<(
        { __typename?: 'DatasetVersion' }
        & { ' $fragmentRefs'?: { 'DatasetVersionPicker_VersionFragment': DatasetVersionPicker_VersionFragment } }
      )> } } | null };

export type DatasetVersionPicker_VersionFragment = { __typename?: 'DatasetVersion', id: string, name: string, createdAt: any } & { ' $fragmentName'?: 'DatasetVersionPicker_VersionFragment' };

export type DatasetVersionPicker_DatasetFragment = { __typename?: 'Dataset', id: string } & { ' $fragmentName'?: 'DatasetVersionPicker_DatasetFragment' };

export type DeleteDatasetLinkTrigger_DatasetLinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', name: string, id: string }, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'DatasetLinkPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteDatasetLinkTrigger_DatasetLinkFragment' };

export type DeleteDatasetTrigger_DatasetFragment = { __typename?: 'Dataset', id: string, name: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteDatasetTrigger_DatasetFragment' };

export type DownloadVersionFile_FileFragment = { __typename?: 'DatasetVersionFile', id: string, filename: string } & { ' $fragmentName'?: 'DownloadVersionFile_FileFragment' };

export type LinkDatasetDialogMutationVariables = Exact<{
  input: LinkDatasetInput;
}>;


export type LinkDatasetDialogMutation = { __typename?: 'Mutation', linkDataset: { __typename?: 'LinkDatasetResult', success: boolean, errors: Array<LinkDatasetError>, link?: { __typename?: 'DatasetLink', id: string, workspace: { __typename?: 'Workspace', slug: string } } | null } };

export type LinkDatasetDialog_DatasetFragment = { __typename?: 'Dataset', id: string, name: string } & { ' $fragmentName'?: 'LinkDatasetDialog_DatasetFragment' };

export type PinDatasetButtonMutationVariables = Exact<{
  input: PinDatasetInput;
}>;


export type PinDatasetButtonMutation = { __typename?: 'Mutation', pinDataset: { __typename?: 'PinDatasetResult', success: boolean, errors: Array<PinDatasetError>, link?: { __typename?: 'DatasetLink', id: string, isPinned: boolean } | null } };

export type PinDatasetButton_LinkFragment = { __typename?: 'DatasetLink', id: string, isPinned: boolean, permissions: { __typename?: 'DatasetLinkPermissions', pin: boolean } } & { ' $fragmentName'?: 'PinDatasetButton_LinkFragment' };

export type UploadDatasetVersionDialog_DatasetLinkFragment = { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', id: string, name: string, slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null }, workspace: { __typename?: 'Workspace', slug: string } } & { ' $fragmentName'?: 'UploadDatasetVersionDialog_DatasetLinkFragment' };

export type UpdateDatasetMutationVariables = Exact<{
  input: UpdateDatasetInput;
}>;


export type UpdateDatasetMutation = { __typename?: 'Mutation', updateDataset: { __typename?: 'UpdateDatasetResult', success: boolean, errors: Array<UpdateDatasetError>, dataset?: { __typename?: 'Dataset', id: string, name: string, description?: string | null, sharedWithOrganization: boolean, updatedAt: any } | null } };

export type UpdateDatasetVersionMutationVariables = Exact<{
  input: UpdateDatasetVersionInput;
}>;


export type UpdateDatasetVersionMutation = { __typename?: 'Mutation', updateDatasetVersion: { __typename?: 'UpdateDatasetVersionResult', success: boolean, errors: Array<UpdateDatasetVersionError>, version?: { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null } | null } };

export type CreateDatasetVersionMutationVariables = Exact<{
  input: CreateDatasetVersionInput;
}>;


export type CreateDatasetVersionMutation = { __typename?: 'Mutation', createDatasetVersion: { __typename?: 'CreateDatasetVersionResult', success: boolean, errors: Array<CreateDatasetVersionError>, version?: { __typename?: 'DatasetVersion', id: string, name: string, changelog?: string | null } | null } };

export type GenerateDatasetUploadUrlMutationVariables = Exact<{
  input: GenerateDatasetUploadUrlInput;
}>;


export type GenerateDatasetUploadUrlMutation = { __typename?: 'Mutation', generateDatasetUploadUrl: { __typename?: 'GenerateDatasetUploadUrlResult', success: boolean, errors: Array<CreateDatasetVersionFileError>, uploadUrl?: string | null } };

export type PrepareVersionFileDownloadMutationVariables = Exact<{
  input: PrepareVersionFileDownloadInput;
}>;


export type PrepareVersionFileDownloadMutation = { __typename?: 'Mutation', prepareVersionFileDownload: { __typename?: 'PrepareVersionFileDownloadResult', success: boolean, downloadUrl?: string | null, errors: Array<PrepareVersionFileDownloadError> } };

export type CreateDatasetVersionFileMutationVariables = Exact<{
  input: CreateDatasetVersionFileInput;
}>;


export type CreateDatasetVersionFileMutation = { __typename?: 'Mutation', createDatasetVersionFile: { __typename?: 'CreateDatasetVersionFileResult', success: boolean, errors: Array<CreateDatasetVersionFileError>, file?: { __typename?: 'DatasetVersionFile', id: string, uri: string } | null } };

export type DeleteDatasetLinkMutationVariables = Exact<{
  input: DeleteDatasetLinkInput;
}>;


export type DeleteDatasetLinkMutation = { __typename?: 'Mutation', deleteDatasetLink: { __typename?: 'DeleteDatasetLinkResult', success: boolean, errors: Array<DeleteDatasetLinkError> } };

export type DeleteDatasetMutationVariables = Exact<{
  input: DeleteDatasetInput;
}>;


export type DeleteDatasetMutation = { __typename?: 'Mutation', deleteDataset: { __typename?: 'DeleteDatasetResult', success: boolean, errors: Array<DeleteDatasetError> } };

export type SetMetadataAttributeMutationVariables = Exact<{
  input: SetMetadataAttributeInput;
}>;


export type SetMetadataAttributeMutation = { __typename?: 'Mutation', setMetadataAttribute: { __typename?: 'SetMetadataAttributeResult', success: boolean, errors: Array<SetMetadataAttributeError>, attribute?: { __typename?: 'MetadataAttribute', id: string, key: string, label?: string | null, value?: any | null, system: boolean } | null } };

export type DeleteMetadataAttributeMutationVariables = Exact<{
  input: DeleteMetadataAttributeInput;
}>;


export type DeleteMetadataAttributeMutation = { __typename?: 'Mutation', deleteMetadataAttribute: { __typename?: 'DeleteMetadataAttributeResult', success: boolean, errors: Array<DeleteMetadataAttributeError> } };

export type TabularFileMetadataQueryVariables = Exact<{
  fileId: Scalars['ID']['input'];
}>;


export type TabularFileMetadataQuery = { __typename?: 'Query', datasetVersionFile?: { __typename?: 'DatasetVersionFile', properties?: any | null, id: string, targetId: any, attributes: Array<{ __typename?: 'MetadataAttribute', id: string, key: string, value?: any | null, label?: string | null, system: boolean, createdAt: any, updatedAt: any, createdBy?: { __typename?: 'User', displayName: string } | null, updatedBy?: { __typename?: 'User', displayName: string } | null }> } | null };

export type DatasetLayout_WorkspaceFragment = (
  { __typename?: 'Workspace', name: string, slug: string }
  & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
) & { ' $fragmentName'?: 'DatasetLayout_WorkspaceFragment' };

export type DatasetLayout_DatasetLinkFragment = (
  { __typename?: 'DatasetLink', dataset: { __typename?: 'Dataset', slug: string, workspace?: { __typename?: 'Workspace', slug: string } | null, permissions: { __typename?: 'DatasetPermissions', delete: boolean, createVersion: boolean } } }
  & { ' $fragmentRefs'?: { 'UploadDatasetVersionDialog_DatasetLinkFragment': UploadDatasetVersionDialog_DatasetLinkFragment;'PinDatasetButton_LinkFragment': PinDatasetButton_LinkFragment } }
) & { ' $fragmentName'?: 'DatasetLayout_DatasetLinkFragment' };

export type DatasetLayout_VersionFragment = (
  { __typename?: 'DatasetVersion', id: string, name: string }
  & { ' $fragmentRefs'?: { 'DatasetVersionPicker_VersionFragment': DatasetVersionPicker_VersionFragment } }
) & { ' $fragmentName'?: 'DatasetLayout_VersionFragment' };

export type UpdateUserMutationVariables = Exact<{
  input: UpdateUserInput;
}>;


export type UpdateUserMutation = { __typename?: 'Mutation', updateUser: { __typename?: 'UpdateUserResult', success: boolean, errors: Array<UpdateUserError>, user?: { __typename?: 'User', id: string, language: string, firstName?: string | null, lastName?: string | null } | null } };

export type UserAvatar_UserFragment = { __typename?: 'User', displayName: string, avatar: { __typename?: 'Avatar', initials: string, color: string } } & { ' $fragmentName'?: 'UserAvatar_UserFragment' };

export type ResetPasswordMutationVariables = Exact<{
  input: ResetPasswordInput;
}>;


export type ResetPasswordMutation = { __typename?: 'Mutation', resetPassword: { __typename?: 'ResetPasswordResult', success: boolean } };

export type SetPasswordMutationVariables = Exact<{
  input: SetPasswordInput;
}>;


export type SetPasswordMutation = { __typename?: 'Mutation', setPassword: { __typename?: 'SetPasswordResult', success: boolean, error?: SetPasswordError | null } };

export type LoginMutationVariables = Exact<{
  input: LoginInput;
}>;


export type LoginMutation = { __typename?: 'Mutation', login: { __typename?: 'LoginResult', success: boolean, errors?: Array<LoginError> | null } };

export type LogoutMutationVariables = Exact<{ [key: string]: never; }>;


export type LogoutMutation = { __typename?: 'Mutation', logout: { __typename?: 'LogoutResult', success: boolean } };

export type RegisterMutationVariables = Exact<{
  input: RegisterInput;
}>;


export type RegisterMutation = { __typename?: 'Mutation', register: { __typename?: 'RegisterResult', success: boolean, errors?: Array<RegisterError> | null } };

export type GenerateChallengeMutationVariables = Exact<{ [key: string]: never; }>;


export type GenerateChallengeMutation = { __typename?: 'Mutation', generateChallenge: { __typename?: 'GenerateChallengeResult', success: boolean, errors?: Array<GenerateChallengeError> | null } };

export type VerifyDeviceMutationVariables = Exact<{
  input: VerifyDeviceInput;
}>;


export type VerifyDeviceMutation = { __typename?: 'Mutation', verifyDevice: { __typename?: 'VerifyDeviceResult', success: boolean, errors?: Array<VerifyDeviceError> | null } };

export type DisableTwoFactorMutationVariables = Exact<{
  input: DisableTwoFactorInput;
}>;


export type DisableTwoFactorMutation = { __typename?: 'Mutation', disableTwoFactor: { __typename?: 'DisableTwoFactorResult', success: boolean, errors?: Array<DisableTwoFactorError> | null } };

export type EnableTwoFactorMutationVariables = Exact<{ [key: string]: never; }>;


export type EnableTwoFactorMutation = { __typename?: 'Mutation', enableTwoFactor: { __typename?: 'EnableTwoFactorResult', success: boolean, verified?: boolean | null, errors?: Array<EnableTwoFactorError> | null } };

export type GetUserQueryVariables = Exact<{ [key: string]: never; }>;


export type GetUserQuery = { __typename?: 'Query', me: { __typename?: 'Me', hasTwoFactorEnabled: boolean, permissions: { __typename?: 'MePermissions', adminPanel: boolean, superUser: boolean, createWorkspace: boolean }, features: Array<{ __typename?: 'FeatureFlag', code: string }>, user?: (
      { __typename?: 'User', email: string, id: string, firstName?: string | null, lastName?: string | null, displayName: string, language: string, avatar: { __typename?: 'Avatar', initials: string, color: string } }
      & { ' $fragmentRefs'?: { 'UserAvatar_UserFragment': UserAvatar_UserFragment } }
    ) | null } };

export type AccountPageQueryVariables = Exact<{ [key: string]: never; }>;


export type AccountPageQuery = { __typename?: 'Query', me: { __typename?: 'Me', hasTwoFactorEnabled: boolean, user?: (
      { __typename?: 'User', firstName?: string | null, lastName?: string | null, dateJoined: any, displayName: string, id: string, email: string, language: string }
      & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
    ) | null }, pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, status: WorkspaceInvitationStatus, role: WorkspaceMembershipRole, createdAt: any, invitedBy?: (
        { __typename?: 'User' }
        & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
      ) | null, workspace: { __typename?: 'Workspace', slug: string, name: string } }> } };

export type RegisterPageQueryVariables = Exact<{ [key: string]: never; }>;


export type RegisterPageQuery = { __typename?: 'Query', config: { __typename?: 'Config', passwordRequirements?: Array<string> | null } };

export type NotebooksPageQueryVariables = Exact<{ [key: string]: never; }>;


export type NotebooksPageQuery = { __typename?: 'Query', notebooksUrl: any };

export type WorkspaceRoleFragment = { __typename?: 'WorkspaceMembership', role: WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', name: string, slug: string } } & { ' $fragmentName'?: 'WorkspaceRoleFragment' };

export type OrganizationDatasetsQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
}>;


export type OrganizationDatasetsQuery = { __typename?: 'Query', organization?: (
    { __typename?: 'Organization', datasetLinks: { __typename?: 'DatasetLinkPage', totalItems: number, pageNumber: number, totalPages: number, items: Array<(
        { __typename?: 'DatasetLink' }
        & { ' $fragmentRefs'?: { 'OrganizationDataset_LinkFragment': OrganizationDataset_LinkFragment } }
      )> } }
    & { ' $fragmentRefs'?: { 'Organization_OrganizationFragment': Organization_OrganizationFragment } }
  ) | null };

export type DeleteOrganizationInvitationMutationVariables = Exact<{
  input: DeleteOrganizationInvitationInput;
}>;


export type DeleteOrganizationInvitationMutation = { __typename?: 'Mutation', deleteOrganizationInvitation: { __typename?: 'DeleteOrganizationInvitationResult', success: boolean, errors: Array<DeleteOrganizationInvitationError> } };

export type OrganizationInvitationsQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type OrganizationInvitationsQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean }, invitations: { __typename?: 'OrganizationInvitationPage', totalItems: number, items: Array<{ __typename?: 'OrganizationInvitation', id: string, role: OrganizationMembershipRole, email: string, status: OrganizationInvitationStatus, createdAt: any, invitedBy?: { __typename?: 'User', displayName: string } | null, workspaceInvitations: Array<{ __typename?: 'OrganizationWorkspaceInvitation', role: WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', name: string, slug: string } }> }> } } | null };

export type ResendOrganizationInvitationMutationVariables = Exact<{
  input: ResendOrganizationInvitationInput;
}>;


export type ResendOrganizationInvitationMutation = { __typename?: 'Mutation', resendOrganizationInvitation: { __typename?: 'ResendOrganizationInvitationResult', success: boolean, errors: Array<ResendOrganizationInvitationError> } };

export type InviteOrganizationMemberMutationVariables = Exact<{
  input: InviteOrganizationMemberInput;
}>;


export type InviteOrganizationMemberMutation = { __typename?: 'Mutation', inviteOrganizationMember: { __typename?: 'InviteOrganizationMemberResult', success: boolean, errors: Array<InviteOrganizationMemberError> } };

export type DeleteOrganizationMemberMutationVariables = Exact<{
  input: DeleteOrganizationMemberInput;
}>;


export type DeleteOrganizationMemberMutation = { __typename?: 'Mutation', deleteOrganizationMember: { __typename?: 'DeleteOrganizationMemberResult', success: boolean, errors: Array<DeleteOrganizationMemberError> } };

export type OrganizationMembersQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  term?: InputMaybe<Scalars['String']['input']>;
  role?: InputMaybe<OrganizationMembershipRole>;
}>;


export type OrganizationMembersQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean, manageOwners: boolean }, workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string, name: string }> }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number, items: Array<{ __typename?: 'OrganizationMembership', id: string, role: OrganizationMembershipRole, createdAt: any, workspaceMemberships: Array<(
          { __typename?: 'WorkspaceMembership', id: string, role: WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }
          & { ' $fragmentRefs'?: { 'WorkspaceRoleFragment': WorkspaceRoleFragment } }
        )>, user: (
          { __typename?: 'User' }
          & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
        ) }> } } | null };

export type UpdateOrganizationMemberMutationVariables = Exact<{
  input: UpdateOrganizationMemberInput;
}>;


export type UpdateOrganizationMemberMutation = { __typename?: 'Mutation', updateOrganizationMember: { __typename?: 'UpdateOrganizationMemberResult', success: boolean, errors: Array<UpdateOrganizationMemberError>, membership?: { __typename?: 'OrganizationMembership', id: string, role: OrganizationMembershipRole } | null } };

export type UpdateOrganizationMemberDialog_OrganizationMemberFragment = { __typename?: 'OrganizationMembership', id: string, role: OrganizationMembershipRole, workspaceMemberships: Array<{ __typename?: 'WorkspaceMembership', id: string, role: WorkspaceMembershipRole, workspace: { __typename?: 'Workspace', slug: string, name: string } }>, user: { __typename?: 'User', id: string, displayName: string, email: string } } & { ' $fragmentName'?: 'UpdateOrganizationMemberDialog_OrganizationMemberFragment' };

export type UpdateOrganizationMemberDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string } & { ' $fragmentName'?: 'UpdateOrganizationMemberDialog_WorkspaceFragment' };

export type OrganizationWorkspaceInvitationsQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type OrganizationWorkspaceInvitationsQuery = { __typename?: 'Query', organization?: { __typename?: 'Organization', id: string, permissions: { __typename?: 'OrganizationPermissions', manageMembers: boolean }, pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, email: string, role: WorkspaceMembershipRole, status: WorkspaceInvitationStatus, createdAt: any, workspace: { __typename?: 'Workspace', name: string, slug: string }, invitedBy?: { __typename?: 'User', displayName: string } | null }> } } | null };

export type DeleteWorkspaceInvitationMutationVariables = Exact<{
  input: DeleteWorkspaceInvitationInput;
}>;


export type DeleteWorkspaceInvitationMutation = { __typename?: 'Mutation', deleteWorkspaceInvitation: { __typename?: 'DeleteWorkspaceInvitationResult', success: boolean, errors: Array<DeleteWorkspaceInvitationError> } };

export type ResendWorkspaceInvitationMutationVariables = Exact<{
  input: ResendWorkspaceInvitationInput;
}>;


export type ResendWorkspaceInvitationMutation = { __typename?: 'Mutation', resendWorkspaceInvitation: { __typename?: 'ResendWorkspaceInvitationResult', success: boolean, errors: Array<ResendWorkspaceInvitationError> } };

export type Organization_OrganizationFragment = { __typename?: 'Organization', id: string, name: string, shortName?: string | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string }> }> }, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean, archiveWorkspace: boolean, manageMembers: boolean, manageOwners: boolean }, members: { __typename?: 'OrganizationMembershipPage', totalItems: number } } & { ' $fragmentName'?: 'Organization_OrganizationFragment' };

export type OrganizationQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
}>;


export type OrganizationQuery = { __typename?: 'Query', organization?: (
    { __typename?: 'Organization' }
    & { ' $fragmentRefs'?: { 'Organization_OrganizationFragment': Organization_OrganizationFragment } }
  ) | null };

export type OrganizationsQueryVariables = Exact<{ [key: string]: never; }>;


export type OrganizationsQuery = { __typename?: 'Query', organizations: Array<{ __typename?: 'Organization', id: string, name: string, workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string, name: string }> } }> };

export type OrganizationDataset_LinkFragment = { __typename?: 'DatasetLink', id: string, workspace: { __typename?: 'Workspace', slug: string, name: string }, dataset: { __typename?: 'Dataset', id: string, slug: string, name: string, description?: string | null, updatedAt: any, sharedWithOrganization: boolean, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null, links: { __typename?: 'DatasetLinkPage', items: Array<{ __typename?: 'DatasetLink', workspace: { __typename?: 'Workspace', slug: string, name: string } }> } } } & { ' $fragmentName'?: 'OrganizationDataset_LinkFragment' };

export type OrganizationWorkspace_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, createdAt: any, updatedAt?: any | null, countries: Array<{ __typename?: 'Country', code: string }>, createdBy: (
    { __typename?: 'User' }
    & { ' $fragmentRefs'?: { 'UserAvatar_UserFragment': UserAvatar_UserFragment } }
  ), members: { __typename?: 'WorkspaceMembershipPage', totalItems: number }, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, delete: boolean } } & { ' $fragmentName'?: 'OrganizationWorkspace_WorkspaceFragment' };

export type OrganizationWorkspacesQueryVariables = Exact<{
  organizationId: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
}>;


export type OrganizationWorkspacesQuery = { __typename?: 'Query', organization?: (
    { __typename?: 'Organization' }
    & { ' $fragmentRefs'?: { 'Organization_OrganizationFragment': Organization_OrganizationFragment } }
  ) | null, workspaces: { __typename?: 'WorkspacePage', totalItems: number, pageNumber: number, totalPages: number, items: Array<(
      { __typename?: 'Workspace' }
      & { ' $fragmentRefs'?: { 'OrganizationWorkspace_WorkspaceFragment': OrganizationWorkspace_WorkspaceFragment } }
    )> } };

export type PipelinePageQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type PipelinePageQuery = { __typename?: 'Query', dag?: { __typename?: 'DAG', id: string, label: string, externalId: string, schedule?: string | null, externalUrl?: any | null, description?: string | null, countries: Array<(
      { __typename?: 'Country' }
      & { ' $fragmentRefs'?: { 'CountryBadge_CountryFragment': CountryBadge_CountryFragment } }
    )>, tags: Array<(
      { __typename?: 'Tag' }
      & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
    )>, template: { __typename?: 'DAGTemplate', code: string, description?: string | null, sampleConfig?: any | null }, user?: (
      { __typename?: 'User' }
      & { ' $fragmentRefs'?: { 'UserProperty_UserFragment': UserProperty_UserFragment } }
    ) | null, runs: { __typename?: 'DAGRunPage', totalItems: number, totalPages: number, items: Array<(
        { __typename?: 'DAGRun', id: string, label?: string | null, triggerMode?: DagRunTrigger | null, externalId?: string | null, externalUrl?: any | null, status: DagRunStatus, executionDate?: any | null, lastRefreshedAt?: any | null, duration?: number | null, user?: (
          { __typename?: 'User' }
          & { ' $fragmentRefs'?: { 'UserColumn_UserFragment': UserColumn_UserFragment } }
        ) | null }
        & { ' $fragmentRefs'?: { 'PipelineRunFavoriteTrigger_RunFragment': PipelineRunFavoriteTrigger_RunFragment } }
      )> } } | null };

export type UpdatePipelineMutationVariables = Exact<{
  input: UpdatePipelineInput;
}>;


export type UpdatePipelineMutation = { __typename?: 'Mutation', updatePipeline: { __typename?: 'UpdatePipelineResult', success: boolean, errors: Array<UpdatePipelineError>, pipeline?: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, description?: string | null, schedule?: string | null, webhookEnabled: boolean, autoUpdateFromTemplate: boolean } | null } };

export type PipelineConfigureRunPageQueryVariables = Exact<{
  pipelineId: Scalars['UUID']['input'];
}>;


export type PipelineConfigureRunPageQuery = { __typename?: 'Query', dag?: (
    { __typename?: 'DAG', id: string, label: string, externalId: string, description?: string | null, template: { __typename?: 'DAGTemplate', sampleConfig?: any | null, description?: string | null } }
    & { ' $fragmentRefs'?: { 'PipelineRunForm_DagFragment': PipelineRunForm_DagFragment } }
  ) | null };

export type PipelineRunPageQueryVariables = Exact<{
  pipelineId: Scalars['UUID']['input'];
  runId: Scalars['UUID']['input'];
}>;


export type PipelineRunPageQuery = { __typename?: 'Query', dagRun?: (
    { __typename?: 'DAGRun', id: string, label?: string | null, triggerMode?: DagRunTrigger | null, user?: { __typename?: 'User', displayName: string } | null }
    & { ' $fragmentRefs'?: { 'PipelineRunDataCard_DagRunFragment': PipelineRunDataCard_DagRunFragment } }
  ) | null, dag?: (
    { __typename?: 'DAG', id: string, externalId: string, label: string }
    & { ' $fragmentRefs'?: { 'PipelineRunDataCard_DagFragment': PipelineRunDataCard_DagFragment } }
  ) | null };

export type PipelinesPageQueryVariables = Exact<{
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type PipelinesPageQuery = { __typename?: 'Query', dags: { __typename?: 'DAGPage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'DAG', label: string, id: string, externalId: string, countries: Array<(
        { __typename?: 'Country' }
        & { ' $fragmentRefs'?: { 'CountryBadge_CountryFragment': CountryBadge_CountryFragment } }
      )>, tags: Array<(
        { __typename?: 'Tag' }
        & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
      )>, runs: { __typename?: 'DAGRunPage', items: Array<{ __typename?: 'DAGRun', id: string, status: DagRunStatus, executionDate?: any | null }> } }> } };

export type JoinWorkspaceMutationVariables = Exact<{
  input: JoinWorkspaceInput;
}>;


export type JoinWorkspaceMutation = { __typename?: 'Mutation', joinWorkspace: { __typename?: 'JoinWorkspaceResult', success: boolean, errors: Array<JoinWorkspaceError>, invitation?: { __typename?: 'WorkspaceInvitation', id: string, status: WorkspaceInvitationStatus, role: WorkspaceMembershipRole, createdAt: any, invitedBy?: (
        { __typename?: 'User' }
        & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
      ) | null, workspace: { __typename?: 'Workspace', slug: string, name: string } } | null, workspace?: { __typename?: 'Workspace', slug: string } | null } };

export type DeclineWorkspaceInvitationMutationVariables = Exact<{
  input: DeclineWorkspaceInvitationInput;
}>;


export type DeclineWorkspaceInvitationMutation = { __typename?: 'Mutation', declineWorkspaceInvitation: { __typename?: 'DeclineWorkspaceInvitationResult', success: boolean, errors: Array<DeclineWorkspaceInvitationError>, invitation?: { __typename?: 'WorkspaceInvitation', id: string, status: WorkspaceInvitationStatus } | null } };

export type ConnectionPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  connectionId: Scalars['UUID']['input'];
}>;


export type ConnectionPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', update: boolean } }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null, connection?: (
    { __typename?: 'CustomConnection', id: string, name: string, slug: string, description?: string | null, type: ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }
    & { ' $fragmentRefs'?: { 'ConnectionUsageSnippets_Connection_CustomConnection_Fragment': ConnectionUsageSnippets_Connection_CustomConnection_Fragment;'ConnectionFieldsSection_Connection_CustomConnection_Fragment': ConnectionFieldsSection_Connection_CustomConnection_Fragment } }
  ) | (
    { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, description?: string | null, type: ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }
    & { ' $fragmentRefs'?: { 'ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment': ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment;'ConnectionFieldsSection_Connection_Dhis2Connection_Fragment': ConnectionFieldsSection_Connection_Dhis2Connection_Fragment } }
  ) | (
    { __typename?: 'GCSConnection', id: string, name: string, slug: string, description?: string | null, type: ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }
    & { ' $fragmentRefs'?: { 'ConnectionUsageSnippets_Connection_GcsConnection_Fragment': ConnectionUsageSnippets_Connection_GcsConnection_Fragment;'ConnectionFieldsSection_Connection_GcsConnection_Fragment': ConnectionFieldsSection_Connection_GcsConnection_Fragment } }
  ) | (
    { __typename?: 'IASOConnection', id: string, name: string, slug: string, description?: string | null, type: ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }
    & { ' $fragmentRefs'?: { 'ConnectionUsageSnippets_Connection_IasoConnection_Fragment': ConnectionUsageSnippets_Connection_IasoConnection_Fragment;'ConnectionFieldsSection_Connection_IasoConnection_Fragment': ConnectionFieldsSection_Connection_IasoConnection_Fragment } }
  ) | (
    { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, description?: string | null, type: ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }
    & { ' $fragmentRefs'?: { 'ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment': ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment;'ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment': ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment } }
  ) | (
    { __typename?: 'S3Connection', id: string, name: string, slug: string, description?: string | null, type: ConnectionType, createdAt: any, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }
    & { ' $fragmentRefs'?: { 'ConnectionUsageSnippets_Connection_S3Connection_Fragment': ConnectionUsageSnippets_Connection_S3Connection_Fragment;'ConnectionFieldsSection_Connection_S3Connection_Fragment': ConnectionFieldsSection_Connection_S3Connection_Fragment } }
  ) | null };

export type UpdateConnectionMutationVariables = Exact<{
  input: UpdateConnectionInput;
}>;


export type UpdateConnectionMutation = { __typename?: 'Mutation', updateConnection: { __typename?: 'UpdateConnectionResult', success: boolean, errors: Array<UpdateConnectionError>, connection?: { __typename?: 'CustomConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | { __typename?: 'S3Connection', id: string, name: string, slug: string, description?: string | null, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } | null } };

export type ConnectionsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
}>;


export type ConnectionsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', update: boolean, createConnection: boolean }, connections: Array<{ __typename?: 'CustomConnection', id: string, description?: string | null, name: string, type: ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'DHIS2Connection', id: string, description?: string | null, name: string, type: ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'GCSConnection', id: string, description?: string | null, name: string, type: ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'IASOConnection', id: string, description?: string | null, name: string, type: ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'PostgreSQLConnection', id: string, description?: string | null, name: string, type: ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } } | { __typename?: 'S3Connection', id: string, description?: string | null, name: string, type: ConnectionType, slug: string, updatedAt?: any | null, permissions: { __typename?: 'ConnectionPermissions', update: boolean, delete: boolean } }> }
    & { ' $fragmentRefs'?: { 'CreateConnectionDialog_WorkspaceFragment': CreateConnectionDialog_WorkspaceFragment;'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null };

export type WorkspaceDatabaseTablePageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  tableName: Scalars['String']['input'];
}>;


export type WorkspaceDatabaseTablePageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', deleteDatabaseTable: boolean }, database: { __typename?: 'Database', table?: (
        { __typename?: 'DatabaseTable', name: string, count?: number | null, columns: Array<{ __typename?: 'TableColumn', name: string, type: string }> }
        & { ' $fragmentRefs'?: { 'DatabaseTableDataGrid_TableFragment': DatabaseTableDataGrid_TableFragment } }
      ) | null } }
    & { ' $fragmentRefs'?: { 'DatabaseTableDataGrid_WorkspaceFragment': DatabaseTableDataGrid_WorkspaceFragment;'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null };

export type WorkspaceDatabasesPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspaceDatabasesPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', update: boolean }, database: { __typename?: 'Database', tables: { __typename?: 'DatabaseTablePage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'DatabaseTable', name: string, count?: number | null }> } } }
    & { ' $fragmentRefs'?: { 'DatabaseVariablesSection_WorkspaceFragment': DatabaseVariablesSection_WorkspaceFragment;'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null };

export type WorkspaceDatasetAccessPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  sourceWorkspaceSlug: Scalars['String']['input'];
  datasetSlug: Scalars['String']['input'];
  versionId: Scalars['ID']['input'];
  isSpecificVersion: Scalars['Boolean']['input'];
}>;


export type WorkspaceDatasetAccessPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, organization?: { __typename?: 'Organization', id: string, name: string } | null }
    & { ' $fragmentRefs'?: { 'DatasetLayout_WorkspaceFragment': DatasetLayout_WorkspaceFragment } }
  ) | null, datasetLink?: (
    { __typename?: 'DatasetLink', id: string, dataset: (
      { __typename?: 'Dataset', name: string, sharedWithOrganization: boolean, permissions: { __typename?: 'DatasetPermissions', update: boolean }, workspace?: { __typename?: 'Workspace', organization?: { __typename?: 'Organization', id: string, name: string } | null } | null, version?: (
        { __typename?: 'DatasetVersion' }
        & { ' $fragmentRefs'?: { 'DatasetLayout_VersionFragment': DatasetLayout_VersionFragment } }
      ) | null, latestVersion?: (
        { __typename?: 'DatasetVersion' }
        & { ' $fragmentRefs'?: { 'DatasetLayout_VersionFragment': DatasetLayout_VersionFragment } }
      ) | null }
      & { ' $fragmentRefs'?: { 'DatasetLinksDataGrid_DatasetFragment': DatasetLinksDataGrid_DatasetFragment } }
    ) }
    & { ' $fragmentRefs'?: { 'DatasetLayout_DatasetLinkFragment': DatasetLayout_DatasetLinkFragment } }
  ) | null };

export type WorkspaceDatasetFilesPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  sourceWorkspaceSlug: Scalars['String']['input'];
  datasetSlug: Scalars['String']['input'];
  versionId: Scalars['ID']['input'];
  isSpecificVersion: Scalars['Boolean']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspaceDatasetFilesPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string }
    & { ' $fragmentRefs'?: { 'DatasetLayout_WorkspaceFragment': DatasetLayout_WorkspaceFragment } }
  ) | null, datasetLink?: (
    { __typename?: 'DatasetLink', id: string, dataset: (
      { __typename?: 'Dataset', name: string, version?: (
        { __typename?: 'DatasetVersion', files: { __typename?: 'DatasetVersionFilePage', items: Array<(
            { __typename?: 'DatasetVersionFile' }
            & { ' $fragmentRefs'?: { 'DatasetExplorer_FileFragment': DatasetExplorer_FileFragment } }
          )> } }
        & { ' $fragmentRefs'?: { 'DatasetLayout_VersionFragment': DatasetLayout_VersionFragment;'DatasetExplorer_VersionFragment': DatasetExplorer_VersionFragment } }
      ) | null, latestVersion?: (
        { __typename?: 'DatasetVersion', files: { __typename?: 'DatasetVersionFilePage', items: Array<(
            { __typename?: 'DatasetVersionFile' }
            & { ' $fragmentRefs'?: { 'DatasetExplorer_FileFragment': DatasetExplorer_FileFragment } }
          )> } }
        & { ' $fragmentRefs'?: { 'DatasetLayout_VersionFragment': DatasetLayout_VersionFragment;'DatasetExplorer_VersionFragment': DatasetExplorer_VersionFragment } }
      ) | null }
      & { ' $fragmentRefs'?: { 'DatasetLinksDataGrid_DatasetFragment': DatasetLinksDataGrid_DatasetFragment } }
    ) }
    & { ' $fragmentRefs'?: { 'DatasetLayout_DatasetLinkFragment': DatasetLayout_DatasetLinkFragment } }
  ) | null };

export type WorkspaceDatasetIndexPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  sourceWorkspaceSlug: Scalars['String']['input'];
  datasetSlug: Scalars['String']['input'];
  versionId: Scalars['ID']['input'];
  isSpecificVersion: Scalars['Boolean']['input'];
}>;


export type WorkspaceDatasetIndexPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string }
    & { ' $fragmentRefs'?: { 'DatasetLayout_WorkspaceFragment': DatasetLayout_WorkspaceFragment } }
  ) | null, datasetLink?: (
    { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', id: string, name: string, slug: string, description?: string | null, sharedWithOrganization: boolean, updatedAt: any, createdAt: any, permissions: { __typename?: 'DatasetPermissions', update: boolean }, workspace?: { __typename?: 'Workspace', name: string, slug: string, organization?: { __typename?: 'Organization', name: string } | null } | null, createdBy?: (
        { __typename?: 'User' }
        & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
      ) | null, version?: (
        { __typename?: 'DatasetVersion', id: string, createdAt: any, changelog?: string | null, name: string, createdBy?: (
          { __typename?: 'User' }
          & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
        ) | null, permissions: { __typename?: 'DatasetVersionPermissions', update: boolean } }
        & { ' $fragmentRefs'?: { 'DatasetLayout_VersionFragment': DatasetLayout_VersionFragment } }
      ) | null, latestVersion?: (
        { __typename?: 'DatasetVersion', id: string, changelog?: string | null, createdAt: any, name: string, createdBy?: (
          { __typename?: 'User' }
          & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
        ) | null, permissions: { __typename?: 'DatasetVersionPermissions', update: boolean } }
        & { ' $fragmentRefs'?: { 'DatasetLayout_VersionFragment': DatasetLayout_VersionFragment } }
      ) | null } }
    & { ' $fragmentRefs'?: { 'DatasetLayout_DatasetLinkFragment': DatasetLayout_DatasetLinkFragment } }
  ) | null };

export type WorkspaceDatasetsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
}>;


export type WorkspaceDatasetsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, permissions: { __typename?: 'WorkspacePermissions', createDataset: boolean }, pinnedDatasets: { __typename?: 'DatasetLinkPage', items: Array<(
        { __typename?: 'DatasetLink' }
        & { ' $fragmentRefs'?: { 'DatasetCard_LinkFragment': DatasetCard_LinkFragment } }
      )> }, datasets: { __typename?: 'DatasetLinkPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<(
        { __typename?: 'DatasetLink', id: string, dataset: { __typename?: 'Dataset', id: string, name: string, slug: string, description?: string | null, updatedAt: any, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null, permissions: { __typename?: 'DatasetPermissions', update: boolean, delete: boolean }, createdBy?: (
            { __typename?: 'User' }
            & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
          ) | null } }
        & { ' $fragmentRefs'?: { 'PinDatasetButton_LinkFragment': PinDatasetButton_LinkFragment } }
      )> } }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment;'CreateDatasetDialog_WorkspaceFragment': CreateDatasetDialog_WorkspaceFragment } }
  ) | null };

export type WorkspaceFilesPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  page: Scalars['Int']['input'];
  perPage: Scalars['Int']['input'];
  prefix: Scalars['String']['input'];
  query?: InputMaybe<Scalars['String']['input']>;
  ignoreHiddenFiles?: InputMaybe<Scalars['Boolean']['input']>;
}>;


export type WorkspaceFilesPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, bucket: { __typename?: 'Bucket', objects: (
        { __typename?: 'BucketObjectPage' }
        & { ' $fragmentRefs'?: { 'BucketExplorer_ObjectsFragment': BucketExplorer_ObjectsFragment } }
      ) }, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean } }
    & { ' $fragmentRefs'?: { 'BucketExplorer_WorkspaceFragment': BucketExplorer_WorkspaceFragment;'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment;'UploadObjectDialog_WorkspaceFragment': UploadObjectDialog_WorkspaceFragment;'CreateBucketFolderDialog_WorkspaceFragment': CreateBucketFolderDialog_WorkspaceFragment;'BucketExplorer_WorkspaceFragment': BucketExplorer_WorkspaceFragment } }
  ) | null };

export type WorkspacePageQueryVariables = Exact<{
  slug: Scalars['String']['input'];
}>;


export type WorkspacePageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, description?: string | null, dockerImage?: string | null, configuration: any, countries: Array<{ __typename?: 'Country', code: string, flag: string, name: string }>, permissions: { __typename?: 'WorkspacePermissions', delete: boolean, update: boolean, manageMembers: boolean } }
    & { ' $fragmentRefs'?: { 'ArchiveWorkspace_WorkspaceFragment': ArchiveWorkspace_WorkspaceFragment;'InviteMemberWorkspace_WorkspaceFragment': InviteMemberWorkspace_WorkspaceFragment;'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null };

export type UpdateWorkspaceMutationVariables = Exact<{
  input: UpdateWorkspaceInput;
}>;


export type UpdateWorkspaceMutation = { __typename?: 'Mutation', updateWorkspace: { __typename?: 'UpdateWorkspaceResult', success: boolean, errors: Array<UpdateWorkspaceError>, workspace?: { __typename?: 'Workspace', slug: string, name: string, description?: string | null, configuration: any, countries: Array<{ __typename?: 'Country', code: string, alpha3: string, name: string }> } | null } };

export type WorkspaceNotebooksPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
}>;


export type WorkspaceNotebooksPageQuery = { __typename?: 'Query', notebooksUrl: any, workspace?: (
    { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', launchNotebookServer: boolean } }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null };

export type WorkspacePipelineCodePageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  pipelineCode: Scalars['String']['input'];
}>;


export type WorkspacePipelineCodePageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'PipelineLayout_WorkspaceFragment': PipelineLayout_WorkspaceFragment } }
  ) | null, pipeline?: (
    { __typename?: 'Pipeline', id: string, code: string, name?: string | null, type: PipelineType, currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, files: Array<(
        { __typename?: 'FileNode' }
        & { ' $fragmentRefs'?: { 'FilesEditor_FileFragment': FilesEditor_FileFragment } }
      )> } | null }
    & { ' $fragmentRefs'?: { 'PipelineLayout_PipelineFragment': PipelineLayout_PipelineFragment } }
  ) | null };

export type GetPipelineVersionFilesQueryVariables = Exact<{
  versionId: Scalars['UUID']['input'];
}>;


export type GetPipelineVersionFilesQuery = { __typename?: 'Query', pipelineVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, files: Array<(
      { __typename?: 'FileNode' }
      & { ' $fragmentRefs'?: { 'FilesEditor_FileFragment': FilesEditor_FileFragment } }
    )> } | null };

export type WorkspacePipelinePageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  pipelineCode: Scalars['String']['input'];
}>;


export type WorkspacePipelinePageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'PipelineLayout_WorkspaceFragment': PipelineLayout_WorkspaceFragment } }
  ) | null, pipeline?: (
    { __typename?: 'Pipeline', webhookUrl?: string | null, webhookEnabled: boolean, id: string, createdAt: any, code: string, name?: string | null, description?: string | null, schedule?: string | null, type: PipelineType, functionalType?: PipelineFunctionalType | null, notebookPath?: string | null, autoUpdateFromTemplate: boolean, hasNewTemplateVersions: boolean, permissions: { __typename?: 'PipelinePermissions', run: boolean, update: boolean, schedule: boolean, delete: boolean, createVersion: boolean, createTemplateVersion: { __typename?: 'CreateTemplateVersionPermission', isAllowed: boolean } }, tags: Array<(
      { __typename?: 'Tag' }
      & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
    )>, sourceTemplate?: { __typename?: 'PipelineTemplate', id: string, code: string, name: string } | null, newTemplateVersions: Array<{ __typename?: 'PipelineTemplateVersion', id: string, changelog?: string | null, versionNumber: number, createdAt: any }>, currentVersion?: (
      { __typename?: 'PipelineVersion', id: string, versionName: string, description?: string | null, config?: any | null, externalLink?: any | null }
      & { ' $fragmentRefs'?: { 'PipelineVersionParametersTable_VersionFragment': PipelineVersionParametersTable_VersionFragment;'PipelineVersionConfigDialog_VersionFragment': PipelineVersionConfigDialog_VersionFragment } }
    ) | null, recipients: Array<{ __typename?: 'PipelineRecipient', user: { __typename?: 'User', id: string, displayName: string } }> }
    & { ' $fragmentRefs'?: { 'RunPipelineDialog_PipelineFragment': RunPipelineDialog_PipelineFragment;'PipelineLayout_PipelineFragment': PipelineLayout_PipelineFragment } }
  ) | null };

export type WorkspacePipelineNotificationsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  pipelineCode: Scalars['String']['input'];
}>;


export type WorkspacePipelineNotificationsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace' }
    & { ' $fragmentRefs'?: { 'PipelineLayout_WorkspaceFragment': PipelineLayout_WorkspaceFragment } }
  ) | null, pipeline?: (
    { __typename?: 'Pipeline', id: string, code: string, type: PipelineType, schedule?: string | null, permissions: { __typename?: 'PipelinePermissions', schedule: boolean, update: boolean } }
    & { ' $fragmentRefs'?: { 'PipelineLayout_PipelineFragment': PipelineLayout_PipelineFragment;'PipelineRecipients_PipelineFragment': PipelineRecipients_PipelineFragment } }
  ) | null };

export type WorkspacePipelineRunPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  runId: Scalars['UUID']['input'];
}>;


export type WorkspacePipelineRunPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment;'RunOutputsTable_WorkspaceFragment': RunOutputsTable_WorkspaceFragment } }
  ) | null, pipelineRun?: (
    { __typename?: 'PipelineRun', id: string, timeout?: number | null, config: any, executionDate?: any | null, duration?: number | null, triggerMode?: PipelineRunTrigger | null, version?: { __typename?: 'PipelineVersion', versionName: string, parameters: Array<(
        { __typename?: 'PipelineParameter' }
        & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
      )> } | null, pipeline: (
      { __typename?: 'Pipeline', id: string, code: string, name?: string | null, type: PipelineType, notebookPath?: string | null, sourceTemplate?: { __typename?: 'PipelineTemplate', id: string, name: string } | null, permissions: { __typename?: 'PipelinePermissions', stopPipeline: boolean } }
      & { ' $fragmentRefs'?: { 'RunPipelineDialog_PipelineFragment': RunPipelineDialog_PipelineFragment } }
    ), user?: (
      { __typename?: 'User' }
      & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
    ) | null, stoppedBy?: (
      { __typename?: 'User' }
      & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
    ) | null }
    & { ' $fragmentRefs'?: { 'RunOutputsTable_RunFragment': RunOutputsTable_RunFragment;'RunPipelineDialog_RunFragment': RunPipelineDialog_RunFragment;'RunMessages_RunFragment': RunMessages_RunFragment;'RunLogs_RunFragment': RunLogs_RunFragment;'PipelineRunStatusBadge_RunFragment': PipelineRunStatusBadge_RunFragment } }
  ) | null };

export type WorkspacePipelineRunsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  pipelineCode: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspacePipelineRunsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'PipelineLayout_WorkspaceFragment': PipelineLayout_WorkspaceFragment } }
  ) | null, pipeline?: (
    { __typename?: 'Pipeline', id: string, type: PipelineType, runs: { __typename?: 'PipelineRunPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<(
        { __typename?: 'PipelineRun', id: string, executionDate?: any | null, duration?: number | null, triggerMode?: PipelineRunTrigger | null, version?: { __typename?: 'PipelineVersion', versionName: string, createdAt: any, user?: (
            { __typename?: 'User' }
            & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
          ) | null } | null, user?: (
          { __typename?: 'User' }
          & { ' $fragmentRefs'?: { 'UserColumn_UserFragment': UserColumn_UserFragment } }
        ) | null }
        & { ' $fragmentRefs'?: { 'PipelineRunStatusBadge_RunFragment': PipelineRunStatusBadge_RunFragment } }
      )> } }
    & { ' $fragmentRefs'?: { 'PipelineLayout_PipelineFragment': PipelineLayout_PipelineFragment } }
  ) | null };

export type WorkspacePipelineVersionsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  pipelineCode: Scalars['String']['input'];
  page: Scalars['Int']['input'];
  perPage: Scalars['Int']['input'];
}>;


export type WorkspacePipelineVersionsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null, pipeline?: { __typename?: 'Pipeline', id: string, code: string, name?: string | null, currentVersion?: { __typename?: 'PipelineVersion', id: string } | null, versions: { __typename?: 'PipelineVersionPage', totalItems: number, totalPages: number, items: Array<(
        { __typename?: 'PipelineVersion', id: string }
        & { ' $fragmentRefs'?: { 'PipelineVersionCard_VersionFragment': PipelineVersionCard_VersionFragment } }
      )> } } | null };

export type WorkspaceTemplatePageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  templateCode: Scalars['String']['input'];
}>;


export type WorkspaceTemplatePageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'PipelineLayout_WorkspaceFragment': PipelineLayout_WorkspaceFragment } }
  ) | null, template?: (
    { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, functionalType?: PipelineFunctionalType | null, permissions: { __typename?: 'PipelineTemplatePermissions', update: boolean, delete: boolean }, tags: Array<(
      { __typename?: 'Tag' }
      & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
    )>, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, sourcePipelineVersion: { __typename?: 'PipelineVersion', zipfile: string, files: Array<(
          { __typename?: 'FileNode' }
          & { ' $fragmentRefs'?: { 'FilesEditor_FileFragment': FilesEditor_FileFragment } }
        )> } } | null }
    & { ' $fragmentRefs'?: { 'TemplateLayout_TemplateFragment': TemplateLayout_TemplateFragment } }
  ) | null };

export type WorkspaceTemplateVersionsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  templateCode: Scalars['String']['input'];
  page: Scalars['Int']['input'];
  perPage: Scalars['Int']['input'];
}>;


export type WorkspaceTemplateVersionsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null, template?: { __typename?: 'PipelineTemplate', id: string, code: string, name: string, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null, versions: { __typename?: 'TemplateVersionPage', totalItems: number, totalPages: number, items: Array<(
        { __typename?: 'PipelineTemplateVersion', id: string }
        & { ' $fragmentRefs'?: { 'TemplateVersionCard_VersionFragment': TemplateVersionCard_VersionFragment } }
      )> } } | null };

export type WorkspaceWebappPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  webappId: Scalars['UUID']['input'];
}>;


export type WorkspaceWebappPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace' }
    & { ' $fragmentRefs'?: { 'WebappForm_WorkspaceFragment': WebappForm_WorkspaceFragment } }
  ) | null, webapp?: (
    { __typename?: 'Webapp' }
    & { ' $fragmentRefs'?: { 'WebappForm_WebappFragment': WebappForm_WebappFragment } }
  ) | null };

export type WorkspaceWebappsPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspaceWebappsPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null, webapps: { __typename?: 'WebappsPage', totalPages: number, totalItems: number, items: Array<{ __typename?: 'Webapp', id: string, name: string, icon?: string | null, description?: string | null, url: string, isFavorite: boolean, createdBy: (
        { __typename?: 'User', firstName?: string | null, lastName?: string | null }
        & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
      ), workspace: { __typename?: 'Workspace', slug: string, name: string }, permissions: { __typename?: 'WebappPermissions', update: boolean, delete: boolean } }> }, favoriteWebapps: { __typename?: 'WebappsPage', items: Array<(
      { __typename?: 'Webapp' }
      & { ' $fragmentRefs'?: { 'WebappCard_WebappFragment': WebappCard_WebappFragment } }
    )> } };

export type CheckWorkspaceAvailabilityQueryVariables = Exact<{
  slug: Scalars['String']['input'];
}>;


export type CheckWorkspaceAvailabilityQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string } | null };

export type DeletePipelineTemplateMutationVariables = Exact<{
  input: DeletePipelineTemplateInput;
}>;


export type DeletePipelineTemplateMutation = { __typename?: 'Mutation', deletePipelineTemplate: { __typename?: 'DeletePipelineTemplateResult', success: boolean, errors: Array<PipelineTemplateError> } };

export type PipelineTemplateDialog_PipelineTemplateFragment = { __typename?: 'PipelineTemplate', id: string, name: string } & { ' $fragmentName'?: 'PipelineTemplateDialog_PipelineTemplateFragment' };

export type DownloadPipelineVersion_VersionFragment = { __typename?: 'PipelineVersion', id: string, name?: string | null, pipeline: { __typename?: 'Pipeline', id: string, code: string } } & { ' $fragmentName'?: 'DownloadPipelineVersion_VersionFragment' };

export type DownloadTemplateVersion_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string } & { ' $fragmentName'?: 'DownloadTemplateVersion_VersionFragment' };

export type PipelineMetadataDisplay_PipelineFragment = { __typename?: 'Pipeline', functionalType?: PipelineFunctionalType | null, tags: Array<(
    { __typename?: 'Tag' }
    & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
  )> } & { ' $fragmentName'?: 'PipelineMetadataDisplay_PipelineFragment' };

export type PipelineMetadataDisplay_TemplateFragment = { __typename?: 'PipelineTemplate', functionalType?: PipelineFunctionalType | null, tags: Array<(
    { __typename?: 'Tag' }
    & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
  )> } & { ' $fragmentName'?: 'PipelineMetadataDisplay_TemplateFragment' };

export type PipelineRunDataCard_DagFragment = (
  { __typename?: 'DAG', id: string, externalId: string, label: string }
  & { ' $fragmentRefs'?: { 'PipelineRunReadonlyForm_DagFragment': PipelineRunReadonlyForm_DagFragment } }
) & { ' $fragmentName'?: 'PipelineRunDataCard_DagFragment' };

export type PipelineRunDataCard_DagRunFragment = (
  { __typename?: 'DAGRun', id: string, label?: string | null, externalId?: string | null, externalUrl?: any | null, executionDate?: any | null, triggerMode?: DagRunTrigger | null, status: DagRunStatus, config?: any | null, duration?: number | null, progress: number, outputs: Array<(
    { __typename?: 'DAGRunOutput' }
    & { ' $fragmentRefs'?: { 'PipelineRunOutputEntry_OutputFragment': PipelineRunOutputEntry_OutputFragment } }
  )>, user?: (
    { __typename?: 'User', displayName: string }
    & { ' $fragmentRefs'?: { 'UserProperty_UserFragment': UserProperty_UserFragment } }
  ) | null, messages: Array<{ __typename: 'DAGRunMessage' }> }
  & { ' $fragmentRefs'?: { 'RunMessages_DagRunFragment': RunMessages_DagRunFragment;'RunLogs_DagRunFragment': RunLogs_DagRunFragment;'PipelineRunReadonlyForm_DagRunFragment': PipelineRunReadonlyForm_DagRunFragment;'PipelineRunFavoriteTrigger_RunFragment': PipelineRunFavoriteTrigger_RunFragment } }
) & { ' $fragmentName'?: 'PipelineRunDataCard_DagRunFragment' };

export type PipelineRunFavoriteIcon_RunFragment = { __typename?: 'DAGRun', isFavorite: boolean } & { ' $fragmentName'?: 'PipelineRunFavoriteIcon_RunFragment' };

export type SetFavoriteRunMutationVariables = Exact<{
  input: SetDagRunFavoriteInput;
}>;


export type SetFavoriteRunMutation = { __typename?: 'Mutation', setDAGRunFavorite?: { __typename?: 'SetDAGRunFavoriteResult', success: boolean, errors: Array<SetDagRunFavoriteError>, dagRun?: { __typename?: 'DAGRun', id: string, label?: string | null, isFavorite: boolean } | null } | null };

export type PipelineRunFavoriteTrigger_RunFragment = (
  { __typename?: 'DAGRun', id: string, label?: string | null, isFavorite: boolean }
  & { ' $fragmentRefs'?: { 'PipelineRunFavoriteIcon_RunFragment': PipelineRunFavoriteIcon_RunFragment } }
) & { ' $fragmentName'?: 'PipelineRunFavoriteTrigger_RunFragment' };

export type PipelineRunForm_DagFragment = { __typename?: 'DAG', formCode?: string | null, id: string, template: { __typename?: 'DAGTemplate', sampleConfig?: any | null } } & { ' $fragmentName'?: 'PipelineRunForm_DagFragment' };

export type PipelineRunReadonlyForm_DagFragment = { __typename?: 'DAG', formCode?: string | null, id: string } & { ' $fragmentName'?: 'PipelineRunReadonlyForm_DagFragment' };

export type PipelineRunReadonlyForm_DagRunFragment = { __typename?: 'DAGRun', config?: any | null } & { ' $fragmentName'?: 'PipelineRunReadonlyForm_DagRunFragment' };

export type PipelineRunOutputEntry_OutputFragment = { __typename?: 'DAGRunOutput', title: string, uri: string } & { ' $fragmentName'?: 'PipelineRunOutputEntry_OutputFragment' };

export type PipelineRunStatusBadge_RunFragment = (
  { __typename?: 'PipelineRun', id: string, status: PipelineRunStatus }
  & { ' $fragmentRefs'?: { 'UsePipelineRunPoller_RunFragment': UsePipelineRunPoller_RunFragment } }
) & { ' $fragmentName'?: 'PipelineRunStatusBadge_RunFragment' };

export type CreatePipelineFromTemplateVersionMutationVariables = Exact<{
  input: CreatePipelineFromTemplateVersionInput;
}>;


export type CreatePipelineFromTemplateVersionMutation = { __typename?: 'Mutation', createPipelineFromTemplateVersion: { __typename?: 'CreatePipelineFromTemplateVersionResult', success: boolean, errors?: Array<CreatePipelineFromTemplateVersionError> | null, pipeline?: { __typename?: 'Pipeline', id: string, name?: string | null, code: string } | null } };

export type GetPipelineTemplatesQueryVariables = Exact<{
  page: Scalars['Int']['input'];
  perPage: Scalars['Int']['input'];
  search?: InputMaybe<Scalars['String']['input']>;
  currentWorkspaceSlug: Scalars['String']['input'];
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']> | Scalars['String']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
}>;


export type GetPipelineTemplatesQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, pipelineTemplateTags: Array<string> } | null, pipelineTemplates: { __typename?: 'PipelineTemplatePage', pageNumber: number, totalPages: number, totalItems: number, items: Array<{ __typename?: 'PipelineTemplate', id: string, description?: string | null, code: string, name: string, functionalType?: PipelineFunctionalType | null, tags: Array<{ __typename?: 'Tag', id: string, name: string }>, permissions: { __typename?: 'PipelineTemplatePermissions', delete: boolean }, workspace?: { __typename?: 'Workspace', slug: string, name: string } | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, createdAt: any, user?: (
          { __typename?: 'User' }
          & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
        ) | null, template: { __typename?: 'PipelineTemplate', sourcePipeline?: { __typename?: 'Pipeline', name?: string | null } | null } } | null }> } };

export type PipelineTemplates_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'PipelineTemplates_WorkspaceFragment' };

export type UpdatePipelineVersionMutationVariables = Exact<{
  input: UpdatePipelineVersionInput;
}>;


export type UpdatePipelineVersionMutation = { __typename?: 'Mutation', updatePipelineVersion: { __typename?: 'UpdatePipelineVersionResult', success: boolean, errors: Array<UpdatePipelineVersionError>, pipelineVersion?: (
      { __typename?: 'PipelineVersion' }
      & { ' $fragmentRefs'?: { 'PipelineVersionCard_VersionFragment': PipelineVersionCard_VersionFragment } }
    ) | null } };

export type PipelineVersionCard_VersionFragment = (
  { __typename?: 'PipelineVersion', id: string, versionName: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineVersionPermissions', update: boolean }, parameters: Array<(
    { __typename?: 'PipelineParameter' }
    & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
  )>, pipeline: { __typename?: 'Pipeline', id: string, code: string }, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string, name: string } } | null }
  & { ' $fragmentRefs'?: { 'DownloadPipelineVersion_VersionFragment': DownloadPipelineVersion_VersionFragment;'DeletePipelineVersionTrigger_VersionFragment': DeletePipelineVersionTrigger_VersionFragment } }
) & { ' $fragmentName'?: 'PipelineVersionCard_VersionFragment' };

export type PipelineVersionParametersTable_VersionFragment = { __typename?: 'PipelineVersion', id: string, config?: any | null, parameters: Array<(
    { __typename?: 'PipelineParameter' }
    & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
  )> } & { ' $fragmentName'?: 'PipelineVersionParametersTable_VersionFragment' };

export type WorkspacePipelinesPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  search?: InputMaybe<Scalars['String']['input']>;
  tags?: InputMaybe<Array<Scalars['String']['input']> | Scalars['String']['input']>;
  functionalType?: InputMaybe<PipelineFunctionalType>;
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspacePipelinesPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string, pipelineTags: Array<string> }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment;'CreatePipelineDialog_WorkspaceFragment': CreatePipelineDialog_WorkspaceFragment } }
  ) | null, pipelines: { __typename?: 'PipelinesPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<(
      { __typename?: 'Pipeline' }
      & { ' $fragmentRefs'?: { 'PipelineCard_PipelineFragment': PipelineCard_PipelineFragment } }
    )> } };

export type Pipelines_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'Pipelines_WorkspaceFragment' };

export type PipelinesPickerQueryVariables = Exact<{ [key: string]: never; }>;


export type PipelinesPickerQuery = { __typename?: 'Query', dags: { __typename?: 'DAGPage', items: Array<(
      { __typename?: 'DAG' }
      & { ' $fragmentRefs'?: { 'PipelinesPicker_ValueFragment': PipelinesPicker_ValueFragment } }
    )> } };

export type PipelinesPicker_ValueFragment = { __typename?: 'DAG', id: string, externalId: string } & { ' $fragmentName'?: 'PipelinesPicker_ValueFragment' };

export type CreatePipelineTemplateVersionMutationVariables = Exact<{
  input: CreatePipelineTemplateVersionInput;
}>;


export type CreatePipelineTemplateVersionMutation = { __typename?: 'Mutation', createPipelineTemplateVersion: { __typename?: 'CreatePipelineTemplateVersionResult', success: boolean, errors?: Array<CreatePipelineTemplateVersionError> | null, pipelineTemplate?: { __typename?: 'PipelineTemplate', name: string, code: string } | null } };

export type PipelinePublish_PipelineFragment = { __typename?: 'Pipeline', id: string, name?: string | null, description?: string | null, currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string } | null, template?: { __typename?: 'PipelineTemplate', id: string, name: string } | null } & { ' $fragmentName'?: 'PipelinePublish_PipelineFragment' };

export type PipelinePublish_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'PipelinePublish_WorkspaceFragment' };

export type RunLogs_DagRunFragment = { __typename?: 'DAGRun', id: string, logs?: string | null, status: DagRunStatus } & { ' $fragmentName'?: 'RunLogs_DagRunFragment' };

export type RunLogs_RunFragment = { __typename?: 'PipelineRun', id: string, logs?: string | null, status: PipelineRunStatus } & { ' $fragmentName'?: 'RunLogs_RunFragment' };

export type RunMessages_DagRunFragment = { __typename?: 'DAGRun', id: string, status: DagRunStatus, messages: Array<{ __typename?: 'DAGRunMessage', message: string, timestamp?: any | null, priority: string }> } & { ' $fragmentName'?: 'RunMessages_DagRunFragment' };

export type RunMessages_RunFragment = { __typename?: 'PipelineRun', id: string, status: PipelineRunStatus, messages: Array<{ __typename?: 'PipelineRunMessage', message: string, timestamp?: any | null, priority: MessagePriority }> } & { ' $fragmentName'?: 'RunMessages_RunFragment' };

export type UpdateTemplateVersionMutationVariables = Exact<{
  input: UpdateTemplateVersionInput;
}>;


export type UpdateTemplateVersionMutation = { __typename?: 'Mutation', updateTemplateVersion: { __typename?: 'UpdateTemplateVersionResult', success: boolean, errors: Array<UpdateTemplateVersionError>, templateVersion?: (
      { __typename?: 'PipelineTemplateVersion' }
      & { ' $fragmentRefs'?: { 'TemplateVersionCard_VersionFragment': TemplateVersionCard_VersionFragment } }
    ) | null } };

export type TemplateVersionCard_VersionFragment = (
  { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any, isLatestVersion: boolean, user?: { __typename?: 'User', displayName: string } | null, permissions: { __typename?: 'PipelineTemplateVersionPermissions', update: boolean }, template: { __typename?: 'PipelineTemplate', id: string, code: string } }
  & { ' $fragmentRefs'?: { 'DeleteTemplateVersionTrigger_VersionFragment': DeleteTemplateVersionTrigger_VersionFragment } }
) & { ' $fragmentName'?: 'TemplateVersionCard_VersionFragment' };

export type UpgradePipelineVersionFromTemplateMutationVariables = Exact<{
  input: UpgradePipelineVersionFromTemplateInput;
}>;


export type UpgradePipelineVersionFromTemplateMutation = { __typename?: 'Mutation', upgradePipelineVersionFromTemplate: { __typename?: 'UpgradePipelineVersionFromTemplateResult', success: boolean, errors: Array<UpgradePipelineVersionFromTemplateError> } };

export type UpgradePipelineFromTemplateDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, newTemplateVersions: Array<{ __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, changelog?: string | null, createdAt: any }> } & { ' $fragmentName'?: 'UpgradePipelineFromTemplateDialog_PipelineFragment' };

export type PipelineRunPollerQueryVariables = Exact<{
  runId: Scalars['UUID']['input'];
}>;


export type PipelineRunPollerQuery = { __typename?: 'Query', run?: (
    { __typename?: 'PipelineRun', duration?: number | null, progress: number }
    & { ' $fragmentRefs'?: { 'UsePipelineRunPoller_RunFragment': UsePipelineRunPoller_RunFragment } }
  ) | null };

export type RunPipelineMutationVariables = Exact<{
  input: RunDagInput;
}>;


export type RunPipelineMutation = { __typename?: 'Mutation', runDAG: { __typename?: 'RunDAGResult', success: boolean, errors: Array<RunDagError>, dag?: { __typename?: 'DAG', id: string } | null, dagRun?: { __typename?: 'DAGRun', id: string, externalUrl?: any | null, externalId?: string | null } | null } };

export type GetPipelineVersionQueryVariables = Exact<{
  versionId: Scalars['UUID']['input'];
}>;


export type GetPipelineVersionQuery = { __typename?: 'Query', pipelineVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, zipfile: string, pipeline: { __typename?: 'Pipeline', code: string } } | null };

export type GetPipelineRunQueryVariables = Exact<{
  runId: Scalars['UUID']['input'];
}>;


export type GetPipelineRunQuery = { __typename?: 'Query', dagRun?: { __typename?: 'DAGRun', config?: any | null, externalUrl?: any | null, externalId?: string | null, status: DagRunStatus, executionDate?: any | null, duration?: number | null } | null };

export type GetRunOutputDownloadUrlMutationVariables = Exact<{
  input: PrepareDownloadUrlInput;
}>;


export type GetRunOutputDownloadUrlMutation = { __typename?: 'Mutation', prepareDownloadURL?: { __typename?: 'PrepareDownloadURLResult', success: boolean, url?: any | null } | null };

export type UsePipelineRunPoller_RunFragment = { __typename?: 'PipelineRun', id: string, status: PipelineRunStatus } & { ' $fragmentName'?: 'UsePipelineRunPoller_RunFragment' };

export type RemoveFromFavoritesMutationVariables = Exact<{
  input: RemoveFromFavoritesInput;
}>;


export type RemoveFromFavoritesMutation = { __typename?: 'Mutation', removeFromFavorites: { __typename?: 'RemoveFromFavoritesResult', success: boolean, errors: Array<RemoveFromFavoritesError> } };

export type AddToFavoritesMutationVariables = Exact<{
  input: AddToFavoritesInput;
}>;


export type AddToFavoritesMutation = { __typename?: 'Mutation', addToFavorites: { __typename?: 'AddToFavoritesResult', success: boolean, errors: Array<AddToFavoritesError> } };

export type FavoriteWebappButton_WebappFragment = { __typename?: 'Webapp', id: string, isFavorite: boolean } & { ' $fragmentName'?: 'FavoriteWebappButton_WebappFragment' };

export type WebappCard_WebappFragment = { __typename?: 'Webapp', id: string, icon?: string | null, name: string, workspace: { __typename?: 'Workspace', slug: string, name: string } } & { ' $fragmentName'?: 'WebappCard_WebappFragment' };

export type UpdateWebappMutationVariables = Exact<{
  input: UpdateWebappInput;
}>;


export type UpdateWebappMutation = { __typename?: 'Mutation', updateWebapp: { __typename?: 'UpdateWebappResult', success: boolean, errors: Array<UpdateWebappError> } };

export type CreateWebappMutationVariables = Exact<{
  input: CreateWebappInput;
}>;


export type CreateWebappMutation = { __typename?: 'Mutation', createWebapp: { __typename?: 'CreateWebappResult', success: boolean, errors: Array<CreateWebappError>, webapp?: { __typename?: 'Webapp', id: string } | null } };

export type WebappForm_WebappFragment = { __typename?: 'Webapp', id: string, name: string, description?: string | null, url: string, icon?: string | null, permissions: { __typename?: 'WebappPermissions', update: boolean, delete: boolean } } & { ' $fragmentName'?: 'WebappForm_WebappFragment' };

export type WebappForm_WorkspaceFragment = (
  { __typename?: 'Workspace' }
  & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
) & { ' $fragmentName'?: 'WebappForm_WorkspaceFragment' };

export type ArchiveWorkspaceMutationVariables = Exact<{
  input: ArchiveWorkspaceInput;
}>;


export type ArchiveWorkspaceMutation = { __typename?: 'Mutation', archiveWorkspace: { __typename?: 'ArchiveWorkspaceResult', success: boolean, errors: Array<ArchiveWorkspaceError> } };

export type ArchiveWorkspace_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string } & { ' $fragmentName'?: 'ArchiveWorkspace_WorkspaceFragment' };

export type BucketExplorer_WorkspaceFragment = (
  { __typename?: 'Workspace', slug: string }
  & { ' $fragmentRefs'?: { 'DownloadBucketObject_WorkspaceFragment': DownloadBucketObject_WorkspaceFragment;'DeleteBucketObject_WorkspaceFragment': DeleteBucketObject_WorkspaceFragment } }
) & { ' $fragmentName'?: 'BucketExplorer_WorkspaceFragment' };

export type BucketExplorer_ObjectsFragment = { __typename?: 'BucketObjectPage', hasNextPage: boolean, hasPreviousPage: boolean, pageNumber: number, items: Array<(
    { __typename?: 'BucketObject', key: string, name: string, path: string, size?: any | null, updatedAt?: any | null, type: BucketObjectType }
    & { ' $fragmentRefs'?: { 'DownloadBucketObject_ObjectFragment': DownloadBucketObject_ObjectFragment;'DeleteBucketObject_ObjectFragment': DeleteBucketObject_ObjectFragment } }
  )> } & { ' $fragmentName'?: 'BucketExplorer_ObjectsFragment' };

export type ObjectPickerQueryVariables = Exact<{
  slug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  prefix?: InputMaybe<Scalars['String']['input']>;
}>;


export type ObjectPickerQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', objects: { __typename?: 'BucketObjectPage', pageNumber: number, hasNextPage: boolean, items: Array<{ __typename?: 'BucketObject', name: string, key: string, path: string, type: BucketObjectType, updatedAt?: any | null }> } } } | null };

export type BucketObjectPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'BucketObjectPicker_WorkspaceFragment' };

type ConnectionFieldsSection_Connection_CustomConnection_Fragment = (
  { __typename?: 'CustomConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } }
  & { ' $fragmentRefs'?: { 'UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment': UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment } }
) & { ' $fragmentName'?: 'ConnectionFieldsSection_Connection_CustomConnection_Fragment' };

type ConnectionFieldsSection_Connection_Dhis2Connection_Fragment = (
  { __typename?: 'DHIS2Connection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } }
  & { ' $fragmentRefs'?: { 'UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment': UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment } }
) & { ' $fragmentName'?: 'ConnectionFieldsSection_Connection_Dhis2Connection_Fragment' };

type ConnectionFieldsSection_Connection_GcsConnection_Fragment = (
  { __typename?: 'GCSConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } }
  & { ' $fragmentRefs'?: { 'UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment': UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment } }
) & { ' $fragmentName'?: 'ConnectionFieldsSection_Connection_GcsConnection_Fragment' };

type ConnectionFieldsSection_Connection_IasoConnection_Fragment = (
  { __typename?: 'IASOConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } }
  & { ' $fragmentRefs'?: { 'UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment': UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment } }
) & { ' $fragmentName'?: 'ConnectionFieldsSection_Connection_IasoConnection_Fragment' };

type ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment = (
  { __typename?: 'PostgreSQLConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } }
  & { ' $fragmentRefs'?: { 'UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment': UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment } }
) & { ' $fragmentName'?: 'ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment' };

type ConnectionFieldsSection_Connection_S3Connection_Fragment = (
  { __typename?: 'S3Connection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }>, permissions: { __typename?: 'ConnectionPermissions', update: boolean } }
  & { ' $fragmentRefs'?: { 'UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment': UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment } }
) & { ' $fragmentName'?: 'ConnectionFieldsSection_Connection_S3Connection_Fragment' };

export type ConnectionFieldsSection_ConnectionFragment = ConnectionFieldsSection_Connection_CustomConnection_Fragment | ConnectionFieldsSection_Connection_Dhis2Connection_Fragment | ConnectionFieldsSection_Connection_GcsConnection_Fragment | ConnectionFieldsSection_Connection_IasoConnection_Fragment | ConnectionFieldsSection_Connection_PostgreSqlConnection_Fragment | ConnectionFieldsSection_Connection_S3Connection_Fragment;

type ConnectionUsageSnippets_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> } & { ' $fragmentName'?: 'ConnectionUsageSnippets_Connection_CustomConnection_Fragment' };

type ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> } & { ' $fragmentName'?: 'ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment' };

type ConnectionUsageSnippets_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> } & { ' $fragmentName'?: 'ConnectionUsageSnippets_Connection_GcsConnection_Fragment' };

type ConnectionUsageSnippets_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> } & { ' $fragmentName'?: 'ConnectionUsageSnippets_Connection_IasoConnection_Fragment' };

type ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> } & { ' $fragmentName'?: 'ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment' };

type ConnectionUsageSnippets_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, type: ConnectionType, slug: string, fields: Array<{ __typename?: 'ConnectionField', code: string }> } & { ' $fragmentName'?: 'ConnectionUsageSnippets_Connection_S3Connection_Fragment' };

export type ConnectionUsageSnippets_ConnectionFragment = ConnectionUsageSnippets_Connection_CustomConnection_Fragment | ConnectionUsageSnippets_Connection_Dhis2Connection_Fragment | ConnectionUsageSnippets_Connection_GcsConnection_Fragment | ConnectionUsageSnippets_Connection_IasoConnection_Fragment | ConnectionUsageSnippets_Connection_PostgreSqlConnection_Fragment | ConnectionUsageSnippets_Connection_S3Connection_Fragment;

export type CreateBucketFolderDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean }, bucket: { __typename?: 'Bucket', name: string } } & { ' $fragmentName'?: 'CreateBucketFolderDialog_WorkspaceFragment' };

export type CreateConnectionMutationVariables = Exact<{
  input: CreateConnectionInput;
}>;


export type CreateConnectionMutation = { __typename?: 'Mutation', createConnection: { __typename?: 'CreateConnectionResult', success: boolean, errors: Array<CreateConnectionError>, connection?: { __typename?: 'CustomConnection', id: string, name: string } | { __typename?: 'DHIS2Connection', id: string, name: string } | { __typename?: 'GCSConnection', id: string, name: string } | { __typename?: 'IASOConnection', id: string, name: string } | { __typename?: 'PostgreSQLConnection', id: string, name: string } | { __typename?: 'S3Connection', id: string, name: string } | null } };

export type CreateConnectionDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'CreateConnectionDialog_WorkspaceFragment' };

export type CreatePipelineDialog_WorkspaceFragment = (
  { __typename?: 'Workspace', slug: string }
  & { ' $fragmentRefs'?: { 'BucketObjectPicker_WorkspaceFragment': BucketObjectPicker_WorkspaceFragment } }
) & { ' $fragmentName'?: 'CreatePipelineDialog_WorkspaceFragment' };

export type CreateWorkspaceMutationVariables = Exact<{
  input: CreateWorkspaceInput;
}>;


export type CreateWorkspaceMutation = { __typename?: 'Mutation', createWorkspace: { __typename?: 'CreateWorkspaceResult', success: boolean, errors: Array<CreateWorkspaceError>, workspace?: { __typename?: 'Workspace', slug: string, name: string, description?: string | null, countries: Array<{ __typename?: 'Country', code: string, alpha3: string, name: string }> } | null } };

export type DatabaseTableDataGridQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  tableName: Scalars['String']['input'];
  orderBy: Scalars['String']['input'];
  direction: OrderByDirection;
  page: Scalars['Int']['input'];
}>;


export type DatabaseTableDataGridQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', table?: { __typename?: 'DatabaseTable', rows: { __typename?: 'TableRowsPage', pageNumber: number, hasNextPage: boolean, hasPreviousPage: boolean, items: Array<any> } } | null } } | null };

export type DatabaseTableDataGrid_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'DatabaseTableDataGrid_WorkspaceFragment' };

export type DatabaseTableDataGrid_TableFragment = { __typename?: 'DatabaseTable', name: string, columns: Array<{ __typename?: 'TableColumn', name: string }> } & { ' $fragmentName'?: 'DatabaseTableDataGrid_TableFragment' };

export type DatabaseVariablesSection_WorkspaceFragment = { __typename?: 'Workspace', slug: string, database: { __typename?: 'Database', credentials?: { __typename?: 'DatabaseCredentials', dbName: string, username: string, password: string, host: string, port: number, url: string } | null } } & { ' $fragmentName'?: 'DatabaseVariablesSection_WorkspaceFragment' };

export type DeleteBucketObject_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', deleteObject: boolean } } & { ' $fragmentName'?: 'DeleteBucketObject_WorkspaceFragment' };

export type DeleteBucketObject_ObjectFragment = { __typename?: 'BucketObject', key: string, name: string, type: BucketObjectType } & { ' $fragmentName'?: 'DeleteBucketObject_ObjectFragment' };

export type DeleteConnectionTrigger_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'DeleteConnectionTrigger_WorkspaceFragment' };

type DeleteConnectionTrigger_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteConnectionTrigger_Connection_CustomConnection_Fragment' };

type DeleteConnectionTrigger_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteConnectionTrigger_Connection_Dhis2Connection_Fragment' };

type DeleteConnectionTrigger_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteConnectionTrigger_Connection_GcsConnection_Fragment' };

type DeleteConnectionTrigger_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteConnectionTrigger_Connection_IasoConnection_Fragment' };

type DeleteConnectionTrigger_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteConnectionTrigger_Connection_PostgreSqlConnection_Fragment' };

type DeleteConnectionTrigger_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, name: string, permissions: { __typename?: 'ConnectionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteConnectionTrigger_Connection_S3Connection_Fragment' };

export type DeleteConnectionTrigger_ConnectionFragment = DeleteConnectionTrigger_Connection_CustomConnection_Fragment | DeleteConnectionTrigger_Connection_Dhis2Connection_Fragment | DeleteConnectionTrigger_Connection_GcsConnection_Fragment | DeleteConnectionTrigger_Connection_IasoConnection_Fragment | DeleteConnectionTrigger_Connection_PostgreSqlConnection_Fragment | DeleteConnectionTrigger_Connection_S3Connection_Fragment;

export type DatabaseTableDeleteTrigger_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', deleteDatabaseTable: boolean } } & { ' $fragmentName'?: 'DatabaseTableDeleteTrigger_WorkspaceFragment' };

export type DatabaseTableDeleteTrigger_DatabaseFragment = { __typename?: 'DatabaseTable', name: string } & { ' $fragmentName'?: 'DatabaseTableDeleteTrigger_DatabaseFragment' };

export type DeletePipelineMutationVariables = Exact<{
  input: DeletePipelineInput;
}>;


export type DeletePipelineMutation = { __typename?: 'Mutation', deletePipeline: { __typename?: 'DeletePipelineResult', success: boolean, errors: Array<PipelineError> } };

export type PipelineDelete_PipelineFragment = { __typename?: 'Pipeline', id: string, name?: string | null, code: string } & { ' $fragmentName'?: 'PipelineDelete_PipelineFragment' };

export type PipelineDelete_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'PipelineDelete_WorkspaceFragment' };

export type DeletePipelineVersionTrigger_VersionFragment = { __typename?: 'PipelineVersion', id: string, name?: string | null, pipeline: { __typename?: 'Pipeline', id: string }, permissions: { __typename?: 'PipelineVersionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeletePipelineVersionTrigger_VersionFragment' };

export type DeleteTemplateVersionTrigger_VersionFragment = { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', id: string }, permissions: { __typename?: 'PipelineTemplateVersionPermissions', delete: boolean } } & { ' $fragmentName'?: 'DeleteTemplateVersionTrigger_VersionFragment' };

export type DeleteWebappMutationVariables = Exact<{
  input: DeleteWebappInput;
}>;


export type DeleteWebappMutation = { __typename?: 'Mutation', deleteWebapp: { __typename?: 'DeleteWebappResult', success: boolean, errors: Array<DeleteWebappError> } };

export type WebappDelete_WebappFragment = { __typename?: 'Webapp', id: string, name: string } & { ' $fragmentName'?: 'WebappDelete_WebappFragment' };

export type WebappDelete_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'WebappDelete_WorkspaceFragment' };

export type DownloadBucketObject_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'DownloadBucketObject_WorkspaceFragment' };

export type DownloadBucketObject_ObjectFragment = { __typename?: 'BucketObject', key: string } & { ' $fragmentName'?: 'DownloadBucketObject_ObjectFragment' };

export type FileBrowserDialogQueryVariables = Exact<{
  slug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  prefix?: InputMaybe<Scalars['String']['input']>;
  query?: InputMaybe<Scalars['String']['input']>;
  workspaceSlugs?: InputMaybe<Array<Scalars['String']['input']> | Scalars['String']['input']>;
  useSearch: Scalars['Boolean']['input'];
}>;


export type FileBrowserDialogQuery = { __typename?: 'Query', searchResults?: { __typename?: 'FileResultPage', totalItems: number, totalPages: number, pageNumber: number, items: Array<{ __typename?: 'FileResult', score: number, file: { __typename?: 'File', name: string, key: string, path: string, type: FileType, updatedAt?: any | null, size?: any | null } }> }, workspace?: { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', objects: { __typename?: 'BucketObjectPage', pageNumber: number, hasNextPage: boolean, hasPreviousPage: boolean, items: Array<(
          { __typename?: 'BucketObject' }
          & { ' $fragmentRefs'?: { 'FileBrowserDialog_BucketObjectFragment': FileBrowserDialog_BucketObjectFragment } }
        )> } } } | null };

export type FileBrowserDialog_BucketObjectFragment = { __typename?: 'BucketObject', key: string, name: string, path: string, size?: any | null, updatedAt?: any | null, type: BucketObjectType } & { ' $fragmentName'?: 'FileBrowserDialog_BucketObjectFragment' };

export type FilesEditor_FileFragment = { __typename?: 'FileNode', id: string, name: string, path: string, type: FileType, content?: string | null, parentId?: string | null, autoSelect: boolean, language?: string | null, lineCount?: number | null } & { ' $fragmentName'?: 'FilesEditor_FileFragment' };

export type UploadPipelineMutationVariables = Exact<{
  input: UploadPipelineInput;
}>;


export type UploadPipelineMutation = { __typename?: 'Mutation', uploadPipeline: { __typename?: 'UploadPipelineResult', success: boolean, errors: Array<PipelineError>, details?: string | null, pipelineVersion?: (
      { __typename?: 'PipelineVersion', id: string, versionNumber: number, versionName: string, isLatestVersion: boolean }
      & { ' $fragmentRefs'?: { 'PipelineVersionPicker_VersionFragment': PipelineVersionPicker_VersionFragment } }
    ) | null } };

export type GenerateNewDatabasePasswordMutationVariables = Exact<{
  input: GenerateNewDatabasePasswordInput;
}>;


export type GenerateNewDatabasePasswordMutation = { __typename?: 'Mutation', generateNewDatabasePassword: { __typename?: 'GenerateNewDatabasePasswordResult', success: boolean, errors: Array<GenerateNewDatabasePasswordError> } };

export type GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment' };

export type GenerateWebhookPipelineWebhookUrlMutationVariables = Exact<{
  input: GeneratePipelineWebhookUrlInput;
}>;


export type GenerateWebhookPipelineWebhookUrlMutation = { __typename?: 'Mutation', generatePipelineWebhookUrl: { __typename?: 'GeneratePipelineWebhookUrlResult', success: boolean, errors: Array<GeneratePipelineWebhookUrlError>, pipeline?: { __typename?: 'Pipeline', id: string, code: string, webhookUrl?: string | null } | null } };

export type GeneratePipelineWebhookUrlDialog_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string } & { ' $fragmentName'?: 'GeneratePipelineWebhookUrlDialog_PipelineFragment' };

export type InviteWorkspaceMemberMutationVariables = Exact<{
  input: InviteWorkspaceMemberInput;
}>;


export type InviteWorkspaceMemberMutation = { __typename?: 'Mutation', inviteWorkspaceMember: { __typename?: 'InviteWorkspaceMemberResult', success: boolean, errors: Array<InviteWorkspaceMembershipError>, workspaceMembership?: { __typename?: 'WorkspaceMembership', id: string } | null } };

export type InviteMemberWorkspace_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string } & { ' $fragmentName'?: 'InviteMemberWorkspace_WorkspaceFragment' };

export type PipelineCard_PipelineFragment = (
  { __typename?: 'Pipeline', id: string, code: string, name?: string | null, schedule?: string | null, description?: string | null, type: PipelineType, sourceTemplate?: { __typename?: 'PipelineTemplate', id: string, name: string } | null, currentVersion?: { __typename?: 'PipelineVersion', versionName: string, createdAt: any, user?: (
      { __typename?: 'User' }
      & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
    ) | null } | null, lastRuns: { __typename?: 'PipelineRunPage', items: Array<(
      { __typename?: 'PipelineRun', executionDate?: any | null, user?: (
        { __typename?: 'User' }
        & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
      ) | null }
      & { ' $fragmentRefs'?: { 'PipelineRunStatusBadge_RunFragment': PipelineRunStatusBadge_RunFragment } }
    )> } }
  & { ' $fragmentRefs'?: { 'PipelineMetadataDisplay_PipelineFragment': PipelineMetadataDisplay_PipelineFragment } }
) & { ' $fragmentName'?: 'PipelineCard_PipelineFragment' };

export type PipelineCard_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'PipelineCard_WorkspaceFragment' };

export type DeletePipelineRecipientTrigger_RecipientFragment = { __typename?: 'PipelineRecipient', id: string, user: { __typename?: 'User', displayName: string } } & { ' $fragmentName'?: 'DeletePipelineRecipientTrigger_RecipientFragment' };

export type DeletePipelineRecipientTrigger_PipelineFragment = { __typename?: 'Pipeline', permissions: { __typename?: 'PipelinePermissions', update: boolean } } & { ' $fragmentName'?: 'DeletePipelineRecipientTrigger_PipelineFragment' };

export type PipelineRecipientsQueryVariables = Exact<{
  id: Scalars['UUID']['input'];
}>;


export type PipelineRecipientsQuery = { __typename?: 'Query', pipeline?: (
    { __typename?: 'Pipeline', recipients: Array<(
      { __typename?: 'PipelineRecipient', id: string, notificationLevel: PipelineNotificationLevel, user: { __typename?: 'User', id: string, displayName: string } }
      & { ' $fragmentRefs'?: { 'DeletePipelineRecipientTrigger_RecipientFragment': DeletePipelineRecipientTrigger_RecipientFragment } }
    )>, workspace: { __typename?: 'Workspace', slug: string, members: { __typename?: 'WorkspaceMembershipPage', totalItems: number } } }
    & { ' $fragmentRefs'?: { 'DeletePipelineRecipientTrigger_PipelineFragment': DeletePipelineRecipientTrigger_PipelineFragment } }
  ) | null };

export type PipelineRecipients_PipelineFragment = { __typename?: 'Pipeline', id: string, code: string, permissions: { __typename?: 'PipelinePermissions', update: boolean } } & { ' $fragmentName'?: 'PipelineRecipients_PipelineFragment' };

export type UpdatePipelineVersionConfigMutationVariables = Exact<{
  input: UpdatePipelineVersionInput;
}>;


export type UpdatePipelineVersionConfigMutation = { __typename?: 'Mutation', updatePipelineVersion: { __typename?: 'UpdatePipelineVersionResult', success: boolean, errors: Array<UpdatePipelineVersionError>, pipelineVersion?: { __typename?: 'PipelineVersion', id: string, config?: any | null } | null } };

export type PipelineVersionConfigDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, name?: string | null, description?: string | null, externalLink?: any | null, isLatestVersion: boolean, createdAt: any, config?: any | null, pipeline: { __typename?: 'Pipeline', id: string, schedule?: string | null, workspace: { __typename?: 'Workspace', slug: string } }, parameters: Array<(
    { __typename?: 'PipelineParameter' }
    & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
  )> } & { ' $fragmentName'?: 'PipelineVersionConfigDialog_VersionFragment' };

export type PipelineVersionPickerQueryVariables = Exact<{
  pipelineId: Scalars['UUID']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type PipelineVersionPickerQuery = { __typename?: 'Query', pipeline?: { __typename?: 'Pipeline', versions: { __typename?: 'PipelineVersionPage', pageNumber: number, totalPages: number, totalItems: number, items: Array<(
        { __typename?: 'PipelineVersion' }
        & { ' $fragmentRefs'?: { 'PipelineVersionPicker_VersionFragment': PipelineVersionPicker_VersionFragment } }
      )> } } | null };

export type PipelineVersionPicker_PipelineFragment = { __typename?: 'Pipeline', id: string } & { ' $fragmentName'?: 'PipelineVersionPicker_PipelineFragment' };

export type PipelineVersionPicker_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, parameters: Array<(
    { __typename?: 'PipelineParameter' }
    & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
  )>, user?: { __typename?: 'User', displayName: string } | null } & { ' $fragmentName'?: 'PipelineVersionPicker_VersionFragment' };

export type RunOutputsTable_WorkspaceFragment = (
  { __typename?: 'Workspace', slug: string, bucket: { __typename?: 'Bucket', name: string } }
  & { ' $fragmentRefs'?: { 'DownloadBucketObject_WorkspaceFragment': DownloadBucketObject_WorkspaceFragment } }
) & { ' $fragmentName'?: 'RunOutputsTable_WorkspaceFragment' };

export type RunOutputsTable_RunFragment = { __typename?: 'PipelineRun', id: string, outputs: Array<{ __typename: 'BucketObject', name: string, key: string, path: string, type: BucketObjectType } | { __typename: 'DatabaseTable', tableName: string } | { __typename: 'GenericOutput', genericName?: string | null, genericType: string, genericUri: string }>, datasetVersions: Array<{ __typename?: 'DatasetVersion', name: string, dataset: { __typename?: 'Dataset', slug: string, name: string, workspace?: { __typename?: 'Workspace', slug: string } | null } }> } & { ' $fragmentName'?: 'RunOutputsTable_RunFragment' };

export type GetConnectionBySlugDhis2QueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  connectionSlug: Scalars['String']['input'];
  type: Dhis2MetadataType;
  filters?: InputMaybe<Array<Scalars['String']['input']> | Scalars['String']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetConnectionBySlugDhis2Query = { __typename?: 'Query', connectionBySlug?: { __typename?: 'CustomConnection' } | { __typename?: 'DHIS2Connection', queryMetadata: { __typename?: 'DHIS2QueryResultPage', pageNumber: number, totalItems: number, error?: Dhis2ConnectionError | null, items?: Array<{ __typename?: 'DHIS2MetadataItem', id?: string | null, label: string }> | null } } | { __typename?: 'GCSConnection' } | { __typename?: 'IASOConnection' } | { __typename?: 'PostgreSQLConnection' } | { __typename?: 'S3Connection' } | null };

export type GetConnectionBySlugIasoQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  connectionSlug: Scalars['String']['input'];
  type: IasoMetadataType;
  search?: InputMaybe<Scalars['String']['input']>;
  filters?: InputMaybe<Array<IasoQueryFilterInput> | IasoQueryFilterInput>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
  page?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetConnectionBySlugIasoQuery = { __typename?: 'Query', connectionBySlug?: { __typename?: 'CustomConnection' } | { __typename?: 'DHIS2Connection' } | { __typename?: 'GCSConnection' } | { __typename?: 'IASOConnection', queryMetadata: { __typename?: 'IASOQueryResultPage', pageNumber: number, totalItems: number, error?: IasoConnectionError | null, items?: Array<{ __typename?: 'IASOMetadataItem', id?: number | null, label: string }> | null } } | { __typename?: 'PostgreSQLConnection' } | { __typename?: 'S3Connection' } | null };

export type ParameterField_ParameterFragment = { __typename?: 'PipelineParameter', code: string, name: string, help?: string | null, type: ParameterType, default?: any | null, required: boolean, choices?: Array<any> | null, connection?: string | null, widget?: ParameterWidget | null, multiple: boolean, directory?: string | null } & { ' $fragmentName'?: 'ParameterField_ParameterFragment' };

export type RunPipelineDialog_VersionFragment = { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<(
    { __typename?: 'PipelineParameter' }
    & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
  )> } & { ' $fragmentName'?: 'RunPipelineDialog_VersionFragment' };

export type PipelineCurrentVersionQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  pipelineCode: Scalars['String']['input'];
}>;


export type PipelineCurrentVersionQuery = { __typename?: 'Query', pipelineByCode?: { __typename?: 'Pipeline', currentVersion?: { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, config?: any | null, user?: { __typename?: 'User', displayName: string } | null, parameters: Array<(
        { __typename?: 'PipelineParameter' }
        & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
      )> } | null } | null };

export type RunPipelineDialog_PipelineFragment = (
  { __typename?: 'Pipeline', id: string, code: string, type: PipelineType, workspace: { __typename?: 'Workspace', slug: string }, permissions: { __typename?: 'PipelinePermissions', run: boolean }, currentVersion?: { __typename?: 'PipelineVersion', id: string } | null }
  & { ' $fragmentRefs'?: { 'PipelineVersionPicker_PipelineFragment': PipelineVersionPicker_PipelineFragment } }
) & { ' $fragmentName'?: 'RunPipelineDialog_PipelineFragment' };

export type RunPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string, config: any, version?: { __typename?: 'PipelineVersion', id: string, versionName: string, createdAt: any, parameters: Array<(
      { __typename?: 'PipelineParameter' }
      & { ' $fragmentRefs'?: { 'ParameterField_ParameterFragment': ParameterField_ParameterFragment } }
    )>, user?: { __typename?: 'User', displayName: string } | null } | null } & { ' $fragmentName'?: 'RunPipelineDialog_RunFragment' };

export type SidebarMenuQueryVariables = Exact<{
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type SidebarMenuQuery = { __typename?: 'Query', pendingWorkspaceInvitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number }, workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<{ __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', code: string, flag: string }> }> } };

export type SidebarMenu_WorkspaceFragment = { __typename?: 'Workspace', slug: string, name: string, countries: Array<{ __typename?: 'Country', flag: string, code: string }>, organization?: { __typename?: 'Organization', id: string, name: string, shortName?: string | null, permissions: { __typename?: 'OrganizationPermissions', createWorkspace: boolean } } | null } & { ' $fragmentName'?: 'SidebarMenu_WorkspaceFragment' };

export type StopPipelineMutationVariables = Exact<{
  input: StopPipelineInput;
}>;


export type StopPipelineMutation = { __typename?: 'Mutation', stopPipeline: { __typename?: 'StopPipelineResult', success: boolean, errors: Array<PipelineError> } };

export type StopPipelineDialog_RunFragment = { __typename?: 'PipelineRun', id: string } & { ' $fragmentName'?: 'StopPipelineDialog_RunFragment' };

export type StopPipelineDialog_PipelineFragment = { __typename?: 'Pipeline', code: string } & { ' $fragmentName'?: 'StopPipelineDialog_PipelineFragment' };

export type TemplateCard_TemplateFragment = (
  { __typename?: 'PipelineTemplate', id: string, code: string, name: string, description?: string | null, currentVersion?: { __typename?: 'PipelineTemplateVersion', id: string, createdAt: any, user?: (
      { __typename?: 'User' }
      & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
    ) | null } | null }
  & { ' $fragmentRefs'?: { 'PipelineMetadataDisplay_TemplateFragment': PipelineMetadataDisplay_TemplateFragment } }
) & { ' $fragmentName'?: 'TemplateCard_TemplateFragment' };

export type TemplateCard_WorkspaceFragment = { __typename?: 'Workspace', slug: string } & { ' $fragmentName'?: 'TemplateCard_WorkspaceFragment' };

type UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment = { __typename?: 'CustomConnection', id: string, name: string, type: ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } & { ' $fragmentName'?: 'UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment' };

type UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment = { __typename?: 'DHIS2Connection', id: string, name: string, type: ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } & { ' $fragmentName'?: 'UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment' };

type UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment = { __typename?: 'GCSConnection', id: string, name: string, type: ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } & { ' $fragmentName'?: 'UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment' };

type UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment = { __typename?: 'IASOConnection', id: string, name: string, type: ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } & { ' $fragmentName'?: 'UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment' };

type UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment = { __typename?: 'PostgreSQLConnection', id: string, name: string, type: ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } & { ' $fragmentName'?: 'UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment' };

type UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment = { __typename?: 'S3Connection', id: string, name: string, type: ConnectionType, fields: Array<{ __typename?: 'ConnectionField', code: string, value?: string | null, secret: boolean }> } & { ' $fragmentName'?: 'UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment' };

export type UpdateConnectionFieldsDialog_ConnectionFragment = UpdateConnectionFieldsDialog_Connection_CustomConnection_Fragment | UpdateConnectionFieldsDialog_Connection_Dhis2Connection_Fragment | UpdateConnectionFieldsDialog_Connection_GcsConnection_Fragment | UpdateConnectionFieldsDialog_Connection_IasoConnection_Fragment | UpdateConnectionFieldsDialog_Connection_PostgreSqlConnection_Fragment | UpdateConnectionFieldsDialog_Connection_S3Connection_Fragment;

export type UploadObjectDialog_WorkspaceFragment = { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', createObject: boolean } } & { ' $fragmentName'?: 'UploadObjectDialog_WorkspaceFragment' };

export type GetUsersQueryVariables = Exact<{
  query: Scalars['String']['input'];
  workspaceSlug?: InputMaybe<Scalars['String']['input']>;
  organizationId?: InputMaybe<Scalars['UUID']['input']>;
}>;


export type GetUsersQuery = { __typename?: 'Query', users: Array<(
    { __typename?: 'User' }
    & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
  )> };

export type UserPicker_UserFragment = (
  { __typename?: 'User' }
  & { ' $fragmentRefs'?: { 'User_UserFragment': User_UserFragment } }
) & { ' $fragmentName'?: 'UserPicker_UserFragment' };

export type WorkspaceConnectionPickerQueryVariables = Exact<{
  slug: Scalars['String']['input'];
}>;


export type WorkspaceConnectionPickerQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string }
    & { ' $fragmentRefs'?: { 'WorkspaceConnectionPicker_WorkspaceFragment': WorkspaceConnectionPicker_WorkspaceFragment } }
  ) | null };

export type WorkspaceConnectionPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string, connections: Array<{ __typename?: 'CustomConnection', id: string, name: string, slug: string, type: ConnectionType } | { __typename?: 'DHIS2Connection', id: string, name: string, slug: string, type: ConnectionType } | { __typename?: 'GCSConnection', id: string, name: string, slug: string, type: ConnectionType } | { __typename?: 'IASOConnection', id: string, name: string, slug: string, type: ConnectionType } | { __typename?: 'PostgreSQLConnection', id: string, name: string, slug: string, type: ConnectionType } | { __typename?: 'S3Connection', id: string, name: string, slug: string, type: ConnectionType }> } & { ' $fragmentName'?: 'WorkspaceConnectionPicker_WorkspaceFragment' };

export type DeleteWorkspaceInvitationMutationVariables = Exact<{
  input: DeleteWorkspaceInvitationInput;
}>;


export type DeleteWorkspaceInvitationMutation = { __typename?: 'Mutation', deleteWorkspaceInvitation: { __typename?: 'DeleteWorkspaceInvitationResult', success: boolean, errors: Array<DeleteWorkspaceInvitationError> } };

export type DeleteWorkspaceInvitation_WorkspaceInvitationFragment = { __typename?: 'WorkspaceInvitation', id: string, email: string } & { ' $fragmentName'?: 'DeleteWorkspaceInvitation_WorkspaceInvitationFragment' };

export type ResendWorkspaceInvitationMutationVariables = Exact<{
  input: ResendWorkspaceInvitationInput;
}>;


export type ResendWorkspaceInvitationMutation = { __typename?: 'Mutation', resendWorkspaceInvitation: { __typename?: 'ResendWorkspaceInvitationResult', success: boolean, errors: Array<ResendWorkspaceInvitationError> } };

export type ResendWorkspaceInvitation_WorkspaceInvitationFragment = { __typename?: 'WorkspaceInvitation', id: string, email: string } & { ' $fragmentName'?: 'ResendWorkspaceInvitation_WorkspaceInvitationFragment' };

export type WorkspaceInvitationsQueryVariables = Exact<{
  slug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspaceInvitationsQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean }, invitations: { __typename?: 'WorkspaceInvitationPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceInvitation', id: string, role: WorkspaceMembershipRole, email: string, status: WorkspaceInvitationStatus, createdAt: any, invitedBy?: { __typename?: 'User', displayName: string } | null }> } } | null };

export type WorkspaceMemberPickerQueryVariables = Exact<{
  slug: Scalars['String']['input'];
}>;


export type WorkspaceMemberPickerQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string }
    & { ' $fragmentRefs'?: { 'WorkspaceMemberPicker_WorkspaceFragment': WorkspaceMemberPicker_WorkspaceFragment } }
  ) | null };

export type WorkspaceMemberPicker_WorkspaceFragment = { __typename?: 'Workspace', slug: string, members: { __typename?: 'WorkspaceMembershipPage', items: Array<{ __typename?: 'WorkspaceMembership', id: string, user: { __typename?: 'User', id: string, displayName: string } }> } } & { ' $fragmentName'?: 'WorkspaceMemberPicker_WorkspaceFragment' };

export type DeleteWorkspaceMemberMutationVariables = Exact<{
  input: DeleteWorkspaceMemberInput;
}>;


export type DeleteWorkspaceMemberMutation = { __typename?: 'Mutation', deleteWorkspaceMember: { __typename?: 'DeleteWorkspaceMemberResult', success: boolean, errors: Array<DeleteWorkspaceMemberError> } };

export type DeleteWorkspaceMember_WorkspaceMemberFragment = { __typename?: 'WorkspaceMembership', id: string, user: { __typename?: 'User', id: string, displayName: string }, organizationMembership?: { __typename?: 'OrganizationMembership', role: OrganizationMembershipRole } | null } & { ' $fragmentName'?: 'DeleteWorkspaceMember_WorkspaceMemberFragment' };

export type UpdateWorkspaceMemberMutationVariables = Exact<{
  input: UpdateWorkspaceMemberInput;
}>;


export type UpdateWorkspaceMemberMutation = { __typename?: 'Mutation', updateWorkspaceMember: { __typename?: 'UpdateWorkspaceMemberResult', success: boolean, errors: Array<UpdateWorkspaceMemberError>, workspaceMembership?: { __typename?: 'WorkspaceMembership', id: string, role: WorkspaceMembershipRole } | null } };

export type UpdateWorkspaceMember_WorkspaceMemberFragment = { __typename?: 'WorkspaceMembership', id: string, role: WorkspaceMembershipRole } & { ' $fragmentName'?: 'UpdateWorkspaceMember_WorkspaceMemberFragment' };

export type WorskspaceMembersQueryVariables = Exact<{
  slug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorskspaceMembersQuery = { __typename?: 'Query', workspace?: { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean }, members: { __typename?: 'WorkspaceMembershipPage', totalItems: number, items: Array<{ __typename?: 'WorkspaceMembership', id: string, role: WorkspaceMembershipRole, createdAt: any, user: { __typename?: 'User', id: string, displayName: string, email: string }, organizationMembership?: { __typename?: 'OrganizationMembership', role: OrganizationMembershipRole } | null }> } } | null };

export type WorkspacePickerQueryVariables = Exact<{
  query?: InputMaybe<Scalars['String']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspacePickerQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', totalItems: number, items: Array<(
      { __typename?: 'Workspace' }
      & { ' $fragmentRefs'?: { 'WorkspacePicker_ValueFragment': WorkspacePicker_ValueFragment } }
    )> } };

export type WorkspacePicker_ValueFragment = { __typename?: 'Workspace', slug: string, name: string } & { ' $fragmentName'?: 'WorkspacePicker_ValueFragment' };

export type DeleteWorkspaceMutationVariables = Exact<{
  input: DeleteWorkspaceInput;
}>;


export type DeleteWorkspaceMutation = { __typename?: 'Mutation', deleteWorkspace: { __typename?: 'DeleteWorkspaceResult', success: boolean, errors: Array<DeleteWorkspaceError> } };

export type CreatePipelineMutationVariables = Exact<{
  input: CreatePipelineInput;
}>;


export type CreatePipelineMutation = { __typename?: 'Mutation', createPipeline: { __typename?: 'CreatePipelineResult', success: boolean, errors: Array<PipelineError>, pipeline?: { __typename?: 'Pipeline', code: string } | null } };

export type DeletePipelineVersionMutationVariables = Exact<{
  input: DeletePipelineVersionInput;
}>;


export type DeletePipelineVersionMutation = { __typename?: 'Mutation', deletePipelineVersion: { __typename?: 'DeletePipelineVersionResult', success: boolean, errors: Array<DeletePipelineVersionError> } };

export type AddPipelineRecipientMutationVariables = Exact<{
  input: CreatePipelineRecipientInput;
}>;


export type AddPipelineRecipientMutation = { __typename?: 'Mutation', addPipelineRecipient: { __typename?: 'AddPipelineRecipientResult', success: boolean, errors: Array<PipelineRecipientError> } };

export type WorkspacesPageQueryVariables = Exact<{ [key: string]: never; }>;


export type WorkspacesPageQuery = { __typename?: 'Query', workspaces: { __typename?: 'WorkspacePage', items: Array<{ __typename?: 'Workspace', slug: string }> } };

export type WorkspacePipelineStartPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
}>;


export type WorkspacePipelineStartPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null };

export type WorkspaceTemplatesPageQueryVariables = Exact<{
  workspaceSlug: Scalars['String']['input'];
  page?: InputMaybe<Scalars['Int']['input']>;
  perPage?: InputMaybe<Scalars['Int']['input']>;
}>;


export type WorkspaceTemplatesPageQuery = { __typename?: 'Query', workspace?: (
    { __typename?: 'Workspace', slug: string, name: string }
    & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
  ) | null, pipelineTemplates: { __typename?: 'PipelineTemplatePage', totalItems: number, totalPages: number, pageNumber: number, items: Array<(
      { __typename?: 'PipelineTemplate' }
      & { ' $fragmentRefs'?: { 'TemplateCard_TemplateFragment': TemplateCard_TemplateFragment } }
    )> } };

export type GetTemplateVersionForDownloadQueryVariables = Exact<{
  versionId: Scalars['UUID']['input'];
}>;


export type GetTemplateVersionForDownloadQuery = { __typename?: 'Query', pipelineTemplateVersion?: { __typename?: 'PipelineTemplateVersion', id: string, versionNumber: number, template: { __typename?: 'PipelineTemplate', code: string }, sourcePipelineVersion: { __typename?: 'PipelineVersion', zipfile: string } } | null };

export type GetFileDownloadUrlMutationVariables = Exact<{
  input: PrepareObjectDownloadInput;
}>;


export type GetFileDownloadUrlMutation = { __typename?: 'Mutation', prepareObjectDownload: { __typename?: 'PrepareObjectDownloadResult', success: boolean, downloadUrl?: any | null } };

export type DeleteBucketObjectMutationVariables = Exact<{
  input: DeleteBucketObjectInput;
}>;


export type DeleteBucketObjectMutation = { __typename?: 'Mutation', deleteBucketObject: { __typename?: 'DeleteBucketObjectResult', success: boolean, errors: Array<DeleteBucketObjectError> } };

export type GetBucketUploadUrlMutationVariables = Exact<{
  input: PrepareObjectUploadInput;
}>;


export type GetBucketUploadUrlMutation = { __typename?: 'Mutation', prepareObjectUpload: { __typename?: 'PrepareObjectUploadResult', success: boolean, uploadUrl?: any | null } };

export type CreateBucketFolderMutationVariables = Exact<{
  input: CreateBucketFolderInput;
}>;


export type CreateBucketFolderMutation = { __typename?: 'Mutation', createBucketFolder: { __typename?: 'CreateBucketFolderResult', success: boolean, errors: Array<CreateBucketFolderError>, folder?: { __typename?: 'BucketObject', key: string, name: string, type: BucketObjectType } | null } };

export type DeleteConnectionMutationVariables = Exact<{
  input: DeleteConnectionInput;
}>;


export type DeleteConnectionMutation = { __typename?: 'Mutation', deleteConnection: { __typename?: 'DeleteConnectionResult', success: boolean, errors: Array<DeleteConnectionError> } };

export type DeleteWorkspaceDatabaseTableMutationVariables = Exact<{
  input: DeleteWorkspaceDatabaseTableInput;
}>;


export type DeleteWorkspaceDatabaseTableMutation = { __typename?: 'Mutation', deleteWorkspaceDatabaseTable?: { __typename?: 'DeleteWorkspaceDatabaseTableResult', success: boolean, errors: Array<DeleteWorkspaceDatabaseTableError> } | null };

export type LaunchNotebookServerMutationVariables = Exact<{
  input: LaunchNotebookServerInput;
}>;


export type LaunchNotebookServerMutation = { __typename?: 'Mutation', launchNotebookServer: { __typename?: 'LaunchNotebookServerResult', success: boolean, server?: { __typename?: 'NotebookServer', name: string, ready: boolean, url: string } | null } };

export type UpdateWorkspacePipelineMutationVariables = Exact<{
  input: UpdatePipelineInput;
}>;


export type UpdateWorkspacePipelineMutation = { __typename?: 'Mutation', updatePipeline: { __typename?: 'UpdatePipelineResult', success: boolean, errors: Array<UpdatePipelineError>, pipeline?: { __typename?: 'Pipeline', id: string, name?: string | null, description?: string | null, schedule?: string | null, config: any, functionalType?: PipelineFunctionalType | null, updatedAt?: any | null, webhookEnabled: boolean, webhookUrl?: string | null, autoUpdateFromTemplate: boolean, tags: Array<(
        { __typename?: 'Tag' }
        & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
      )>, recipients: Array<{ __typename?: 'PipelineRecipient', user: { __typename?: 'User', id: string, displayName: string } }> } | null } };

export type RunWorkspacePipelineMutationVariables = Exact<{
  input: RunPipelineInput;
}>;


export type RunWorkspacePipelineMutation = { __typename?: 'Mutation', runPipeline: { __typename?: 'RunPipelineResult', success: boolean, errors: Array<PipelineError>, run?: { __typename?: 'PipelineRun', id: string, pipeline: { __typename: 'Pipeline', id: string } } | null } };

export type NewRunFragment = { __typename?: 'PipelineRun', id: string } & { ' $fragmentName'?: 'NewRunFragment' };

export type DeletePipelineVersionMutationVariables = Exact<{
  input: DeletePipelineVersionInput;
}>;


export type DeletePipelineVersionMutation = { __typename?: 'Mutation', deletePipelineVersion: { __typename?: 'DeletePipelineVersionResult', success: boolean, errors: Array<DeletePipelineVersionError> } };

export type UpdatePipelineRecipientMutationVariables = Exact<{
  input: UpdatePipelineRecipientInput;
}>;


export type UpdatePipelineRecipientMutation = { __typename?: 'Mutation', updatePipelineRecipient: { __typename?: 'UpdatePipelineRecipientResult', success: boolean, errors: Array<PipelineRecipientError>, recipient?: { __typename?: 'PipelineRecipient', id: string, notificationLevel: PipelineNotificationLevel } | null } };

export type DeletePipelineRecipientMutationVariables = Exact<{
  input: DeletePipelineRecipientInput;
}>;


export type DeletePipelineRecipientMutation = { __typename?: 'Mutation', deletePipelineRecipient: { __typename?: 'DeletePipelineRecipientResult', success: boolean, errors: Array<PipelineRecipientError> } };

export type UpdateWorkspaceTemplateMutationVariables = Exact<{
  input: UpdateTemplateInput;
}>;


export type UpdateWorkspaceTemplateMutation = { __typename?: 'Mutation', updatePipelineTemplate: { __typename?: 'UpdateTemplateResult', success: boolean, errors: Array<UpdateTemplateError>, template?: { __typename?: 'PipelineTemplate', id: string, name: string, description?: string | null, config?: string | null, functionalType?: PipelineFunctionalType | null, tags: Array<(
        { __typename?: 'Tag' }
        & { ' $fragmentRefs'?: { 'Tag_TagFragment': Tag_TagFragment } }
      )> } | null } };

export type DeleteTemplateVersionMutationVariables = Exact<{
  input: DeleteTemplateVersionInput;
}>;


export type DeleteTemplateVersionMutation = { __typename?: 'Mutation', deleteTemplateVersion: { __typename?: 'DeleteTemplateVersionResult', success: boolean, errors: Array<DeleteTemplateVersionError> } };

export type PipelineLayout_WorkspaceFragment = (
  { __typename?: 'Workspace' }
  & { ' $fragmentRefs'?: { 'TabLayout_WorkspaceFragment': TabLayout_WorkspaceFragment } }
) & { ' $fragmentName'?: 'PipelineLayout_WorkspaceFragment' };

export type PipelineLayout_PipelineFragment = (
  { __typename?: 'Pipeline', id: string, code: string, name?: string | null, permissions: { __typename?: 'PipelinePermissions', run: boolean, delete: boolean, update: boolean, createTemplateVersion: { __typename?: 'CreateTemplateVersionPermission', isAllowed: boolean, reasons: Array<CreateTemplateVersionPermissionReason> } }, template?: { __typename?: 'PipelineTemplate', id: string, name: string, code: string } | null, currentVersion?: (
    { __typename?: 'PipelineVersion', id: string, name?: string | null, description?: string | null, config?: any | null, externalLink?: any | null, templateVersion?: { __typename?: 'PipelineTemplateVersion', id: string } | null }
    & { ' $fragmentRefs'?: { 'PipelineVersionPicker_VersionFragment': PipelineVersionPicker_VersionFragment;'DownloadPipelineVersion_VersionFragment': DownloadPipelineVersion_VersionFragment } }
  ) | null }
  & { ' $fragmentRefs'?: { 'RunPipelineDialog_PipelineFragment': RunPipelineDialog_PipelineFragment } }
) & { ' $fragmentName'?: 'PipelineLayout_PipelineFragment' };

export type TabLayout_WorkspaceFragment = (
  { __typename?: 'Workspace', name: string }
  & { ' $fragmentRefs'?: { 'WorkspaceLayout_WorkspaceFragment': WorkspaceLayout_WorkspaceFragment } }
) & { ' $fragmentName'?: 'TabLayout_WorkspaceFragment' };

export type TemplateLayout_WorkspaceFragment = (
  { __typename?: 'Workspace' }
  & { ' $fragmentRefs'?: { 'TabLayout_WorkspaceFragment': TabLayout_WorkspaceFragment } }
) & { ' $fragmentName'?: 'TemplateLayout_WorkspaceFragment' };

export type TemplateLayout_TemplateFragment = { __typename?: 'PipelineTemplate', id: string, code: string, name: string, permissions: { __typename?: 'PipelineTemplatePermissions', delete: boolean, update: boolean }, currentVersion?: (
    { __typename?: 'PipelineTemplateVersion', id: string }
    & { ' $fragmentRefs'?: { 'DownloadTemplateVersion_VersionFragment': DownloadTemplateVersion_VersionFragment } }
  ) | null } & { ' $fragmentName'?: 'TemplateLayout_TemplateFragment' };

export type Sidebar_WorkspaceFragment = (
  { __typename?: 'Workspace', slug: string, permissions: { __typename?: 'WorkspacePermissions', manageMembers: boolean, update: boolean, launchNotebookServer: boolean } }
  & { ' $fragmentRefs'?: { 'SidebarMenu_WorkspaceFragment': SidebarMenu_WorkspaceFragment } }
) & { ' $fragmentName'?: 'Sidebar_WorkspaceFragment' };

export type WorkspaceLayout_WorkspaceFragment = (
  { __typename?: 'Workspace', slug: string }
  & { ' $fragmentRefs'?: { 'Sidebar_WorkspaceFragment': Sidebar_WorkspaceFragment } }
) & { ' $fragmentName'?: 'WorkspaceLayout_WorkspaceFragment' };

export const UserAvatar_UserFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}}]} as unknown as DocumentNode<UserAvatar_UserFragment, unknown>;
export const User_UserFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}}]} as unknown as DocumentNode<User_UserFragment, unknown>;
export const UserColumn_UserFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserColumn_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<UserColumn_UserFragment, unknown>;
export const CountryBadge_CountryFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CountryBadge_country"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Country"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<CountryBadge_CountryFragment, unknown>;
export const CountryPicker_CountryFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CountryPicker_country"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Country"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"alpha3"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<CountryPicker_CountryFragment, unknown>;
export const WorkspaceDisplayFragmentFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<WorkspaceDisplayFragmentFragment, unknown>;
export const DatabaseTablesPageFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTablesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTableResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"databaseTable"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"count"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<DatabaseTablesPageFragment, unknown>;
export const DatasetsPageFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetsPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}}]} as unknown as DocumentNode<DatasetsPageFragment, unknown>;
export const FilesPageFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FilesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"FileResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"file"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<FilesPageFragment, unknown>;
export const Tag_TagFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<Tag_TagFragment, unknown>;
export const UsePipelineRunPoller_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]} as unknown as DocumentNode<UsePipelineRunPoller_RunFragment, unknown>;
export const PipelineRunStatusBadge_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]} as unknown as DocumentNode<PipelineRunStatusBadge_RunFragment, unknown>;
export const PipelinesPageFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelinesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"lastRuns"},"name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"EnumValue","value":"EXECUTION_DATE_DESC"}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}}]} as unknown as DocumentNode<PipelinesPageFragment, unknown>;
export const PipelineTemplatesPageFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineTemplatesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}}]}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<PipelineTemplatesPageFragment, unknown>;
export const CreateDatasetDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreateDatasetDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createDataset"}}]}}]}}]} as unknown as DocumentNode<CreateDatasetDialog_WorkspaceFragment, unknown>;
export const DatasetCard_LinkFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetCard_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]} as unknown as DocumentNode<DatasetCard_LinkFragment, unknown>;
export const DownloadVersionFile_FileFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadVersionFile_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}}]}}]} as unknown as DocumentNode<DownloadVersionFile_FileFragment, unknown>;
export const DatasetVersionFileSample_FileFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"attachment"},"value":{"kind":"BooleanValue","value":false}}]}]}}]} as unknown as DocumentNode<DatasetVersionFileSample_FileFragment, unknown>;
export const ColumnMetadataDrawer_FileFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"targetId"}},{"kind":"Field","name":{"kind":"Name","value":"attributes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"system"}},{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"Field","name":{"kind":"Name","value":"properties"}}]}}]} as unknown as DocumentNode<ColumnMetadataDrawer_FileFragment, unknown>;
export const DatasetVersionFileColumns_FileFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"targetId"}},{"kind":"Field","name":{"kind":"Name","value":"attributes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"system"}},{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"Field","name":{"kind":"Name","value":"properties"}}]}}]} as unknown as DocumentNode<DatasetVersionFileColumns_FileFragment, unknown>;
export const DatasetExplorer_FileFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetExplorer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadVersionFile_file"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileSample_file"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"targetId"}},{"kind":"Field","name":{"kind":"Name","value":"attributes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"system"}},{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"Field","name":{"kind":"Name","value":"properties"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadVersionFile_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"attachment"},"value":{"kind":"BooleanValue","value":false}}]}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"}}]}}]} as unknown as DocumentNode<DatasetExplorer_FileFragment, unknown>;
export const DatasetVersionFileSample_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}}]} as unknown as DocumentNode<DatasetVersionFileSample_VersionFragment, unknown>;
export const DatasetVersionFileColumns_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}}]} as unknown as DocumentNode<DatasetVersionFileColumns_VersionFragment, unknown>;
export const DatasetExplorer_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetExplorer_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetExplorer_file"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileSample_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileColumns_version"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadVersionFile_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"attachment"},"value":{"kind":"BooleanValue","value":false}}]}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"targetId"}},{"kind":"Field","name":{"kind":"Name","value":"attributes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"system"}},{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"Field","name":{"kind":"Name","value":"properties"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetExplorer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadVersionFile_file"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileSample_file"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}}]} as unknown as DocumentNode<DatasetExplorer_VersionFragment, unknown>;
export const DatasetLinksDataGrid_DatasetFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLinksDataGrid_dataset"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Dataset"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<DatasetLinksDataGrid_DatasetFragment, unknown>;
export const DatasetPicker_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"datasets"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]} as unknown as DocumentNode<DatasetPicker_WorkspaceFragment, unknown>;
export const DatasetVersionFilesDataGrid_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFilesDataGrid_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"download"}}]}}]}}]} as unknown as DocumentNode<DatasetVersionFilesDataGrid_VersionFragment, unknown>;
export const DatasetVersionPicker_DatasetFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_dataset"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Dataset"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<DatasetVersionPicker_DatasetFragment, unknown>;
export const DeleteDatasetLinkTrigger_DatasetLinkFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteDatasetLinkTrigger_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<DeleteDatasetLinkTrigger_DatasetLinkFragment, unknown>;
export const DeleteDatasetTrigger_DatasetFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteDatasetTrigger_dataset"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Dataset"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<DeleteDatasetTrigger_DatasetFragment, unknown>;
export const LinkDatasetDialog_DatasetFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"LinkDatasetDialog_dataset"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Dataset"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<LinkDatasetDialog_DatasetFragment, unknown>;
export const SidebarMenu_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}}]} as unknown as DocumentNode<SidebarMenu_WorkspaceFragment, unknown>;
export const Sidebar_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}}]} as unknown as DocumentNode<Sidebar_WorkspaceFragment, unknown>;
export const WorkspaceLayout_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}}]} as unknown as DocumentNode<WorkspaceLayout_WorkspaceFragment, unknown>;
export const DatasetLayout_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<DatasetLayout_WorkspaceFragment, unknown>;
export const UploadDatasetVersionDialog_DatasetLinkFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]} as unknown as DocumentNode<UploadDatasetVersionDialog_DatasetLinkFragment, unknown>;
export const PinDatasetButton_LinkFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PinDatasetButton_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pin"}}]}}]}}]} as unknown as DocumentNode<PinDatasetButton_LinkFragment, unknown>;
export const DatasetLayout_DatasetLinkFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PinDatasetButton_link"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"createVersion"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PinDatasetButton_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pin"}}]}}]}}]} as unknown as DocumentNode<DatasetLayout_DatasetLinkFragment, unknown>;
export const DatasetVersionPicker_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]} as unknown as DocumentNode<DatasetVersionPicker_VersionFragment, unknown>;
export const DatasetLayout_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionPicker_version"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]} as unknown as DocumentNode<DatasetLayout_VersionFragment, unknown>;
export const WorkspaceRoleFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceRole"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"WorkspaceMembership"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]} as unknown as DocumentNode<WorkspaceRoleFragment, unknown>;
export const UpdateOrganizationMemberDialog_OrganizationMemberFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpdateOrganizationMemberDialog_organizationMember"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"OrganizationMembership"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspaceMemberships"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"email"}}]}}]}}]} as unknown as DocumentNode<UpdateOrganizationMemberDialog_OrganizationMemberFragment, unknown>;
export const UpdateOrganizationMemberDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpdateOrganizationMemberDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<UpdateOrganizationMemberDialog_WorkspaceFragment, unknown>;
export const Organization_OrganizationFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Organization_organization"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Organization"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"archiveWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"manageOwners"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}}]}}]} as unknown as DocumentNode<Organization_OrganizationFragment, unknown>;
export const OrganizationDataset_LinkFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"OrganizationDataset_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"sharedWithOrganization"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"links"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"50"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]}}]} as unknown as DocumentNode<OrganizationDataset_LinkFragment, unknown>;
export const OrganizationWorkspace_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"OrganizationWorkspace_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}}]} as unknown as DocumentNode<OrganizationWorkspace_WorkspaceFragment, unknown>;
export const PipelineTemplateDialog_PipelineTemplateFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineTemplateDialog_pipelineTemplate"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<PipelineTemplateDialog_PipelineTemplateFragment, unknown>;
export const PipelineRunReadonlyForm_DagFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"formCode"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<PipelineRunReadonlyForm_DagFragment, unknown>;
export const PipelineRunDataCard_DagFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunDataCard_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dag"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"formCode"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<PipelineRunDataCard_DagFragment, unknown>;
export const PipelineRunOutputEntry_OutputFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunOutputEntry_output"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRunOutput"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"title"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}}]} as unknown as DocumentNode<PipelineRunOutputEntry_OutputFragment, unknown>;
export const UserProperty_UserFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserProperty_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<UserProperty_UserFragment, unknown>;
export const RunMessages_DagRunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunMessages_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"priority"}}]}}]}}]} as unknown as DocumentNode<RunMessages_DagRunFragment, unknown>;
export const RunLogs_DagRunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunLogs_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"logs"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]} as unknown as DocumentNode<RunLogs_DagRunFragment, unknown>;
export const PipelineRunReadonlyForm_DagRunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"config"}}]}}]} as unknown as DocumentNode<PipelineRunReadonlyForm_DagRunFragment, unknown>;
export const PipelineRunFavoriteIcon_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}}]} as unknown as DocumentNode<PipelineRunFavoriteIcon_RunFragment, unknown>;
export const PipelineRunFavoriteTrigger_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}}]} as unknown as DocumentNode<PipelineRunFavoriteTrigger_RunFragment, unknown>;
export const PipelineRunDataCard_DagRunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunDataCard_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"externalUrl"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"triggerMode"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}},{"kind":"Field","name":{"kind":"Name","value":"outputs"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunOutputEntry_output"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserProperty_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"progress"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunMessages_dagRun"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunLogs_dagRun"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dagRun"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunOutputEntry_output"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRunOutput"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"title"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserProperty_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunMessages_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"priority"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunLogs_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"logs"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"config"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"}}]}}]} as unknown as DocumentNode<PipelineRunDataCard_DagRunFragment, unknown>;
export const PipelineRunForm_DagFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunForm_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"sampleConfig"}}]}},{"kind":"Field","name":{"kind":"Name","value":"formCode"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<PipelineRunForm_DagFragment, unknown>;
export const PipelineTemplates_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineTemplates_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<PipelineTemplates_WorkspaceFragment, unknown>;
export const ParameterField_ParameterFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<ParameterField_ParameterFragment, unknown>;
export const DownloadPipelineVersion_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<DownloadPipelineVersion_VersionFragment, unknown>;
export const DeletePipelineVersionTrigger_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineVersionTrigger_VersionFragment, unknown>;
export const PipelineVersionCard_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionCard_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<PipelineVersionCard_VersionFragment, unknown>;
export const PipelineVersionParametersTable_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionParametersTable_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"config"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<PipelineVersionParametersTable_VersionFragment, unknown>;
export const Pipelines_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Pipelines_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<Pipelines_WorkspaceFragment, unknown>;
export const PipelinesPicker_ValueFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelinesPicker_value"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}}]}}]} as unknown as DocumentNode<PipelinesPicker_ValueFragment, unknown>;
export const PipelinePublish_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelinePublish_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]} as unknown as DocumentNode<PipelinePublish_PipelineFragment, unknown>;
export const PipelinePublish_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelinePublish_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<PipelinePublish_WorkspaceFragment, unknown>;
export const RunLogs_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunLogs_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"logs"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]} as unknown as DocumentNode<RunLogs_RunFragment, unknown>;
export const RunMessages_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunMessages_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"priority"}}]}}]}}]} as unknown as DocumentNode<RunMessages_RunFragment, unknown>;
export const DeleteTemplateVersionTrigger_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<DeleteTemplateVersionTrigger_VersionFragment, unknown>;
export const TemplateVersionCard_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateVersionCard_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<TemplateVersionCard_VersionFragment, unknown>;
export const UpgradePipelineFromTemplateDialog_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpgradePipelineFromTemplateDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"newTemplateVersions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]} as unknown as DocumentNode<UpgradePipelineFromTemplateDialog_PipelineFragment, unknown>;
export const FavoriteWebappButton_WebappFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FavoriteWebappButton_webapp"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Webapp"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}}]} as unknown as DocumentNode<FavoriteWebappButton_WebappFragment, unknown>;
export const WebappCard_WebappFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappCard_webapp"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Webapp"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"icon"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]} as unknown as DocumentNode<WebappCard_WebappFragment, unknown>;
export const WebappForm_WebappFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappForm_webapp"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Webapp"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"icon"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<WebappForm_WebappFragment, unknown>;
export const WebappForm_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappForm_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<WebappForm_WorkspaceFragment, unknown>;
export const ArchiveWorkspace_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ArchiveWorkspace_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<ArchiveWorkspace_WorkspaceFragment, unknown>;
export const DownloadBucketObject_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<DownloadBucketObject_WorkspaceFragment, unknown>;
export const DeleteBucketObject_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteObject"}}]}}]}}]} as unknown as DocumentNode<DeleteBucketObject_WorkspaceFragment, unknown>;
export const BucketExplorer_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketExplorer_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadBucketObject_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteBucketObject_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteObject"}}]}}]}}]} as unknown as DocumentNode<BucketExplorer_WorkspaceFragment, unknown>;
export const DownloadBucketObject_ObjectFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_object"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}}]}}]} as unknown as DocumentNode<DownloadBucketObject_ObjectFragment, unknown>;
export const DeleteBucketObject_ObjectFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteBucketObject_object"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]} as unknown as DocumentNode<DeleteBucketObject_ObjectFragment, unknown>;
export const BucketExplorer_ObjectsFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketExplorer_objects"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObjectPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadBucketObject_object"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteBucketObject_object"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_object"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteBucketObject_object"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]} as unknown as DocumentNode<BucketExplorer_ObjectsFragment, unknown>;
export const UpdateConnectionFieldsDialog_ConnectionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpdateConnectionFieldsDialog_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"secret"}}]}}]}}]} as unknown as DocumentNode<UpdateConnectionFieldsDialog_ConnectionFragment, unknown>;
export const ConnectionFieldsSection_ConnectionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ConnectionFieldsSection_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"secret"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UpdateConnectionFieldsDialog_connection"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpdateConnectionFieldsDialog_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"secret"}}]}}]}}]} as unknown as DocumentNode<ConnectionFieldsSection_ConnectionFragment, unknown>;
export const ConnectionUsageSnippets_ConnectionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ConnectionUsageSnippets_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<ConnectionUsageSnippets_ConnectionFragment, unknown>;
export const CreateBucketFolderDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreateBucketFolderDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createObject"}}]}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]} as unknown as DocumentNode<CreateBucketFolderDialog_WorkspaceFragment, unknown>;
export const CreateConnectionDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreateConnectionDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<CreateConnectionDialog_WorkspaceFragment, unknown>;
export const BucketObjectPicker_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketObjectPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<BucketObjectPicker_WorkspaceFragment, unknown>;
export const CreatePipelineDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreatePipelineDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"BucketObjectPicker_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketObjectPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<CreatePipelineDialog_WorkspaceFragment, unknown>;
export const DatabaseTableDataGrid_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTableDataGrid_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<DatabaseTableDataGrid_WorkspaceFragment, unknown>;
export const DatabaseTableDataGrid_TableFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTableDataGrid_table"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTable"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"columns"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]} as unknown as DocumentNode<DatabaseTableDataGrid_TableFragment, unknown>;
export const DatabaseVariablesSection_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseVariablesSection_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"database"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"credentials"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dbName"}},{"kind":"Field","name":{"kind":"Name","value":"username"}},{"kind":"Field","name":{"kind":"Name","value":"password"}},{"kind":"Field","name":{"kind":"Name","value":"host"}},{"kind":"Field","name":{"kind":"Name","value":"port"}},{"kind":"Field","name":{"kind":"Name","value":"url"}}]}}]}}]}}]} as unknown as DocumentNode<DatabaseVariablesSection_WorkspaceFragment, unknown>;
export const DeleteConnectionTrigger_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteConnectionTrigger_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<DeleteConnectionTrigger_WorkspaceFragment, unknown>;
export const DeleteConnectionTrigger_ConnectionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteConnectionTrigger_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<DeleteConnectionTrigger_ConnectionFragment, unknown>;
export const DatabaseTableDeleteTrigger_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTableDeleteTrigger_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteDatabaseTable"}}]}}]}}]} as unknown as DocumentNode<DatabaseTableDeleteTrigger_WorkspaceFragment, unknown>;
export const DatabaseTableDeleteTrigger_DatabaseFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTableDeleteTrigger_database"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTable"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<DatabaseTableDeleteTrigger_DatabaseFragment, unknown>;
export const PipelineDelete_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineDelete_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]} as unknown as DocumentNode<PipelineDelete_PipelineFragment, unknown>;
export const PipelineDelete_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineDelete_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<PipelineDelete_WorkspaceFragment, unknown>;
export const WebappDelete_WebappFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappDelete_webapp"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Webapp"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<WebappDelete_WebappFragment, unknown>;
export const WebappDelete_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappDelete_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<WebappDelete_WorkspaceFragment, unknown>;
export const FileBrowserDialog_BucketObjectFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FileBrowserDialog_bucketObject"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]} as unknown as DocumentNode<FileBrowserDialog_BucketObjectFragment, unknown>;
export const FilesEditor_FileFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FilesEditor_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"FileNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"content"}},{"kind":"Field","name":{"kind":"Name","value":"parentId"}},{"kind":"Field","name":{"kind":"Name","value":"autoSelect"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"Field","name":{"kind":"Name","value":"lineCount"}}]}}]} as unknown as DocumentNode<FilesEditor_FileFragment, unknown>;
export const GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"GenerateWorkspaceDatabasePasswordDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<GenerateWorkspaceDatabasePasswordDialog_WorkspaceFragment, unknown>;
export const GeneratePipelineWebhookUrlDialog_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"GeneratePipelineWebhookUrlDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]} as unknown as DocumentNode<GeneratePipelineWebhookUrlDialog_PipelineFragment, unknown>;
export const InviteMemberWorkspace_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"InviteMemberWorkspace_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<InviteMemberWorkspace_WorkspaceFragment, unknown>;
export const PipelineMetadataDisplay_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineMetadataDisplay_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<PipelineMetadataDisplay_PipelineFragment, unknown>;
export const PipelineCard_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineCard_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"sourceTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineMetadataDisplay_pipeline"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"lastRuns"},"name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"EnumValue","value":"EXECUTION_DATE_DESC"}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineMetadataDisplay_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}}]} as unknown as DocumentNode<PipelineCard_PipelineFragment, unknown>;
export const PipelineCard_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineCard_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<PipelineCard_WorkspaceFragment, unknown>;
export const DeletePipelineRecipientTrigger_RecipientFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineRecipientTrigger_recipient"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRecipient"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineRecipientTrigger_RecipientFragment, unknown>;
export const DeletePipelineRecipientTrigger_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineRecipientTrigger_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineRecipientTrigger_PipelineFragment, unknown>;
export const PipelineRecipients_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRecipients_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}}]}}]} as unknown as DocumentNode<PipelineRecipients_PipelineFragment, unknown>;
export const PipelineVersionConfigDialog_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionConfigDialog_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<PipelineVersionConfigDialog_VersionFragment, unknown>;
export const RunOutputsTable_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunOutputsTable_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadBucketObject_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<RunOutputsTable_WorkspaceFragment, unknown>;
export const RunOutputsTable_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunOutputsTable_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"outputs"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"GenericOutput"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"genericName"},"name":{"kind":"Name","value":"name"}},{"kind":"Field","alias":{"kind":"Name","value":"genericType"},"name":{"kind":"Name","value":"type"}},{"kind":"Field","alias":{"kind":"Name","value":"genericUri"},"name":{"kind":"Name","value":"uri"}}]}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTable"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"tableName"},"name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"datasetVersions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}}]}}]} as unknown as DocumentNode<RunOutputsTable_RunFragment, unknown>;
export const RunPipelineDialog_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<RunPipelineDialog_VersionFragment, unknown>;
export const RunPipelineDialog_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"version"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<RunPipelineDialog_RunFragment, unknown>;
export const StopPipelineDialog_RunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"StopPipelineDialog_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<StopPipelineDialog_RunFragment, unknown>;
export const StopPipelineDialog_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"StopPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]} as unknown as DocumentNode<StopPipelineDialog_PipelineFragment, unknown>;
export const PipelineMetadataDisplay_TemplateFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineMetadataDisplay_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<PipelineMetadataDisplay_TemplateFragment, unknown>;
export const TemplateCard_TemplateFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateCard_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineMetadataDisplay_template"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineMetadataDisplay_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<TemplateCard_TemplateFragment, unknown>;
export const TemplateCard_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateCard_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]} as unknown as DocumentNode<TemplateCard_WorkspaceFragment, unknown>;
export const UploadObjectDialog_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadObjectDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createObject"}}]}}]}}]} as unknown as DocumentNode<UploadObjectDialog_WorkspaceFragment, unknown>;
export const UserPicker_UserFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserPicker_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<UserPicker_UserFragment, unknown>;
export const WorkspaceConnectionPicker_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceConnectionPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"connections"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]}}]} as unknown as DocumentNode<WorkspaceConnectionPicker_WorkspaceFragment, unknown>;
export const DeleteWorkspaceInvitation_WorkspaceInvitationFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteWorkspaceInvitation_workspaceInvitation"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"WorkspaceInvitation"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}}]}}]} as unknown as DocumentNode<DeleteWorkspaceInvitation_WorkspaceInvitationFragment, unknown>;
export const ResendWorkspaceInvitation_WorkspaceInvitationFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ResendWorkspaceInvitation_workspaceInvitation"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"WorkspaceInvitation"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}}]}}]} as unknown as DocumentNode<ResendWorkspaceInvitation_WorkspaceInvitationFragment, unknown>;
export const WorkspaceMemberPicker_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceMemberPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]}}]}}]} as unknown as DocumentNode<WorkspaceMemberPicker_WorkspaceFragment, unknown>;
export const DeleteWorkspaceMember_WorkspaceMemberFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteWorkspaceMember_workspaceMember"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"WorkspaceMembership"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organizationMembership"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"role"}}]}}]}}]} as unknown as DocumentNode<DeleteWorkspaceMember_WorkspaceMemberFragment, unknown>;
export const UpdateWorkspaceMember_WorkspaceMemberFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpdateWorkspaceMember_workspaceMember"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"WorkspaceMembership"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}}]}}]} as unknown as DocumentNode<UpdateWorkspaceMember_WorkspaceMemberFragment, unknown>;
export const WorkspacePicker_ValueFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspacePicker_value"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<WorkspacePicker_ValueFragment, unknown>;
export const NewRunFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"NewRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<NewRunFragment, unknown>;
export const TabLayout_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<TabLayout_WorkspaceFragment, unknown>;
export const PipelineLayout_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<PipelineLayout_WorkspaceFragment, unknown>;
export const PipelineVersionPicker_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<PipelineVersionPicker_VersionFragment, unknown>;
export const PipelineVersionPicker_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<PipelineVersionPicker_PipelineFragment, unknown>;
export const RunPipelineDialog_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<RunPipelineDialog_PipelineFragment, unknown>;
export const PipelineLayout_PipelineFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"createTemplateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isAllowed"}},{"kind":"Field","name":{"kind":"Name","value":"reasons"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}}]} as unknown as DocumentNode<PipelineLayout_PipelineFragment, unknown>;
export const TemplateLayout_WorkspaceFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<TemplateLayout_WorkspaceFragment, unknown>;
export const DownloadTemplateVersion_VersionFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadTemplateVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<DownloadTemplateVersion_VersionFragment, unknown>;
export const TemplateLayout_TemplateFragmentDoc = {"kind":"Document","definitions":[{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateLayout_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadTemplateVersion_version"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadTemplateVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<TemplateLayout_TemplateFragment, unknown>;
export const CountryPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"CountryPicker"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"CountryPicker_country"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CountryPicker_country"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Country"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"alpha3"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<CountryPickerQuery, CountryPickerQueryVariables>;
export const GetWorkspacesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetWorkspaces"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"organizationId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]} as unknown as DocumentNode<GetWorkspacesQuery, GetWorkspacesQueryVariables>;
export const SearchFilesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchFiles"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"files"},"name":{"kind":"Name","value":"searchFiles"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlugs"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"FilesPage"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FilesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"FileResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"file"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]} as unknown as DocumentNode<SearchFilesQuery, SearchFilesQueryVariables>;
export const SearchPipelineTemplatesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchPipelineTemplates"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"pipelineTemplates"},"name":{"kind":"Name","value":"searchPipelineTemplates"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlugs"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineTemplatesPage"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineTemplatesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}}]}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]} as unknown as DocumentNode<SearchPipelineTemplatesQuery, SearchPipelineTemplatesQueryVariables>;
export const SearchPipelinesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchPipelines"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"functionalType"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineFunctionalType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"pipelines"},"name":{"kind":"Name","value":"searchPipelines"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlugs"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"functionalType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"functionalType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelinesPage"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelinesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"lastRuns"},"name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"EnumValue","value":"EXECUTION_DATE_DESC"}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]} as unknown as DocumentNode<SearchPipelinesQuery, SearchPipelinesQueryVariables>;
export const SearchDatasetsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchDatasets"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"datasets"},"name":{"kind":"Name","value":"searchDatasets"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlugs"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetsPage"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetsPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]} as unknown as DocumentNode<SearchDatasetsQuery, SearchDatasetsQueryVariables>;
export const SearchDatabaseTablesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SearchDatabaseTables"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}},"type":{"kind":"NonNullType","type":{"kind":"ListType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"databaseTables"},"name":{"kind":"Name","value":"searchDatabaseTables"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlugs"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatabaseTablesPage"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceDisplayFragment"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTablesPage"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTableResultPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"databaseTable"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"count"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceDisplayFragment"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]} as unknown as DocumentNode<SearchDatabaseTablesQuery, SearchDatabaseTablesQueryVariables>;
export const CreateDatasetDialogDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateDatasetDialog"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateDatasetInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createDataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"link"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<CreateDatasetDialogMutation, CreateDatasetDialogMutationVariables>;
export const DatasetLinksDataGridDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"DatasetLinksDataGrid"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"datasetId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"datasetId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"links"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"6"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteDatasetLinkTrigger_datasetLink"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteDatasetLinkTrigger_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<DatasetLinksDataGridQuery, DatasetLinksDataGridQueryVariables>;
export const DatasetPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"DatasetPicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetPicker_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"datasets"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]} as unknown as DocumentNode<DatasetPickerQuery, DatasetPickerQueryVariables>;
export const GetDatasetVersionFileSampleDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetDatasetVersionFileSample"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"datasetVersionFile"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"properties"}},{"kind":"Field","name":{"kind":"Name","value":"fileSample"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"sample"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"statusReason"}}]}}]}}]}}]} as unknown as DocumentNode<GetDatasetVersionFileSampleQuery, GetDatasetVersionFileSampleQueryVariables>;
export const DatasetVersionFilesDataGridDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"DatasetVersionFilesDataGrid"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"1"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"datasetVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadVersionFile_file"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadVersionFile_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}}]}}]} as unknown as DocumentNode<DatasetVersionFilesDataGridQuery, DatasetVersionFilesDataGridQueryVariables>;
export const DatasetVersionPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"DatasetVersionPicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"datasetId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"datasetId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"versions"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionPicker_version"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]} as unknown as DocumentNode<DatasetVersionPickerQuery, DatasetVersionPickerQueryVariables>;
export const LinkDatasetDialogDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"LinkDatasetDialog"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"LinkDatasetInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"linkDataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"link"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]}}]}}]} as unknown as DocumentNode<LinkDatasetDialogMutation, LinkDatasetDialogMutationVariables>;
export const PinDatasetButtonDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"PinDatasetButton"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"PinDatasetInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pinDataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"link"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}}]}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<PinDatasetButtonMutation, PinDatasetButtonMutationVariables>;
export const UpdateDatasetDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateDataset"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateDatasetInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateDataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"sharedWithOrganization"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<UpdateDatasetMutation, UpdateDatasetMutationVariables>;
export const UpdateDatasetVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateDatasetVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateDatasetVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateDatasetVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"version"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}}]}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<UpdateDatasetVersionMutation, UpdateDatasetVersionMutationVariables>;
export const CreateDatasetVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateDatasetVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateDatasetVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createDatasetVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"version"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}}]}},{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<CreateDatasetVersionMutation, CreateDatasetVersionMutationVariables>;
export const GenerateDatasetUploadUrlDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"generateDatasetUploadUrl"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"GenerateDatasetUploadUrlInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"generateDatasetUploadUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"uploadUrl"}}]}}]}}]} as unknown as DocumentNode<GenerateDatasetUploadUrlMutation, GenerateDatasetUploadUrlMutationVariables>;
export const PrepareVersionFileDownloadDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"PrepareVersionFileDownload"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"PrepareVersionFileDownloadInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"prepareVersionFileDownload"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<PrepareVersionFileDownloadMutation, PrepareVersionFileDownloadMutationVariables>;
export const CreateDatasetVersionFileDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateDatasetVersionFile"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateDatasetVersionFileInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createDatasetVersionFile"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"file"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}}]}}]}}]} as unknown as DocumentNode<CreateDatasetVersionFileMutation, CreateDatasetVersionFileMutationVariables>;
export const DeleteDatasetLinkDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteDatasetLink"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteDatasetLinkInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteDatasetLink"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteDatasetLinkMutation, DeleteDatasetLinkMutationVariables>;
export const DeleteDatasetDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteDataset"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteDatasetInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteDataset"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteDatasetMutation, DeleteDatasetMutationVariables>;
export const SetMetadataAttributeDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetMetadataAttribute"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"SetMetadataAttributeInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"setMetadataAttribute"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"attribute"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"system"}}]}}]}}]}}]} as unknown as DocumentNode<SetMetadataAttributeMutation, SetMetadataAttributeMutationVariables>;
export const DeleteMetadataAttributeDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteMetadataAttribute"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteMetadataAttributeInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteMetadataAttribute"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteMetadataAttributeMutation, DeleteMetadataAttributeMutationVariables>;
export const TabularFileMetadataDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"TabularFileMetadata"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"fileId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"datasetVersionFile"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"fileId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"attributes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"system"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"updatedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"properties"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"targetId"}}]}}]}}]} as unknown as DocumentNode<TabularFileMetadataQuery, TabularFileMetadataQueryVariables>;
export const UpdateUserDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateUser"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateUserInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateUser"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"Field","name":{"kind":"Name","value":"firstName"}},{"kind":"Field","name":{"kind":"Name","value":"lastName"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateUserMutation, UpdateUserMutationVariables>;
export const ResetPasswordDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ResetPassword"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ResetPasswordInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"resetPassword"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}}]}}]}}]} as unknown as DocumentNode<ResetPasswordMutation, ResetPasswordMutationVariables>;
export const SetPasswordDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"SetPassword"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"SetPasswordInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"setPassword"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"error"}}]}}]}}]} as unknown as DocumentNode<SetPasswordMutation, SetPasswordMutationVariables>;
export const LoginDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"Login"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"LoginInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"login"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<LoginMutation, LoginMutationVariables>;
export const LogoutDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"Logout"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"logout"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}}]}}]}}]} as unknown as DocumentNode<LogoutMutation, LogoutMutationVariables>;
export const RegisterDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"Register"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"RegisterInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"register"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<RegisterMutation, RegisterMutationVariables>;
export const GenerateChallengeDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"GenerateChallenge"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"generateChallenge"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<GenerateChallengeMutation, GenerateChallengeMutationVariables>;
export const VerifyDeviceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"VerifyDevice"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"VerifyDeviceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"verifyDevice"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<VerifyDeviceMutation, VerifyDeviceMutationVariables>;
export const DisableTwoFactorDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DisableTwoFactor"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DisableTwoFactorInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"disableTwoFactor"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DisableTwoFactorMutation, DisableTwoFactorMutationVariables>;
export const EnableTwoFactorDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"EnableTwoFactor"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"enableTwoFactor"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"verified"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<EnableTwoFactorMutation, EnableTwoFactorMutationVariables>;
export const GetUserDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetUser"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"me"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasTwoFactorEnabled"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"adminPanel"}},{"kind":"Field","name":{"kind":"Name","value":"superUser"}},{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}},{"kind":"Field","name":{"kind":"Name","value":"features"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"firstName"}},{"kind":"Field","name":{"kind":"Name","value":"lastName"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}}]} as unknown as DocumentNode<GetUserQuery, GetUserQueryVariables>;
export const AccountPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"AccountPage"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"me"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasTwoFactorEnabled"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"firstName"}},{"kind":"Field","name":{"kind":"Name","value":"lastName"}},{"kind":"Field","name":{"kind":"Name","value":"dateJoined"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"pendingWorkspaceInvitations"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"invitedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<AccountPageQuery, AccountPageQueryVariables>;
export const RegisterPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"RegisterPage"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"config"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"passwordRequirements"}}]}}]}}]} as unknown as DocumentNode<RegisterPageQuery, RegisterPageQueryVariables>;
export const NotebooksPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"notebooksPage"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"notebooksUrl"}}]}}]} as unknown as DocumentNode<NotebooksPageQuery, NotebooksPageQueryVariables>;
export const OrganizationDatasetsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"OrganizationDatasets"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"1"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"10"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Organization_organization"}},{"kind":"Field","name":{"kind":"Name","value":"datasetLinks"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"OrganizationDataset_link"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Organization_organization"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Organization"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"archiveWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"manageOwners"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"OrganizationDataset_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"sharedWithOrganization"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"links"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"50"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]}}]} as unknown as DocumentNode<OrganizationDatasetsQuery, OrganizationDatasetsQueryVariables>;
export const DeleteOrganizationInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteOrganizationInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteOrganizationInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteOrganizationInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteOrganizationInvitationMutation, DeleteOrganizationInvitationMutationVariables>;
export const OrganizationInvitationsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"OrganizationInvitations"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}}]}},{"kind":"Field","name":{"kind":"Name","value":"invitations"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"invitedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"workspaceInvitations"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"role"}}]}}]}}]}}]}}]}}]} as unknown as DocumentNode<OrganizationInvitationsQuery, OrganizationInvitationsQueryVariables>;
export const ResendOrganizationInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ResendOrganizationInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ResendOrganizationInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"resendOrganizationInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<ResendOrganizationInvitationMutation, ResendOrganizationInvitationMutationVariables>;
export const InviteOrganizationMemberDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"InviteOrganizationMember"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"InviteOrganizationMemberInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"inviteOrganizationMember"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<InviteOrganizationMemberMutation, InviteOrganizationMemberMutationVariables>;
export const DeleteOrganizationMemberDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteOrganizationMember"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteOrganizationMemberInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteOrganizationMember"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteOrganizationMemberMutation, DeleteOrganizationMemberMutationVariables>;
export const OrganizationMembersDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"OrganizationMembers"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"term"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"role"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"OrganizationMembershipRole"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"manageOwners"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1000"}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"term"},"value":{"kind":"Variable","name":{"kind":"Name","value":"term"}}},{"kind":"Argument","name":{"kind":"Name","value":"role"},"value":{"kind":"Variable","name":{"kind":"Name","value":"role"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspaceMemberships"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceRole"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceRole"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"WorkspaceMembership"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<OrganizationMembersQuery, OrganizationMembersQueryVariables>;
export const UpdateOrganizationMemberDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateOrganizationMember"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateOrganizationMemberInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateOrganizationMember"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"membership"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateOrganizationMemberMutation, UpdateOrganizationMemberMutationVariables>;
export const OrganizationWorkspaceInvitationsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"OrganizationWorkspaceInvitations"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pendingWorkspaceInvitations"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"invitedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]}}]}}]} as unknown as DocumentNode<OrganizationWorkspaceInvitationsQuery, OrganizationWorkspaceInvitationsQueryVariables>;
export const DeleteWorkspaceInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteWorkspaceInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteWorkspaceInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteWorkspaceInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteWorkspaceInvitationMutation, DeleteWorkspaceInvitationMutationVariables>;
export const ResendWorkspaceInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"ResendWorkspaceInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ResendWorkspaceInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"resendWorkspaceInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<ResendWorkspaceInvitationMutation, ResendWorkspaceInvitationMutationVariables>;
export const OrganizationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"Organization"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Organization_organization"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Organization_organization"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Organization"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"archiveWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"manageOwners"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}}]}}]} as unknown as DocumentNode<OrganizationQuery, OrganizationQueryVariables>;
export const OrganizationsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"Organizations"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organizations"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]} as unknown as DocumentNode<OrganizationsQuery, OrganizationsQueryVariables>;
export const OrganizationWorkspacesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"OrganizationWorkspaces"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"1"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"10"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Organization_organization"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"organizationId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"OrganizationWorkspace_workspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Organization_organization"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Organization"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"archiveWorkspace"}},{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"manageOwners"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"OrganizationWorkspace_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<OrganizationWorkspacesQuery, OrganizationWorkspacesQueryVariables>;
export const PipelinePageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelinePage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dag"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"CountryBadge_country"}}]}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"externalUrl"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"sampleConfig"}}]}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserProperty_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"triggerMode"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"externalUrl"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserColumn_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"lastRefreshedAt"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CountryBadge_country"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Country"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserProperty_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserColumn_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"}}]}}]} as unknown as DocumentNode<PipelinePageQuery, PipelinePageQueryVariables>;
export const UpdatePipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdatePipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdatePipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"webhookEnabled"}},{"kind":"Field","name":{"kind":"Name","value":"autoUpdateFromTemplate"}}]}}]}}]}}]} as unknown as DocumentNode<UpdatePipelineMutation, UpdatePipelineMutationVariables>;
export const PipelineConfigureRunPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelineConfigureRunPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dag"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"sampleConfig"}},{"kind":"Field","name":{"kind":"Name","value":"description"}}]}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunForm_dag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunForm_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"sampleConfig"}}]}},{"kind":"Field","name":{"kind":"Name","value":"formCode"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]} as unknown as DocumentNode<PipelineConfigureRunPageQuery, PipelineConfigureRunPageQueryVariables>;
export const PipelineRunPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelineRunPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"runId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dagRun"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"runId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"triggerMode"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunDataCard_dagRun"}}]}},{"kind":"Field","name":{"kind":"Name","value":"dag"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunDataCard_dag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunOutputEntry_output"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRunOutput"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"title"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserProperty_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunMessages_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"priority"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunLogs_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"logs"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"config"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteIcon_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"formCode"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunDataCard_dagRun"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAGRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"externalUrl"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"triggerMode"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}},{"kind":"Field","name":{"kind":"Name","value":"outputs"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunOutputEntry_output"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserProperty_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"progress"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunMessages_dagRun"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunLogs_dagRun"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dagRun"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunFavoriteTrigger_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunDataCard_dag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunReadonlyForm_dag"}}]}}]} as unknown as DocumentNode<PipelineRunPageQuery, PipelineRunPageQueryVariables>;
export const PipelinesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelinesPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"15"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dags"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"CountryBadge_country"}}]}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"EnumValue","value":"EXECUTION_DATE_DESC"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}}]}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CountryBadge_country"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Country"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<PipelinesPageQuery, PipelinesPageQueryVariables>;
export const JoinWorkspaceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"joinWorkspace"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"JoinWorkspaceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"joinWorkspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"invitation"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"invitedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<JoinWorkspaceMutation, JoinWorkspaceMutationVariables>;
export const DeclineWorkspaceInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"declineWorkspaceInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeclineWorkspaceInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"declineWorkspaceInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"invitation"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeclineWorkspaceInvitationMutation, DeclineWorkspaceInvitationMutationVariables>;
export const ConnectionPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"ConnectionPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"connectionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"Field","name":{"kind":"Name","value":"connection"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"connectionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ConnectionUsageSnippets_connection"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ConnectionFieldsSection_connection"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UpdateConnectionFieldsDialog_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"secret"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ConnectionUsageSnippets_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ConnectionFieldsSection_connection"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"secret"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UpdateConnectionFieldsDialog_connection"}}]}}]} as unknown as DocumentNode<ConnectionPageQuery, ConnectionPageQueryVariables>;
export const UpdateConnectionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"updateConnection"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateConnectionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateConnection"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"connection"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"fields"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"secret"}}]}}]}}]}}]}}]} as unknown as DocumentNode<UpdateConnectionMutation, UpdateConnectionMutationVariables>;
export const ConnectionsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"ConnectionsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"createConnection"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"CreateConnectionDialog_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"connections"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreateConnectionDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<ConnectionsPageQuery, ConnectionsPageQueryVariables>;
export const WorkspaceDatabaseTablePageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceDatabaseTablePage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"tableName"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteDatabaseTable"}}]}},{"kind":"Field","name":{"kind":"Name","value":"database"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"table"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"tableName"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"count"}},{"kind":"Field","name":{"kind":"Name","value":"columns"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatabaseTableDataGrid_table"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatabaseTableDataGrid_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTableDataGrid_table"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTable"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"columns"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseTableDataGrid_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<WorkspaceDatabaseTablePageQuery, WorkspaceDatabaseTablePageQueryVariables>;
export const WorkspaceDatabasesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceDatabasesPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"database"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"tables"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"count"}}]}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatabaseVariablesSection_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatabaseVariablesSection_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"database"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"credentials"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dbName"}},{"kind":"Field","name":{"kind":"Name","value":"username"}},{"kind":"Field","name":{"kind":"Name","value":"password"}},{"kind":"Field","name":{"kind":"Name","value":"host"}},{"kind":"Field","name":{"kind":"Name","value":"port"}},{"kind":"Field","name":{"kind":"Name","value":"url"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<WorkspaceDatabasesPageQuery, WorkspaceDatabasesPageQueryVariables>;
export const WorkspaceDatasetAccessPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceDatasetAccessPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sourceWorkspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"datasetSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"datasetLink"},"name":{"kind":"Name","value":"datasetLinkBySlug"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sourceWorkspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"datasetSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"datasetSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_datasetLink"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"sharedWithOrganization"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLinksDataGrid_dataset"}},{"kind":"Field","name":{"kind":"Name","value":"version"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"directives":[{"kind":"Directive","name":{"kind":"Name","value":"include"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_version"}}]}},{"kind":"Field","name":{"kind":"Name","value":"latestVersion"},"directives":[{"kind":"Directive","name":{"kind":"Name","value":"skip"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_version"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PinDatasetButton_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pin"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PinDatasetButton_link"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"createVersion"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLinksDataGrid_dataset"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Dataset"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionPicker_version"}}]}}]} as unknown as DocumentNode<WorkspaceDatasetAccessPageQuery, WorkspaceDatasetAccessPageQueryVariables>;
export const WorkspaceDatasetFilesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceDatasetFilesPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sourceWorkspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"datasetSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"1"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"20"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"datasetLink"},"name":{"kind":"Name","value":"datasetLinkBySlug"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sourceWorkspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"datasetSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"datasetSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_datasetLink"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLinksDataGrid_dataset"}},{"kind":"Field","name":{"kind":"Name","value":"version"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"directives":[{"kind":"Directive","name":{"kind":"Name","value":"include"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetExplorer_version"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetExplorer_file"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"latestVersion"},"directives":[{"kind":"Directive","name":{"kind":"Name","value":"skip"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetExplorer_version"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetExplorer_file"}}]}}]}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PinDatasetButton_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pin"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadVersionFile_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"attachment"},"value":{"kind":"BooleanValue","value":false}}]}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"targetId"}},{"kind":"Field","name":{"kind":"Name","value":"attributes"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"value"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"system"}},{"kind":"Field","name":{"kind":"Name","value":"__typename"}}]}},{"kind":"Field","name":{"kind":"Name","value":"properties"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ColumnMetadataDrawer_file"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetExplorer_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersionFile"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"filename"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadVersionFile_file"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileSample_file"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileColumns_file"}},{"kind":"Field","name":{"kind":"Name","value":"contentType"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"uri"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileSample_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionFileColumns_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PinDatasetButton_link"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"createVersion"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLinksDataGrid_dataset"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Dataset"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionPicker_version"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetExplorer_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetExplorer_file"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileSample_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionFileColumns_version"}}]}}]} as unknown as DocumentNode<WorkspaceDatasetFilesPageQuery, WorkspaceDatasetFilesPageQueryVariables>;
export const WorkspaceDatasetIndexPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceDatasetIndexPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"sourceWorkspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"datasetSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"datasetLink"},"name":{"kind":"Name","value":"datasetLinkBySlug"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"sourceWorkspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"datasetSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"datasetSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_datasetLink"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"sharedWithOrganization"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"version"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"directives":[{"kind":"Directive","name":{"kind":"Name","value":"include"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_version"}}]}},{"kind":"Field","name":{"kind":"Name","value":"latestVersion"},"directives":[{"kind":"Directive","name":{"kind":"Name","value":"skip"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"isSpecificVersion"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetLayout_version"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PinDatasetButton_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pin"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_datasetLink"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UploadDatasetVersionDialog_datasetLink"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PinDatasetButton_link"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"createVersion"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetLayout_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetVersionPicker_version"}}]}}]} as unknown as DocumentNode<WorkspaceDatasetIndexPageQuery, WorkspaceDatasetIndexPageQueryVariables>;
export const WorkspaceDatasetsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceDatasetsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"CreateDatasetDialog_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createDataset"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"pinnedDatasets"},"name":{"kind":"Name","value":"datasets"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"pinned"},"value":{"kind":"BooleanValue","value":true}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"6"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DatasetCard_link"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"datasets"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PinDatasetButton_link"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreateDatasetDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createDataset"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DatasetCard_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PinDatasetButton_link"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatasetLink"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"isPinned"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pin"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<WorkspaceDatasetsPageQuery, WorkspaceDatasetsPageQueryVariables>;
export const WorkspaceFilesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceFilesPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"ignoreHiddenFiles"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"BucketExplorer_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UploadObjectDialog_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"CreateBucketFolderDialog_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"BucketExplorer_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"objects"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"prefix"},"value":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"ignoreHiddenFiles"},"value":{"kind":"Variable","name":{"kind":"Name","value":"ignoreHiddenFiles"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"BucketExplorer_objects"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createObject"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteObject"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_object"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteBucketObject_object"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketExplorer_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadBucketObject_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteBucketObject_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UploadObjectDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createObject"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreateBucketFolderDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createObject"}}]}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketExplorer_objects"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObjectPage"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadBucketObject_object"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteBucketObject_object"}}]}}]}}]} as unknown as DocumentNode<WorkspaceFilesPageQuery, WorkspaceFilesPageQueryVariables>;
export const WorkspacePageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"dockerImage"}},{"kind":"Field","name":{"kind":"Name","value":"configuration"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"ArchiveWorkspace_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"InviteMemberWorkspace_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ArchiveWorkspace_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"InviteMemberWorkspace_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<WorkspacePageQuery, WorkspacePageQueryVariables>;
export const UpdateWorkspaceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"updateWorkspace"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateWorkspaceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateWorkspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"configuration"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"alpha3"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<UpdateWorkspaceMutation, UpdateWorkspaceMutationVariables>;
export const WorkspaceNotebooksPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceNotebooksPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"notebooksUrl"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<WorkspaceNotebooksPageQuery, WorkspaceNotebooksPageQueryVariables>;
export const WorkspacePipelineCodePageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelineCodePage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"pipeline"},"name":{"kind":"Name","value":"pipelineByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_pipeline"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"FilesEditor_file"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"createTemplateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isAllowed"}},{"kind":"Field","name":{"kind":"Name","value":"reasons"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FilesEditor_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"FileNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"content"}},{"kind":"Field","name":{"kind":"Name","value":"parentId"}},{"kind":"Field","name":{"kind":"Name","value":"autoSelect"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"Field","name":{"kind":"Name","value":"lineCount"}}]}}]} as unknown as DocumentNode<WorkspacePipelineCodePageQuery, WorkspacePipelineCodePageQueryVariables>;
export const GetPipelineVersionFilesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetPipelineVersionFiles"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipelineVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"files"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"FilesEditor_file"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FilesEditor_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"FileNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"content"}},{"kind":"Field","name":{"kind":"Name","value":"parentId"}},{"kind":"Field","name":{"kind":"Name","value":"autoSelect"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"Field","name":{"kind":"Name","value":"lineCount"}}]}}]} as unknown as DocumentNode<GetPipelineVersionFilesQuery, GetPipelineVersionFilesQueryVariables>;
export const WorkspacePipelinePageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelinePage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"pipeline"},"name":{"kind":"Name","value":"pipelineByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_pipeline"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"createVersion"}},{"kind":"Field","name":{"kind":"Name","value":"createTemplateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isAllowed"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"webhookUrl"}},{"kind":"Field","name":{"kind":"Name","value":"webhookEnabled"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"notebookPath"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"sourceTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"autoUpdateFromTemplate"}},{"kind":"Field","name":{"kind":"Name","value":"hasNewTemplateVersions"}},{"kind":"Field","name":{"kind":"Name","value":"newTemplateVersions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionParametersTable_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionConfigDialog_version"}}]}},{"kind":"Field","name":{"kind":"Name","value":"recipients"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"createTemplateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isAllowed"}},{"kind":"Field","name":{"kind":"Name","value":"reasons"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionParametersTable_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"config"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionConfigDialog_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}}]}}]} as unknown as DocumentNode<WorkspacePipelinePageQuery, WorkspacePipelinePageQueryVariables>;
export const WorkspacePipelineNotificationsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelineNotificationsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"pipeline"},"name":{"kind":"Name","value":"pipelineByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_pipeline"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRecipients_pipeline"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"update"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"createTemplateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isAllowed"}},{"kind":"Field","name":{"kind":"Name","value":"reasons"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRecipients_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}}]}}]} as unknown as DocumentNode<WorkspacePipelineNotificationsPageQuery, WorkspacePipelineNotificationsPageQueryVariables>;
export const WorkspacePipelineRunPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelineRunPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"runId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunOutputsTable_workspace"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipelineRun"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"runId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"version"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"timeout"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}},{"kind":"Field","name":{"kind":"Name","value":"triggerMode"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"notebookPath"}},{"kind":"Field","name":{"kind":"Name","value":"sourceTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"stopPipeline"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"stoppedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunOutputsTable_run"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_run"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunMessages_run"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunLogs_run"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadBucketObject_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunOutputsTable_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadBucketObject_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunOutputsTable_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"outputs"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"GenericOutput"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"genericName"},"name":{"kind":"Name","value":"name"}},{"kind":"Field","alias":{"kind":"Name","value":"genericType"},"name":{"kind":"Name","value":"type"}},{"kind":"Field","alias":{"kind":"Name","value":"genericUri"},"name":{"kind":"Name","value":"uri"}}]}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}},{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DatabaseTable"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"tableName"},"name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"datasetVersions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"dataset"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"version"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunMessages_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"messages"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"message"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}},{"kind":"Field","name":{"kind":"Name","value":"priority"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunLogs_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"logs"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}}]} as unknown as DocumentNode<WorkspacePipelineRunPageQuery, WorkspacePipelineRunPageQueryVariables>;
export const WorkspacePipelineRunsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelineRunsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"1"}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"10"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"pipeline"},"name":{"kind":"Name","value":"pipelineByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_pipeline"}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"version"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}},{"kind":"Field","name":{"kind":"Name","value":"triggerMode"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserColumn_user"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}}]}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"run"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"createTemplateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"isAllowed"}},{"kind":"Field","name":{"kind":"Name","value":"reasons"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"RunPipelineDialog_pipeline"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserColumn_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}}]} as unknown as DocumentNode<WorkspacePipelineRunsPageQuery, WorkspacePipelineRunsPageQueryVariables>;
export const WorkspacePipelineVersionsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelineVersionsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"pipeline"},"name":{"kind":"Name","value":"pipelineByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"versions"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionCard_version"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionCard_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"}}]}}]} as unknown as DocumentNode<WorkspacePipelineVersionsPageQuery, WorkspacePipelineVersionsPageQueryVariables>;
export const WorkspaceTemplatePageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceTemplatePage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"templateCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"template"},"name":{"kind":"Name","value":"templateByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"templateCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TemplateLayout_template"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}},{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"sourcePipelineVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"files"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"FilesEditor_file"}}]}},{"kind":"Field","name":{"kind":"Name","value":"zipfile"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TabLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadTemplateVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TabLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateLayout_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}},{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadTemplateVersion_version"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FilesEditor_file"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"FileNode"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"content"}},{"kind":"Field","name":{"kind":"Name","value":"parentId"}},{"kind":"Field","name":{"kind":"Name","value":"autoSelect"}},{"kind":"Field","name":{"kind":"Name","value":"language"}},{"kind":"Field","name":{"kind":"Name","value":"lineCount"}}]}}]} as unknown as DocumentNode<WorkspaceTemplatePageQuery, WorkspaceTemplatePageQueryVariables>;
export const WorkspaceTemplateVersionsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceTemplateVersionsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"templateCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"template"},"name":{"kind":"Name","value":"templateByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"templateCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"versions"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TemplateVersionCard_version"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateVersionCard_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"}}]}}]} as unknown as DocumentNode<WorkspaceTemplateVersionsPageQuery, WorkspaceTemplateVersionsPageQueryVariables>;
export const WorkspaceWebappPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceWebappPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"webappId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WebappForm_workspace"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"webapp"},"name":{"kind":"Name","value":"webapp"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"webappId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WebappForm_webapp"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappForm_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappForm_webapp"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Webapp"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"icon"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]} as unknown as DocumentNode<WorkspaceWebappPageQuery, WorkspaceWebappPageQueryVariables>;
export const WorkspaceWebappsPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceWebappsPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"15"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"Field","name":{"kind":"Name","value":"webapps"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"icon"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"url"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}},{"kind":"Field","name":{"kind":"Name","value":"createdBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"firstName"}},{"kind":"Field","name":{"kind":"Name","value":"lastName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}}]}},{"kind":"Field","alias":{"kind":"Name","value":"favoriteWebapps"},"name":{"kind":"Name","value":"webapps"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"favorite"},"value":{"kind":"BooleanValue","value":true}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"6"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WebappCard_webapp"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WebappCard_webapp"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Webapp"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"icon"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]} as unknown as DocumentNode<WorkspaceWebappsPageQuery, WorkspaceWebappsPageQueryVariables>;
export const CheckWorkspaceAvailabilityDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"CheckWorkspaceAvailability"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]} as unknown as DocumentNode<CheckWorkspaceAvailabilityQuery, CheckWorkspaceAvailabilityQueryVariables>;
export const DeletePipelineTemplateDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deletePipelineTemplate"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeletePipelineTemplateInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deletePipelineTemplate"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineTemplateMutation, DeletePipelineTemplateMutationVariables>;
export const SetFavoriteRunDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"setFavoriteRun"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"SetDAGRunFavoriteInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"setDAGRunFavorite"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"dagRun"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}},{"kind":"Field","name":{"kind":"Name","value":"isFavorite"}}]}}]}}]}}]} as unknown as DocumentNode<SetFavoriteRunMutation, SetFavoriteRunMutationVariables>;
export const CreatePipelineFromTemplateVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreatePipelineFromTemplateVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreatePipelineFromTemplateVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createPipelineFromTemplateVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}}]} as unknown as DocumentNode<CreatePipelineFromTemplateVersionMutation, CreatePipelineFromTemplateVersionMutationVariables>;
export const GetPipelineTemplatesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetPipelineTemplates"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"currentWorkspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"tags"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"functionalType"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineFunctionalType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"currentWorkspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplateTags"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplates"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"tags"},"value":{"kind":"Variable","name":{"kind":"Name","value":"tags"}}},{"kind":"Argument","name":{"kind":"Name","value":"functionalType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"functionalType"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"sourcePipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<GetPipelineTemplatesQuery, GetPipelineTemplatesQueryVariables>;
export const UpdatePipelineVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdatePipelineVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdatePipelineVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePipelineVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipelineVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionCard_version"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DownloadPipelineVersion_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionCard_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"externalLink"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DownloadPipelineVersion_version"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeletePipelineVersionTrigger_version"}}]}}]} as unknown as DocumentNode<UpdatePipelineVersionMutation, UpdatePipelineVersionMutationVariables>;
export const WorkspacePipelinesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelinesPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"tags"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"functionalType"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineFunctionalType"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"pipelineTags"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"CreatePipelineDialog_workspace"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipelines"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}},{"kind":"Argument","name":{"kind":"Name","value":"tags"},"value":{"kind":"Variable","name":{"kind":"Name","value":"tags"}}},{"kind":"Argument","name":{"kind":"Name","value":"functionalType"},"value":{"kind":"Variable","name":{"kind":"Name","value":"functionalType"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineCard_pipeline"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"BucketObjectPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineMetadataDisplay_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"CreatePipelineDialog_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"BucketObjectPicker_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineCard_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"sourceTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineMetadataDisplay_pipeline"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}},{"kind":"Field","alias":{"kind":"Name","value":"lastRuns"},"name":{"kind":"Name","value":"runs"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"EnumValue","value":"EXECUTION_DATE_DESC"}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineRunStatusBadge_run"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}}]}}]}}]} as unknown as DocumentNode<WorkspacePipelinesPageQuery, WorkspacePipelinesPageQueryVariables>;
export const PipelinesPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelinesPicker"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelinesPicker_value"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelinesPicker_value"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DAG"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}}]}}]} as unknown as DocumentNode<PipelinesPickerQuery, PipelinesPickerQueryVariables>;
export const CreatePipelineTemplateVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreatePipelineTemplateVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreatePipelineTemplateVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createPipelineTemplateVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplate"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}}]} as unknown as DocumentNode<CreatePipelineTemplateVersionMutation, CreatePipelineTemplateVersionMutationVariables>;
export const UpdateTemplateVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateTemplateVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateTemplateVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateTemplateVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"templateVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TemplateVersionCard_version"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"delete"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateVersionCard_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplateVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"changelog"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeleteTemplateVersionTrigger_version"}}]}}]} as unknown as DocumentNode<UpdateTemplateVersionMutation, UpdateTemplateVersionMutationVariables>;
export const UpgradePipelineVersionFromTemplateDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"upgradePipelineVersionFromTemplate"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpgradePipelineVersionFromTemplateInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"upgradePipelineVersionFromTemplate"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<UpgradePipelineVersionFromTemplateMutation, UpgradePipelineVersionFromTemplateMutationVariables>;
export const PipelineRunPollerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelineRunPoller"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"runId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"run"},"name":{"kind":"Name","value":"pipelineRun"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"runId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"usePipelineRunPoller_run"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}},{"kind":"Field","name":{"kind":"Name","value":"progress"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"usePipelineRunPoller_run"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRun"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"status"}}]}}]} as unknown as DocumentNode<PipelineRunPollerQuery, PipelineRunPollerQueryVariables>;
export const RunPipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"RunPipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"RunDAGInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"runDAG"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"dag"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}},{"kind":"Field","name":{"kind":"Name","value":"dagRun"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"externalUrl"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}}]}}]}}]}}]} as unknown as DocumentNode<RunPipelineMutation, RunPipelineMutationVariables>;
export const GetPipelineVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetPipelineVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipelineVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"zipfile"}}]}}]}}]} as unknown as DocumentNode<GetPipelineVersionQuery, GetPipelineVersionQueryVariables>;
export const GetPipelineRunDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetPipelineRun"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"runId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"dagRun"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"runId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"externalUrl"}},{"kind":"Field","name":{"kind":"Name","value":"externalId"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"executionDate"}},{"kind":"Field","name":{"kind":"Name","value":"duration"}}]}}]}}]} as unknown as DocumentNode<GetPipelineRunQuery, GetPipelineRunQueryVariables>;
export const GetRunOutputDownloadUrlDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"GetRunOutputDownloadURL"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"PrepareDownloadURLInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"prepareDownloadURL"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"url"}}]}}]}}]} as unknown as DocumentNode<GetRunOutputDownloadUrlMutation, GetRunOutputDownloadUrlMutationVariables>;
export const RemoveFromFavoritesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"RemoveFromFavorites"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"RemoveFromFavoritesInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"removeFromFavorites"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<RemoveFromFavoritesMutation, RemoveFromFavoritesMutationVariables>;
export const AddToFavoritesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"AddToFavorites"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"AddToFavoritesInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"addToFavorites"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<AddToFavoritesMutation, AddToFavoritesMutationVariables>;
export const UpdateWebappDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateWebapp"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateWebappInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateWebapp"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<UpdateWebappMutation, UpdateWebappMutationVariables>;
export const CreateWebappDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateWebapp"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateWebappInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWebapp"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"webapp"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]}}]}}]} as unknown as DocumentNode<CreateWebappMutation, CreateWebappMutationVariables>;
export const ArchiveWorkspaceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"archiveWorkspace"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ArchiveWorkspaceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"archiveWorkspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<ArchiveWorkspaceMutation, ArchiveWorkspaceMutationVariables>;
export const ObjectPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"ObjectPicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"objects"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"prefix"},"value":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}}]}}]}}]}}]}}]} as unknown as DocumentNode<ObjectPickerQuery, ObjectPickerQueryVariables>;
export const CreateConnectionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"createConnection"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateConnectionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createConnection"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"connection"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<CreateConnectionMutation, CreateConnectionMutationVariables>;
export const CreateWorkspaceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"createWorkspace"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateWorkspaceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"alpha3"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<CreateWorkspaceMutation, CreateWorkspaceMutationVariables>;
export const DatabaseTableDataGridDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"DatabaseTableDataGrid"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"tableName"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"orderBy"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"direction"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"OrderByDirection"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"database"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"table"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"name"},"value":{"kind":"Variable","name":{"kind":"Name","value":"tableName"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"rows"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"orderBy"},"value":{"kind":"Variable","name":{"kind":"Name","value":"orderBy"}}},{"kind":"Argument","name":{"kind":"Name","value":"direction"},"value":{"kind":"Variable","name":{"kind":"Name","value":"direction"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"10"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}},{"kind":"Field","name":{"kind":"Name","value":"items"}}]}}]}}]}}]}}]}}]} as unknown as DocumentNode<DatabaseTableDataGridQuery, DatabaseTableDataGridQueryVariables>;
export const DeletePipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deletePipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeletePipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deletePipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineMutation, DeletePipelineMutationVariables>;
export const DeleteWebappDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deleteWebapp"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteWebappInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteWebapp"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteWebappMutation, DeleteWebappMutationVariables>;
export const FileBrowserDialogDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"FileBrowserDialog"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}},"defaultValue":{"kind":"StringValue","value":"","block":false}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},"defaultValue":{"kind":"ListValue","values":[]}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"useSearch"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"Boolean"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","alias":{"kind":"Name","value":"searchResults"},"name":{"kind":"Name","value":"searchFiles"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlugs"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlugs"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"prefix"},"value":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}}}],"directives":[{"kind":"Directive","name":{"kind":"Name","value":"include"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"useSearch"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"file"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"size"}}]}},{"kind":"Field","name":{"kind":"Name","value":"score"}}]}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"directives":[{"kind":"Directive","name":{"kind":"Name","value":"skip"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"if"},"value":{"kind":"Variable","name":{"kind":"Name","value":"useSearch"}}}]}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"bucket"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"objects"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"prefix"},"value":{"kind":"Variable","name":{"kind":"Name","value":"prefix"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"FileBrowserDialog_bucketObject"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"hasNextPage"}},{"kind":"Field","name":{"kind":"Name","value":"hasPreviousPage"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"FileBrowserDialog_bucketObject"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"BucketObject"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"path"}},{"kind":"Field","name":{"kind":"Name","value":"size"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]} as unknown as DocumentNode<FileBrowserDialogQuery, FileBrowserDialogQueryVariables>;
export const UploadPipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"uploadPipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UploadPipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"uploadPipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"details"}},{"kind":"Field","name":{"kind":"Name","value":"pipelineVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"isLatestVersion"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]} as unknown as DocumentNode<UploadPipelineMutation, UploadPipelineMutationVariables>;
export const GenerateNewDatabasePasswordDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"generateNewDatabasePassword"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"GenerateNewDatabasePasswordInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"generateNewDatabasePassword"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<GenerateNewDatabasePasswordMutation, GenerateNewDatabasePasswordMutationVariables>;
export const GenerateWebhookPipelineWebhookUrlDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"generateWebhookPipelineWebhookUrl"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"GeneratePipelineWebhookUrlInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"generatePipelineWebhookUrl"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"webhookUrl"}}]}}]}}]}}]} as unknown as DocumentNode<GenerateWebhookPipelineWebhookUrlMutation, GenerateWebhookPipelineWebhookUrlMutationVariables>;
export const InviteWorkspaceMemberDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"inviteWorkspaceMember"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"InviteWorkspaceMemberInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"inviteWorkspaceMember"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"workspaceMembership"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]}}]}}]} as unknown as DocumentNode<InviteWorkspaceMemberMutation, InviteWorkspaceMemberMutationVariables>;
export const PipelineRecipientsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelineRecipients"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"id"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"id"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"recipients"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"notificationLevel"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeletePipelineRecipientTrigger_recipient"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspace"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}}]}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"DeletePipelineRecipientTrigger_pipeline"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineRecipientTrigger_recipient"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineRecipient"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"DeletePipelineRecipientTrigger_pipeline"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Pipeline"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"update"}}]}}]}}]} as unknown as DocumentNode<PipelineRecipientsQuery, PipelineRecipientsQueryVariables>;
export const UpdatePipelineVersionConfigDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdatePipelineVersionConfig"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdatePipelineVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePipelineVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipelineVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"config"}}]}}]}}]}}]} as unknown as DocumentNode<UpdatePipelineVersionConfigMutation, UpdatePipelineVersionConfigMutationVariables>;
export const PipelineVersionPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelineVersionPicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"versions"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineVersionPicker_version"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineVersionPicker_version"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineVersion"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]} as unknown as DocumentNode<PipelineVersionPickerQuery, PipelineVersionPickerQueryVariables>;
export const GetConnectionBySlugDhis2Document = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"getConnectionBySlugDhis2"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"connectionSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"type"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DHIS2MetadataType"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"filters"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"connectionBySlug"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"connectionSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"connectionSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"DHIS2Connection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"queryMetadata"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"type"},"value":{"kind":"Variable","name":{"kind":"Name","value":"type"}}},{"kind":"Argument","name":{"kind":"Name","value":"filters"},"value":{"kind":"Variable","name":{"kind":"Name","value":"filters"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"error"}}]}}]}}]}}]}}]} as unknown as DocumentNode<GetConnectionBySlugDhis2Query, GetConnectionBySlugDhis2QueryVariables>;
export const GetConnectionBySlugIasoDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"getConnectionBySlugIaso"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"connectionSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"type"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"IASOMetadataType"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"search"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"filters"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"IASOQueryFilterInput"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"connectionBySlug"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"connectionSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"connectionSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"InlineFragment","typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"IASOConnection"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"queryMetadata"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"type"},"value":{"kind":"Variable","name":{"kind":"Name","value":"type"}}},{"kind":"Argument","name":{"kind":"Name","value":"search"},"value":{"kind":"Variable","name":{"kind":"Name","value":"search"}}},{"kind":"Argument","name":{"kind":"Name","value":"filters"},"value":{"kind":"Variable","name":{"kind":"Name","value":"filters"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"label"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"error"}}]}}]}}]}}]}}]} as unknown as DocumentNode<GetConnectionBySlugIasoQuery, GetConnectionBySlugIasoQueryVariables>;
export const PipelineCurrentVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"PipelineCurrentVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipelineByCode"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"code"},"value":{"kind":"Variable","name":{"kind":"Name","value":"pipelineCode"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionName"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"parameters"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"ParameterField_parameter"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"ParameterField_parameter"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineParameter"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"help"}},{"kind":"Field","name":{"kind":"Name","value":"type"}},{"kind":"Field","name":{"kind":"Name","value":"default"}},{"kind":"Field","name":{"kind":"Name","value":"required"}},{"kind":"Field","name":{"kind":"Name","value":"choices"}},{"kind":"Field","name":{"kind":"Name","value":"connection"}},{"kind":"Field","name":{"kind":"Name","value":"widget"}},{"kind":"Field","name":{"kind":"Name","value":"multiple"}},{"kind":"Field","name":{"kind":"Name","value":"directory"}}]}}]} as unknown as DocumentNode<PipelineCurrentVersionQuery, PipelineCurrentVersionQueryVariables>;
export const SidebarMenuDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"SidebarMenu"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pendingWorkspaceInvitations"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}}]}},{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"flag"}}]}}]}}]}}]}}]} as unknown as DocumentNode<SidebarMenuQuery, SidebarMenuQueryVariables>;
export const StopPipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"stopPipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"StopPipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"stopPipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<StopPipelineMutation, StopPipelineMutationVariables>;
export const GetUsersDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetUsers"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"users"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"organizationId"},"value":{"kind":"Variable","name":{"kind":"Name","value":"organizationId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}}]} as unknown as DocumentNode<GetUsersQuery, GetUsersQueryVariables>;
export const WorkspaceConnectionPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceConnectionPicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceConnectionPicker_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceConnectionPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"connections"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]}}]} as unknown as DocumentNode<WorkspaceConnectionPickerQuery, WorkspaceConnectionPickerQueryVariables>;
export const DeleteWorkspaceInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deleteWorkspaceInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteWorkspaceInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteWorkspaceInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteWorkspaceInvitationMutation, DeleteWorkspaceInvitationMutationVariables>;
export const ResendWorkspaceInvitationDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"resendWorkspaceInvitation"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"ResendWorkspaceInvitationInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"resendWorkspaceInvitation"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<ResendWorkspaceInvitationMutation, ResendWorkspaceInvitationMutationVariables>;
export const WorkspaceInvitationsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceInvitations"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}}]}},{"kind":"Field","name":{"kind":"Name","value":"invitations"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"invitedBy"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]}}]}}]} as unknown as DocumentNode<WorkspaceInvitationsQuery, WorkspaceInvitationsQueryVariables>;
export const WorkspaceMemberPickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceMemberPicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceMemberPicker_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceMemberPicker_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"members"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]}}]}}]} as unknown as DocumentNode<WorkspaceMemberPickerQuery, WorkspaceMemberPickerQueryVariables>;
export const DeleteWorkspaceMemberDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deleteWorkspaceMember"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteWorkspaceMemberInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteWorkspaceMember"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteWorkspaceMemberMutation, DeleteWorkspaceMemberMutationVariables>;
export const UpdateWorkspaceMemberDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"updateWorkspaceMember"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateWorkspaceMemberInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updateWorkspaceMember"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"workspaceMembership"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}}]}}]}}]}}]} as unknown as DocumentNode<UpdateWorkspaceMemberMutation, UpdateWorkspaceMemberMutationVariables>;
export const WorskspaceMembersDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorskspaceMembers"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"slug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"slug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}}]}},{"kind":"Field","name":{"kind":"Name","value":"members"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"role"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"email"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organizationMembership"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"role"}}]}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}}]}}]}}]}}]}}]} as unknown as DocumentNode<WorskspaceMembersQuery, WorskspaceMembersQueryVariables>;
export const WorkspacePickerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePicker"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"query"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}},"defaultValue":{"kind":"IntValue","value":"10"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"query"},"value":{"kind":"Variable","name":{"kind":"Name","value":"query"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspacePicker_value"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspacePicker_value"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<WorkspacePickerQuery, WorkspacePickerQueryVariables>;
export const DeleteWorkspaceDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deleteWorkspace"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteWorkspaceInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteWorkspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteWorkspaceMutation, DeleteWorkspaceMutationVariables>;
export const CreatePipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"createPipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreatePipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createPipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}}]}}]}}]} as unknown as DocumentNode<CreatePipelineMutation, CreatePipelineMutationVariables>;
export const DeletePipelineVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deletePipelineVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeletePipelineVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deletePipelineVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineVersionMutation, DeletePipelineVersionMutationVariables>;
export const AddPipelineRecipientDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"addPipelineRecipient"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreatePipelineRecipientInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"addPipelineRecipient"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<AddPipelineRecipientMutation, AddPipelineRecipientMutationVariables>;
export const WorkspacesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacesPage"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspaces"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"IntValue","value":"1"}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"IntValue","value":"1"}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}}]}}]}}]}}]} as unknown as DocumentNode<WorkspacesPageQuery, WorkspacesPageQueryVariables>;
export const WorkspacePipelineStartPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspacePipelineStartPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}}]} as unknown as DocumentNode<WorkspacePipelineStartPageQuery, WorkspacePipelineStartPageQueryVariables>;
export const WorkspaceTemplatesPageDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"WorkspaceTemplatesPage"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"page"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"workspace"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"slug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"WorkspaceLayout_workspace"}}]}},{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplates"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"workspaceSlug"},"value":{"kind":"Variable","name":{"kind":"Name","value":"workspaceSlug"}}},{"kind":"Argument","name":{"kind":"Name","value":"page"},"value":{"kind":"Variable","name":{"kind":"Name","value":"page"}}},{"kind":"Argument","name":{"kind":"Name","value":"perPage"},"value":{"kind":"Variable","name":{"kind":"Name","value":"perPage"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"items"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"TemplateCard_template"}}]}},{"kind":"Field","name":{"kind":"Name","value":"totalItems"}},{"kind":"Field","name":{"kind":"Name","value":"totalPages"}},{"kind":"Field","name":{"kind":"Name","value":"pageNumber"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"SidebarMenu_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"countries"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"flag"}},{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"organization"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"shortName"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createWorkspace"}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Sidebar_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"SidebarMenu_workspace"}},{"kind":"Field","name":{"kind":"Name","value":"permissions"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"manageMembers"}},{"kind":"Field","name":{"kind":"Name","value":"update"}},{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"PipelineMetadataDisplay_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"UserAvatar_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"Field","name":{"kind":"Name","value":"avatar"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"initials"}},{"kind":"Field","name":{"kind":"Name","value":"color"}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"User_user"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"User"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"email"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"UserAvatar_user"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"WorkspaceLayout_workspace"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Workspace"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"slug"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"Sidebar_workspace"}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"TemplateCard_template"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"PipelineTemplate"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"code"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"FragmentSpread","name":{"kind":"Name","value":"PipelineMetadataDisplay_template"}},{"kind":"Field","name":{"kind":"Name","value":"currentVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"createdAt"}},{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"User_user"}}]}}]}}]}}]} as unknown as DocumentNode<WorkspaceTemplatesPageQuery, WorkspaceTemplatesPageQueryVariables>;
export const GetTemplateVersionForDownloadDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"GetTemplateVersionForDownload"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UUID"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"pipelineTemplateVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"id"},"value":{"kind":"Variable","name":{"kind":"Name","value":"versionId"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"versionNumber"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"code"}}]}},{"kind":"Field","name":{"kind":"Name","value":"sourcePipelineVersion"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"zipfile"}}]}}]}}]}}]} as unknown as DocumentNode<GetTemplateVersionForDownloadQuery, GetTemplateVersionForDownloadQueryVariables>;
export const GetFileDownloadUrlDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"GetFileDownloadUrl"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"PrepareObjectDownloadInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"prepareObjectDownload"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"downloadUrl"}}]}}]}}]} as unknown as DocumentNode<GetFileDownloadUrlMutation, GetFileDownloadUrlMutationVariables>;
export const DeleteBucketObjectDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deleteBucketObject"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteBucketObjectInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteBucketObject"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteBucketObjectMutation, DeleteBucketObjectMutationVariables>;
export const GetBucketUploadUrlDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"GetBucketUploadUrl"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"PrepareObjectUploadInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"prepareObjectUpload"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"uploadUrl"}}]}}]}}]} as unknown as DocumentNode<GetBucketUploadUrlMutation, GetBucketUploadUrlMutationVariables>;
export const CreateBucketFolderDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"CreateBucketFolder"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"CreateBucketFolderInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"createBucketFolder"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"folder"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"key"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"type"}}]}}]}}]}}]} as unknown as DocumentNode<CreateBucketFolderMutation, CreateBucketFolderMutationVariables>;
export const DeleteConnectionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteConnection"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteConnectionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteConnection"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteConnectionMutation, DeleteConnectionMutationVariables>;
export const DeleteWorkspaceDatabaseTableDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deleteWorkspaceDatabaseTable"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteWorkspaceDatabaseTableInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteWorkspaceDatabaseTable"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteWorkspaceDatabaseTableMutation, DeleteWorkspaceDatabaseTableMutationVariables>;
export const LaunchNotebookServerDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"launchNotebookServer"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"LaunchNotebookServerInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"launchNotebookServer"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"server"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"ready"}},{"kind":"Field","name":{"kind":"Name","value":"url"}}]}}]}}]}}]} as unknown as DocumentNode<LaunchNotebookServerMutation, LaunchNotebookServerMutationVariables>;
export const UpdateWorkspacePipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateWorkspacePipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdatePipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"schedule"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"updatedAt"}},{"kind":"Field","name":{"kind":"Name","value":"webhookEnabled"}},{"kind":"Field","name":{"kind":"Name","value":"webhookUrl"}},{"kind":"Field","name":{"kind":"Name","value":"autoUpdateFromTemplate"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}},{"kind":"Field","name":{"kind":"Name","value":"recipients"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"user"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"displayName"}}]}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<UpdateWorkspacePipelineMutation, UpdateWorkspacePipelineMutationVariables>;
export const RunWorkspacePipelineDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"RunWorkspacePipeline"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"RunPipelineInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"runPipeline"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"run"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"pipeline"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"__typename"}},{"kind":"Field","name":{"kind":"Name","value":"id"}}]}}]}}]}}]}}]} as unknown as DocumentNode<RunWorkspacePipelineMutation, RunWorkspacePipelineMutationVariables>;
export const DeletePipelineVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeletePipelineVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeletePipelineVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deletePipelineVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineVersionMutation, DeletePipelineVersionMutationVariables>;
export const UpdatePipelineRecipientDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"updatePipelineRecipient"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdatePipelineRecipientInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePipelineRecipient"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"recipient"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"notificationLevel"}}]}}]}}]}}]} as unknown as DocumentNode<UpdatePipelineRecipientMutation, UpdatePipelineRecipientMutationVariables>;
export const DeletePipelineRecipientDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"deletePipelineRecipient"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeletePipelineRecipientInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deletePipelineRecipient"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeletePipelineRecipientMutation, DeletePipelineRecipientMutationVariables>;
export const UpdateWorkspaceTemplateDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"UpdateWorkspaceTemplate"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"UpdateTemplateInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"updatePipelineTemplate"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}},{"kind":"Field","name":{"kind":"Name","value":"template"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}},{"kind":"Field","name":{"kind":"Name","value":"description"}},{"kind":"Field","name":{"kind":"Name","value":"config"}},{"kind":"Field","name":{"kind":"Name","value":"functionalType"}},{"kind":"Field","name":{"kind":"Name","value":"tags"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"FragmentSpread","name":{"kind":"Name","value":"Tag_tag"}}]}}]}}]}}]}},{"kind":"FragmentDefinition","name":{"kind":"Name","value":"Tag_tag"},"typeCondition":{"kind":"NamedType","name":{"kind":"Name","value":"Tag"}},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"name"}}]}}]} as unknown as DocumentNode<UpdateWorkspaceTemplateMutation, UpdateWorkspaceTemplateMutationVariables>;
export const DeleteTemplateVersionDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"mutation","name":{"kind":"Name","value":"DeleteTemplateVersion"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"input"}},"type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"DeleteTemplateVersionInput"}}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"deleteTemplateVersion"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"input"},"value":{"kind":"Variable","name":{"kind":"Name","value":"input"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"success"}},{"kind":"Field","name":{"kind":"Name","value":"errors"}}]}}]}}]} as unknown as DocumentNode<DeleteTemplateVersionMutation, DeleteTemplateVersionMutationVariables>;