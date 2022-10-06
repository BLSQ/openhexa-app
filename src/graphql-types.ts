export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: string;
  String: string;
  Boolean: boolean;
  Int: number;
  Float: number;
  AccessmodFilesetMetadata: any;
  Date: any;
  DateTime: any;
  JSON: any;
  MovingSpeeds: any;
  SimplifiedExtentType: any;
  StackPriorities: any;
  TimeThresholds: any;
  URL: any;
};

export type AccessmodAccessRequest = {
  __typename?: 'AccessmodAccessRequest';
  acceptedTos: Scalars['Boolean'];
  createdAt: Scalars['DateTime'];
  email: Scalars['String'];
  firstName: Scalars['String'];
  id: Scalars['String'];
  lastName: Scalars['String'];
  status: AccessmodAccessRequestStatus;
  updatedAt: Scalars['DateTime'];
};

export type AccessmodAccessRequestPage = {
  __typename?: 'AccessmodAccessRequestPage';
  items: Array<AccessmodAccessRequest>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
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
  authorizedActions: Array<AccessmodAnalysisAuthorizedActions>;
  barrier?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime'];
  dem?: Maybe<AccessmodFileset>;
  frictionSurface?: Maybe<AccessmodFileset>;
  healthFacilities?: Maybe<AccessmodFileset>;
  id: Scalars['String'];
  invertDirection?: Maybe<Scalars['Boolean']>;
  knightMove?: Maybe<Scalars['Boolean']>;
  landCover?: Maybe<AccessmodFileset>;
  maxTravelTime?: Maybe<Scalars['Int']>;
  movingSpeeds?: Maybe<Scalars['MovingSpeeds']>;
  name: Scalars['String'];
  owner?: Maybe<AccessmodOwner>;
  stack?: Maybe<AccessmodFileset>;
  stackPriorities?: Maybe<Scalars['StackPriorities']>;
  status: AccessmodAnalysisStatus;
  transportNetwork?: Maybe<AccessmodFileset>;
  travelTimes?: Maybe<AccessmodFileset>;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime'];
  water?: Maybe<AccessmodFileset>;
  waterAllTouched?: Maybe<Scalars['Boolean']>;
};

export enum AccessmodAccessibilityAnalysisAlgorithm {
  Anisotropic = 'ANISOTROPIC',
  Isotropic = 'ISOTROPIC'
}

export type AccessmodAnalysis = {
  author: User;
  authorizedActions: Array<AccessmodAnalysisAuthorizedActions>;
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  name: Scalars['String'];
  status: AccessmodAnalysisStatus;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime'];
};

export enum AccessmodAnalysisAuthorizedActions {
  Delete = 'DELETE',
  Run = 'RUN',
  Update = 'UPDATE'
}

export type AccessmodAnalysisPage = {
  __typename?: 'AccessmodAnalysisPage';
  items: Array<AccessmodAnalysis>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
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
  createdAt: Scalars['DateTime'];
  fileset?: Maybe<AccessmodFileset>;
  id: Scalars['String'];
  mimeType: Scalars['String'];
  name: Scalars['String'];
  updatedAt: Scalars['DateTime'];
  uri: Scalars['String'];
};

export type AccessmodFileset = AccessmodOwnership & {
  __typename?: 'AccessmodFileset';
  author: User;
  authorizedActions: Array<AccessmodFilesetAuthorizedActions>;
  createdAt: Scalars['DateTime'];
  files: Array<AccessmodFile>;
  id: Scalars['String'];
  metadata: Scalars['AccessmodFilesetMetadata'];
  mode: AccessmodFilesetMode;
  name: Scalars['String'];
  owner?: Maybe<AccessmodOwner>;
  role: AccessmodFilesetRole;
  status: AccessmodFilesetStatus;
  updatedAt: Scalars['DateTime'];
};

export enum AccessmodFilesetAuthorizedActions {
  CreateFile = 'CREATE_FILE',
  Delete = 'DELETE',
  Update = 'UPDATE'
}

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
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type AccessmodFilesetRole = {
  __typename?: 'AccessmodFilesetRole';
  code: AccessmodFilesetRoleCode;
  createdAt: Scalars['DateTime'];
  format: AccessmodFilesetFormat;
  id: Scalars['String'];
  name: Scalars['String'];
  updatedAt: Scalars['DateTime'];
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
  anisotropic?: Maybe<Scalars['Boolean']>;
  author: User;
  authorizedActions: Array<AccessmodAnalysisAuthorizedActions>;
  catchmentAreas?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime'];
  dem?: Maybe<AccessmodFileset>;
  frictionSurface?: Maybe<AccessmodFileset>;
  geographicCoverage?: Maybe<AccessmodFileset>;
  healthFacilities?: Maybe<AccessmodFileset>;
  hfProcessingOrder?: Maybe<Scalars['String']>;
  id: Scalars['String'];
  maxTravelTime?: Maybe<Scalars['Int']>;
  name: Scalars['String'];
  owner?: Maybe<AccessmodOwner>;
  population?: Maybe<AccessmodFileset>;
  status: AccessmodAnalysisStatus;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime'];
};

export type AccessmodOwner = Team | User;

export type AccessmodOwnership = {
  owner?: Maybe<AccessmodOwner>;
};

export type AccessmodProject = AccessmodOwnership & {
  __typename?: 'AccessmodProject';
  author: User;
  authorizedActions: Array<AccessmodProjectAuthorizedActions>;
  country: Country;
  createdAt: Scalars['DateTime'];
  crs: Scalars['Int'];
  dem?: Maybe<AccessmodFileset>;
  description: Scalars['String'];
  extent?: Maybe<Array<Array<Scalars['Float']>>>;
  id: Scalars['String'];
  name: Scalars['String'];
  owner?: Maybe<AccessmodOwner>;
  permissions: Array<AccessmodProjectPermission>;
  spatialResolution: Scalars['Int'];
  updatedAt: Scalars['DateTime'];
};

export enum AccessmodProjectAuthorizedActions {
  CreateAnalysis = 'CREATE_ANALYSIS',
  CreateFileset = 'CREATE_FILESET',
  CreatePermission = 'CREATE_PERMISSION',
  Delete = 'DELETE',
  Update = 'UPDATE'
}

export enum AccessmodProjectOrder {
  NameAsc = 'NAME_ASC',
  NameDesc = 'NAME_DESC',
  UpdatedAtAsc = 'UPDATED_AT_ASC',
  UpdatedAtDesc = 'UPDATED_AT_DESC'
}

export type AccessmodProjectPage = {
  __typename?: 'AccessmodProjectPage';
  items: Array<AccessmodProject>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type AccessmodProjectPermission = {
  __typename?: 'AccessmodProjectPermission';
  authorizedActions: Array<AccessmodProjectPermissionAuthorizedActions>;
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  mode: PermissionMode;
  project: AccessmodProject;
  team?: Maybe<Team>;
  updatedAt: Scalars['DateTime'];
  user?: Maybe<User>;
};

export enum AccessmodProjectPermissionAuthorizedActions {
  Delete = 'DELETE',
  Update = 'UPDATE'
}

export type AccessmodProjectPermissionPage = {
  __typename?: 'AccessmodProjectPermissionPage';
  items: Array<AccessmodProjectPermission>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type AccessmodZonalStatistics = AccessmodAnalysis & AccessmodOwnership & {
  __typename?: 'AccessmodZonalStatistics';
  author: User;
  authorizedActions: Array<AccessmodAnalysisAuthorizedActions>;
  boundaries?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  name: Scalars['String'];
  owner?: Maybe<AccessmodOwner>;
  population?: Maybe<AccessmodFileset>;
  status: AccessmodAnalysisStatus;
  timeThresholds?: Maybe<Scalars['TimeThresholds']>;
  travelTimes?: Maybe<AccessmodFileset>;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime'];
  zonalStatisticsGeo?: Maybe<AccessmodFileset>;
  zonalStatisticsTable?: Maybe<AccessmodFileset>;
};

export enum ApproveAccessmodAccessRequestError {
  Invalid = 'INVALID'
}

export type ApproveAccessmodAccessRequestInput = {
  id: Scalars['String'];
};

export type ApproveAccessmodAccessRequestResult = {
  __typename?: 'ApproveAccessmodAccessRequestResult';
  errors: Array<ApproveAccessmodAccessRequestError>;
  success: Scalars['Boolean'];
};

export type AuthorizedActions = {
  __typename?: 'AuthorizedActions';
  createCollection: Scalars['Boolean'];
  createTeam: Scalars['Boolean'];
};

export type Avatar = {
  __typename?: 'Avatar';
  color: Scalars['String'];
  initials: Scalars['String'];
};

export type CatalogEntry = {
  __typename?: 'CatalogEntry';
  countries: Array<Country>;
  datasource?: Maybe<Datasource>;
  description?: Maybe<Scalars['String']>;
  externalDescription?: Maybe<Scalars['String']>;
  externalId?: Maybe<Scalars['String']>;
  externalName?: Maybe<Scalars['String']>;
  externalSubtype?: Maybe<Scalars['String']>;
  externalType?: Maybe<Scalars['String']>;
  id: Scalars['String'];
  lastSyncedAt?: Maybe<Scalars['DateTime']>;
  name: Scalars['String'];
  objectId: Scalars['String'];
  objectUrl: Scalars['URL'];
  symbol?: Maybe<Scalars['URL']>;
  type: CatalogEntryType;
};

export type CatalogEntryType = {
  __typename?: 'CatalogEntryType';
  app: Scalars['String'];
  id: Scalars['String'];
  model: Scalars['String'];
  name: Scalars['String'];
};

export type CatalogPage = {
  __typename?: 'CatalogPage';
  items: Array<CatalogEntry>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type Collection = {
  __typename?: 'Collection';
  author?: Maybe<User>;
  authorizedActions: CollectionAuthorizedActions;
  countries: Array<Country>;
  createdAt: Scalars['DateTime'];
  description?: Maybe<Scalars['String']>;
  elements: CollectionElementPage;
  id: Scalars['String'];
  name: Scalars['String'];
  summary?: Maybe<Scalars['String']>;
  tags: Array<Tag>;
  updatedAt: Scalars['DateTime'];
};


export type CollectionElementsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
};

export type CollectionAuthorizedActions = {
  __typename?: 'CollectionAuthorizedActions';
  canDelete: Scalars['Boolean'];
  canUpdate: Scalars['Boolean'];
};

export type CollectionElement = {
  __typename?: 'CollectionElement';
  app: Scalars['String'];
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  model: Scalars['String'];
  name: Scalars['String'];
  objectId: Scalars['String'];
  type: Scalars['String'];
  updatedAt: Scalars['DateTime'];
  url?: Maybe<Scalars['URL']>;
};

export type CollectionElementPage = {
  __typename?: 'CollectionElementPage';
  items: Array<CollectionElement>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type CollectionPage = {
  __typename?: 'CollectionPage';
  items: Array<Collection>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type Country = {
  __typename?: 'Country';
  alpha3: Scalars['String'];
  code: Scalars['String'];
  flag: Scalars['String'];
  name: Scalars['String'];
  whoInfo: WhoInfo;
};

export type CountryInput = {
  alpha3?: InputMaybe<Scalars['String']>;
  code: Scalars['String'];
  flag?: InputMaybe<Scalars['String']>;
  name?: InputMaybe<Scalars['String']>;
};

export enum CreateAccessmodAccessibilityAnalysisError {
  NameDuplicate = 'NAME_DUPLICATE'
}

export type CreateAccessmodAccessibilityAnalysisInput = {
  name: Scalars['String'];
  projectId: Scalars['String'];
};

export type CreateAccessmodAccessibilityAnalysisResult = {
  __typename?: 'CreateAccessmodAccessibilityAnalysisResult';
  analysis?: Maybe<AccessmodAccessibilityAnalysis>;
  errors: Array<CreateAccessmodAccessibilityAnalysisError>;
  success: Scalars['Boolean'];
};

export enum CreateAccessmodFileError {
  UriDuplicate = 'URI_DUPLICATE'
}

export type CreateAccessmodFileInput = {
  filesetId: Scalars['String'];
  mimeType: Scalars['String'];
  uri: Scalars['String'];
};

export type CreateAccessmodFileResult = {
  __typename?: 'CreateAccessmodFileResult';
  errors: Array<CreateAccessmodFileError>;
  file?: Maybe<AccessmodFile>;
  success: Scalars['Boolean'];
};

export enum CreateAccessmodFilesetError {
  NameDuplicate = 'NAME_DUPLICATE',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateAccessmodFilesetInput = {
  automatic?: InputMaybe<Scalars['Boolean']>;
  metadata?: InputMaybe<Scalars['AccessmodFilesetMetadata']>;
  name: Scalars['String'];
  projectId: Scalars['String'];
  roleId: Scalars['String'];
};

export type CreateAccessmodFilesetResult = {
  __typename?: 'CreateAccessmodFilesetResult';
  errors: Array<CreateAccessmodFilesetError>;
  fileset?: Maybe<AccessmodFileset>;
  success: Scalars['Boolean'];
};

export enum CreateAccessmodProjectError {
  NameDuplicate = 'NAME_DUPLICATE',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateAccessmodProjectInput = {
  country: CountryInput;
  crs: Scalars['Int'];
  description?: InputMaybe<Scalars['String']>;
  extent?: InputMaybe<Array<Array<Scalars['Float']>>>;
  name: Scalars['String'];
  spatialResolution: Scalars['Int'];
};

export enum CreateAccessmodProjectPermissionError {
  AlreadyExists = 'ALREADY_EXISTS',
  NotFound = 'NOT_FOUND',
  NotImplemented = 'NOT_IMPLEMENTED',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateAccessmodProjectPermissionInput = {
  mode: PermissionMode;
  projectId: Scalars['String'];
  teamId?: InputMaybe<Scalars['String']>;
  userId?: InputMaybe<Scalars['String']>;
};

export type CreateAccessmodProjectPermissionResult = {
  __typename?: 'CreateAccessmodProjectPermissionResult';
  errors: Array<CreateAccessmodProjectPermissionError>;
  permission?: Maybe<AccessmodProjectPermission>;
  success: Scalars['Boolean'];
};

export type CreateAccessmodProjectResult = {
  __typename?: 'CreateAccessmodProjectResult';
  errors: Array<CreateAccessmodProjectError>;
  project?: Maybe<AccessmodProject>;
  success: Scalars['Boolean'];
};

export enum CreateAccessmodZonalStatisticsError {
  NameDuplicate = 'NAME_DUPLICATE'
}

export type CreateAccessmodZonalStatisticsInput = {
  name: Scalars['String'];
  projectId: Scalars['String'];
};

export type CreateAccessmodZonalStatisticsResult = {
  __typename?: 'CreateAccessmodZonalStatisticsResult';
  analysis?: Maybe<AccessmodZonalStatistics>;
  errors: Array<CreateAccessmodZonalStatisticsError>;
  success: Scalars['Boolean'];
};

export enum CreateCollectionElementError {
  CollectionNotFound = 'COLLECTION_NOT_FOUND',
  Invalid = 'INVALID',
  ObjectNotFound = 'OBJECT_NOT_FOUND'
}

export type CreateCollectionElementInput = {
  app: Scalars['String'];
  collectionId: Scalars['String'];
  model: Scalars['String'];
  objectId: Scalars['String'];
};

export type CreateCollectionElementResult = {
  __typename?: 'CreateCollectionElementResult';
  element?: Maybe<CollectionElement>;
  errors: Array<CreateCollectionElementError>;
  success: Scalars['Boolean'];
};

export enum CreateCollectionError {
  Invalid = 'INVALID'
}

export type CreateCollectionInput = {
  authorId?: InputMaybe<Scalars['String']>;
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']>;
  name: Scalars['String'];
  summary?: InputMaybe<Scalars['String']>;
  tagIds?: InputMaybe<Array<Scalars['String']>>;
};

export type CreateCollectionResult = {
  __typename?: 'CreateCollectionResult';
  collection?: Maybe<Collection>;
  errors: Array<CreateCollectionError>;
  success: Scalars['Boolean'];
};

export enum CreateMembershipError {
  AlreadyExists = 'ALREADY_EXISTS',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateMembershipInput = {
  role: MembershipRole;
  teamId: Scalars['String'];
  userEmail: Scalars['String'];
};

export type CreateMembershipResult = {
  __typename?: 'CreateMembershipResult';
  errors: Array<CreateMembershipError>;
  membership?: Maybe<Membership>;
  success: Scalars['Boolean'];
};

export enum CreateTeamError {
  NameDuplicate = 'NAME_DUPLICATE',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type CreateTeamInput = {
  name: Scalars['String'];
};

export type CreateTeamResult = {
  __typename?: 'CreateTeamResult';
  errors: Array<CreateTeamError>;
  success: Scalars['Boolean'];
  team?: Maybe<Team>;
};

export type Dag = {
  __typename?: 'DAG';
  countries: Array<Country>;
  description?: Maybe<Scalars['String']>;
  externalId: Scalars['String'];
  externalUrl?: Maybe<Scalars['URL']>;
  formCode?: Maybe<Scalars['String']>;
  id: Scalars['String'];
  label: Scalars['String'];
  runs: DagRunPage;
  schedule?: Maybe<Scalars['String']>;
  tags: Array<Tag>;
  template: DagTemplate;
  user?: Maybe<User>;
};


export type DagRunsArgs = {
  orderBy?: InputMaybe<DagRunOrderBy>;
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
};

export type DagPage = {
  __typename?: 'DAGPage';
  items: Array<Dag>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type DagRun = {
  __typename?: 'DAGRun';
  config?: Maybe<Scalars['JSON']>;
  duration?: Maybe<Scalars['Int']>;
  executionDate?: Maybe<Scalars['DateTime']>;
  externalId?: Maybe<Scalars['String']>;
  externalUrl?: Maybe<Scalars['URL']>;
  id: Scalars['String'];
  lastRefreshedAt?: Maybe<Scalars['DateTime']>;
  logs?: Maybe<Scalars['String']>;
  messages: Array<DagRunMessage>;
  outputs: Array<DagRunOutput>;
  progress: Scalars['Int'];
  status: DagRunStatus;
  triggerMode?: Maybe<DagRunTrigger>;
  user?: Maybe<User>;
};

export type DagRunMessage = {
  __typename?: 'DAGRunMessage';
  message: Scalars['String'];
  priority: Scalars['String'];
  timestamp?: Maybe<Scalars['DateTime']>;
};

export enum DagRunOrderBy {
  ExecutionDateAsc = 'EXECUTION_DATE_ASC',
  ExecutionDateDesc = 'EXECUTION_DATE_DESC'
}

export type DagRunOutput = {
  __typename?: 'DAGRunOutput';
  title: Scalars['String'];
  uri: Scalars['String'];
};

export type DagRunPage = {
  __typename?: 'DAGRunPage';
  items: Array<DagRun>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
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
  code: Scalars['String'];
  description?: Maybe<Scalars['String']>;
  sampleConfig?: Maybe<Scalars['JSON']>;
};

export type Dhis2DataElement = {
  __typename?: 'DHIS2DataElement';
  code: Scalars['String'];
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  instance: Dhis2Instance;
  name: Scalars['String'];
  updatedAt: Scalars['DateTime'];
};

export type Dhis2DataElementPage = {
  __typename?: 'DHIS2DataElementPage';
  items: Array<Dhis2DataElement>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type Dhis2Instance = {
  __typename?: 'DHIS2Instance';
  id: Scalars['String'];
  name: Scalars['String'];
  url?: Maybe<Scalars['String']>;
};

export type Datasource = {
  __typename?: 'Datasource';
  id: Scalars['String'];
  name: Scalars['String'];
};

export enum DeleteAccessmodAnalysisError {
  DeleteFailed = 'DELETE_FAILED',
  NotFound = 'NOT_FOUND'
}

export type DeleteAccessmodAnalysisInput = {
  id: Scalars['String'];
};

export type DeleteAccessmodAnalysisResult = {
  __typename?: 'DeleteAccessmodAnalysisResult';
  errors: Array<DeleteAccessmodAnalysisError>;
  success: Scalars['Boolean'];
};

export enum DeleteAccessmodFilesetError {
  FilesetInUse = 'FILESET_IN_USE',
  NotFound = 'NOT_FOUND'
}

export type DeleteAccessmodFilesetInput = {
  id: Scalars['String'];
};

export type DeleteAccessmodFilesetResult = {
  __typename?: 'DeleteAccessmodFilesetResult';
  errors: Array<DeleteAccessmodFilesetError>;
  success: Scalars['Boolean'];
};

export enum DeleteAccessmodProjectError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteAccessmodProjectInput = {
  id: Scalars['String'];
};

export enum DeleteAccessmodProjectPermissionError {
  NotFound = 'NOT_FOUND',
  NotImplemented = 'NOT_IMPLEMENTED',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteAccessmodProjectPermissionInput = {
  id: Scalars['String'];
};

export type DeleteAccessmodProjectPermissionResult = {
  __typename?: 'DeleteAccessmodProjectPermissionResult';
  errors: Array<DeleteAccessmodProjectPermissionError>;
  success: Scalars['Boolean'];
};

export type DeleteAccessmodProjectResult = {
  __typename?: 'DeleteAccessmodProjectResult';
  errors: Array<DeleteAccessmodProjectError>;
  success: Scalars['Boolean'];
};

export enum DeleteCollectionElementError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type DeleteCollectionElementInput = {
  id: Scalars['String'];
};

export type DeleteCollectionElementResult = {
  __typename?: 'DeleteCollectionElementResult';
  collection?: Maybe<Collection>;
  errors: Array<DeleteCollectionElementError>;
  success: Scalars['Boolean'];
};

export enum DeleteCollectionError {
  Invalid = 'INVALID'
}

export type DeleteCollectionInput = {
  id: Scalars['String'];
};

export type DeleteCollectionResult = {
  __typename?: 'DeleteCollectionResult';
  errors: Array<DeleteCollectionError>;
  success: Scalars['Boolean'];
};

export enum DeleteMembershipError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteMembershipInput = {
  id: Scalars['String'];
};

export type DeleteMembershipResult = {
  __typename?: 'DeleteMembershipResult';
  errors: Array<DeleteMembershipError>;
  success: Scalars['Boolean'];
};

export enum DeleteTeamError {
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type DeleteTeamInput = {
  id: Scalars['String'];
};

export type DeleteTeamResult = {
  __typename?: 'DeleteTeamResult';
  errors: Array<DeleteTeamError>;
  success: Scalars['Boolean'];
};

export enum DenyAccessmodAccessRequestError {
  Invalid = 'INVALID'
}

export type DenyAccessmodAccessRequestInput = {
  id: Scalars['String'];
};

export type DenyAccessmodAccessRequestResult = {
  __typename?: 'DenyAccessmodAccessRequestResult';
  errors: Array<DenyAccessmodAccessRequestError>;
  success: Scalars['Boolean'];
};

export type FeatureFlag = {
  __typename?: 'FeatureFlag';
  code: Scalars['String'];
  config: Scalars['JSON'];
};

export enum LaunchAccessmodAnalysisError {
  LaunchFailed = 'LAUNCH_FAILED'
}

export type LaunchAccessmodAnalysisInput = {
  id: Scalars['String'];
};

export type LaunchAccessmodAnalysisResult = {
  __typename?: 'LaunchAccessmodAnalysisResult';
  analysis?: Maybe<AccessmodAnalysis>;
  errors: Array<LaunchAccessmodAnalysisError>;
  success: Scalars['Boolean'];
};

export type LoginInput = {
  email: Scalars['String'];
  password: Scalars['String'];
};

export type LoginResult = {
  __typename?: 'LoginResult';
  me?: Maybe<Me>;
  success: Scalars['Boolean'];
};

export type LogoutResult = {
  __typename?: 'LogoutResult';
  success: Scalars['Boolean'];
};

export type Me = {
  __typename?: 'Me';
  authorizedActions: Array<MeAuthorizedActions>;
  features: Array<FeatureFlag>;
  user?: Maybe<User>;
};

export enum MeAuthorizedActions {
  AdminPanel = 'ADMIN_PANEL',
  CreateAccessmodProject = 'CREATE_ACCESSMOD_PROJECT',
  CreateTeam = 'CREATE_TEAM',
  ManageAccessmodAccessRequests = 'MANAGE_ACCESSMOD_ACCESS_REQUESTS'
}

export type Membership = {
  __typename?: 'Membership';
  authorizedActions: Array<MembershipAuthorizedActions>;
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  role: MembershipRole;
  team: Team;
  updatedAt: Scalars['DateTime'];
  user: User;
};

export enum MembershipAuthorizedActions {
  Delete = 'DELETE',
  Update = 'UPDATE'
}

export type MembershipPage = {
  __typename?: 'MembershipPage';
  items: Array<Membership>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export enum MembershipRole {
  Admin = 'ADMIN',
  Regular = 'REGULAR'
}

export type Mutation = {
  __typename?: 'Mutation';
  approveAccessmodAccessRequest: ApproveAccessmodAccessRequestResult;
  createAccessmodAccessibilityAnalysis: CreateAccessmodAccessibilityAnalysisResult;
  createAccessmodFile: CreateAccessmodFileResult;
  createAccessmodFileset: CreateAccessmodFilesetResult;
  createAccessmodProject: CreateAccessmodProjectResult;
  createAccessmodProjectPermission: CreateAccessmodProjectPermissionResult;
  createAccessmodZonalStatistics: CreateAccessmodZonalStatisticsResult;
  createCollection: CreateCollectionResult;
  createCollectionElement: CreateCollectionElementResult;
  createMembership: CreateMembershipResult;
  createTeam: CreateTeamResult;
  deleteAccessmodAnalysis: DeleteAccessmodAnalysisResult;
  deleteAccessmodFileset: DeleteAccessmodFilesetResult;
  deleteAccessmodProject: DeleteAccessmodProjectResult;
  deleteAccessmodProjectPermission: DeleteAccessmodProjectPermissionResult;
  deleteCollection: DeleteCollectionResult;
  deleteCollectionElement: DeleteCollectionElementResult;
  deleteMembership: DeleteMembershipResult;
  deleteTeam: DeleteTeamResult;
  denyAccessmodAccessRequest: DenyAccessmodAccessRequestResult;
  launchAccessmodAnalysis: LaunchAccessmodAnalysisResult;
  login: LoginResult;
  logout: LogoutResult;
  prepareAccessmodFileDownload: PrepareAccessmodFileDownloadResult;
  prepareAccessmodFileUpload: PrepareAccessmodFileUploadResult;
  prepareAccessmodFilesetVisualizationDownload: PrepareAccessmodFilesetVisualizationDownloadResult;
  prepareDownloadURL?: Maybe<PrepareDownloadUrlResult>;
  requestAccessmodAccess: RequestAccessmodAccessInputResult;
  resetPassword: ResetPasswordResult;
  runDAG: RunDagResult;
  setPassword: SetPasswordResult;
  updateAccessmodAccessibilityAnalysis: UpdateAccessmodAccessibilityAnalysisResult;
  updateAccessmodFileset: UpdateAccessmodFilesetResult;
  updateAccessmodProject: UpdateAccessmodProjectResult;
  updateAccessmodProjectPermission: UpdateAccessmodProjectPermissionResult;
  updateAccessmodZonalStatistics: UpdateAccessmodZonalStatisticsResult;
  updateCollection: UpdateCollectionResult;
  updateDAG: UpdateDagResult;
  updateMembership: UpdateMembershipResult;
  updateTeam: UpdateTeamResult;
};


export type MutationApproveAccessmodAccessRequestArgs = {
  input: ApproveAccessmodAccessRequestInput;
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


export type MutationCreateAccessmodProjectPermissionArgs = {
  input: CreateAccessmodProjectPermissionInput;
};


export type MutationCreateAccessmodZonalStatisticsArgs = {
  input?: InputMaybe<CreateAccessmodZonalStatisticsInput>;
};


export type MutationCreateCollectionArgs = {
  input: CreateCollectionInput;
};


export type MutationCreateCollectionElementArgs = {
  input: CreateCollectionElementInput;
};


export type MutationCreateMembershipArgs = {
  input: CreateMembershipInput;
};


export type MutationCreateTeamArgs = {
  input: CreateTeamInput;
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


export type MutationDeleteAccessmodProjectPermissionArgs = {
  input: DeleteAccessmodProjectPermissionInput;
};


export type MutationDeleteCollectionArgs = {
  input: DeleteCollectionInput;
};


export type MutationDeleteCollectionElementArgs = {
  input: DeleteCollectionElementInput;
};


export type MutationDeleteMembershipArgs = {
  input: DeleteMembershipInput;
};


export type MutationDeleteTeamArgs = {
  input: DeleteTeamInput;
};


export type MutationDenyAccessmodAccessRequestArgs = {
  input: DenyAccessmodAccessRequestInput;
};


export type MutationLaunchAccessmodAnalysisArgs = {
  input?: InputMaybe<LaunchAccessmodAnalysisInput>;
};


export type MutationLoginArgs = {
  input: LoginInput;
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


export type MutationRequestAccessmodAccessArgs = {
  input: RequestAccessmodAccessInput;
};


export type MutationResetPasswordArgs = {
  input: ResetPasswordInput;
};


export type MutationRunDagArgs = {
  input: RunDagInput;
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


export type MutationUpdateAccessmodProjectPermissionArgs = {
  input: UpdateAccessmodProjectPermissionInput;
};


export type MutationUpdateAccessmodZonalStatisticsArgs = {
  input?: InputMaybe<UpdateAccessmodZonalStatisticsInput>;
};


export type MutationUpdateCollectionArgs = {
  input: UpdateCollectionInput;
};


export type MutationUpdateDagArgs = {
  input: UpdateDagInput;
};


export type MutationUpdateMembershipArgs = {
  input: UpdateMembershipInput;
};


export type MutationUpdateTeamArgs = {
  input: UpdateTeamInput;
};

export type Organization = {
  __typename?: 'Organization';
  contactInfo: Scalars['String'];
  id: Scalars['String'];
  name: Scalars['String'];
  type: Scalars['String'];
  url: Scalars['String'];
};

export type OrganizationInput = {
  contactInfo?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
  type?: InputMaybe<Scalars['String']>;
  url?: InputMaybe<Scalars['String']>;
};

export enum PermissionMode {
  Editor = 'EDITOR',
  Owner = 'OWNER',
  Viewer = 'VIEWER'
}

export type PrepareAccessmodFileDownloadInput = {
  fileId: Scalars['String'];
};

export type PrepareAccessmodFileDownloadResult = {
  __typename?: 'PrepareAccessmodFileDownloadResult';
  downloadUrl?: Maybe<Scalars['String']>;
  success: Scalars['Boolean'];
};

export type PrepareAccessmodFileUploadInput = {
  filesetId: Scalars['String'];
  mimeType: Scalars['String'];
};

export type PrepareAccessmodFileUploadResult = {
  __typename?: 'PrepareAccessmodFileUploadResult';
  fileUri?: Maybe<Scalars['String']>;
  success: Scalars['Boolean'];
  uploadUrl?: Maybe<Scalars['String']>;
};

export type PrepareAccessmodFilesetVisualizationDownloadInput = {
  id: Scalars['String'];
};

export type PrepareAccessmodFilesetVisualizationDownloadResult = {
  __typename?: 'PrepareAccessmodFilesetVisualizationDownloadResult';
  success: Scalars['Boolean'];
  url?: Maybe<Scalars['String']>;
};

export type PrepareDownloadUrlInput = {
  uri: Scalars['URL'];
};

export type PrepareDownloadUrlResult = {
  __typename?: 'PrepareDownloadURLResult';
  success: Scalars['Boolean'];
  url?: Maybe<Scalars['URL']>;
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
  countries: Array<Country>;
  country?: Maybe<Country>;
  dag?: Maybe<Dag>;
  dagRun?: Maybe<DagRun>;
  dags: DagPage;
  me: Me;
  organizations: Array<Organization>;
  search: SearchQueryResult;
  team?: Maybe<Team>;
  teams: TeamPage;
};


export type QueryAccessmodAccessRequestsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
};


export type QueryAccessmodAnalysesArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  projectId: Scalars['String'];
};


export type QueryAccessmodAnalysisArgs = {
  id?: InputMaybe<Scalars['String']>;
};


export type QueryAccessmodFilesetArgs = {
  id?: InputMaybe<Scalars['String']>;
};


export type QueryAccessmodFilesetRoleArgs = {
  id: Scalars['String'];
};


export type QueryAccessmodFilesetsArgs = {
  mode?: InputMaybe<AccessmodFilesetMode>;
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  projectId: Scalars['String'];
  roleId?: InputMaybe<Scalars['String']>;
  term?: InputMaybe<Scalars['String']>;
};


export type QueryAccessmodProjectArgs = {
  id?: InputMaybe<Scalars['String']>;
};


export type QueryAccessmodProjectsArgs = {
  countries?: InputMaybe<Array<Scalars['String']>>;
  orderBy?: InputMaybe<AccessmodProjectOrder>;
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  teams?: InputMaybe<Array<Scalars['String']>>;
  term?: InputMaybe<Scalars['String']>;
};


export type QueryBoundariesArgs = {
  country_code: Scalars['String'];
  level: Scalars['String'];
};


export type QueryCatalogArgs = {
  page?: InputMaybe<Scalars['Int']>;
  path?: InputMaybe<Scalars['String']>;
  perPage?: InputMaybe<Scalars['Int']>;
};


export type QueryCollectionArgs = {
  id: Scalars['String'];
};


export type QueryCollectionsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
};


export type QueryCountryArgs = {
  alpha3?: InputMaybe<Scalars['String']>;
  code?: InputMaybe<Scalars['String']>;
};


export type QueryDagArgs = {
  id: Scalars['String'];
};


export type QueryDagRunArgs = {
  id: Scalars['String'];
};


export type QueryDagsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
};


export type QuerySearchArgs = {
  datasourceIds?: InputMaybe<Array<Scalars['String']>>;
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  query?: InputMaybe<Scalars['String']>;
  types?: InputMaybe<Array<Scalars['String']>>;
};


export type QueryTeamArgs = {
  id: Scalars['String'];
};


export type QueryTeamsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  term?: InputMaybe<Scalars['String']>;
};

export enum RequestAccessmodAccessError {
  AlreadyExists = 'ALREADY_EXISTS',
  Invalid = 'INVALID',
  MustAcceptTos = 'MUST_ACCEPT_TOS'
}

export type RequestAccessmodAccessInput = {
  acceptTos: Scalars['Boolean'];
  email: Scalars['String'];
  firstName: Scalars['String'];
  lastName: Scalars['String'];
};

export type RequestAccessmodAccessInputResult = {
  __typename?: 'RequestAccessmodAccessInputResult';
  errors: Array<RequestAccessmodAccessError>;
  success: Scalars['Boolean'];
};

export type ResetPasswordInput = {
  email: Scalars['String'];
};

export type ResetPasswordResult = {
  __typename?: 'ResetPasswordResult';
  success: Scalars['Boolean'];
};

export enum RunDagError {
  DagNotFound = 'DAG_NOT_FOUND',
  InvalidConfig = 'INVALID_CONFIG'
}

export type RunDagInput = {
  config: Scalars['JSON'];
  dagId: Scalars['String'];
};

export type RunDagResult = {
  __typename?: 'RunDAGResult';
  dag?: Maybe<Dag>;
  dagRun?: Maybe<DagRun>;
  errors: Array<RunDagError>;
  success: Scalars['Boolean'];
};

export type S3Bucket = {
  __typename?: 'S3Bucket';
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  name: Scalars['String'];
  updatedAt: Scalars['DateTime'];
};

export type S3Object = {
  __typename?: 'S3Object';
  bucket: S3Bucket;
  collections: Array<Collection>;
  createdAt: Scalars['DateTime'];
  etag: Scalars['String'];
  filename: Scalars['String'];
  id: Scalars['String'];
  key: Scalars['String'];
  lastModified: Scalars['DateTime'];
  parentKey: Scalars['String'];
  size: Scalars['Int'];
  storageClass: Scalars['String'];
  type: Scalars['String'];
  updatedAt: Scalars['DateTime'];
};

export type S3ObjectPage = {
  __typename?: 'S3ObjectPage';
  items: Array<S3Object>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export type SearchQueryResult = {
  __typename?: 'SearchQueryResult';
  results: Array<SearchResult>;
  types: Array<SearchType>;
};

export type SearchResult = {
  __typename?: 'SearchResult';
  object: SearchResultObject;
  rank: Scalars['Float'];
};

export type SearchResultObject = CatalogEntry | Collection;

export type SearchType = {
  __typename?: 'SearchType';
  label: Scalars['String'];
  value: Scalars['String'];
};

export enum SetPasswordError {
  InvalidPassword = 'INVALID_PASSWORD',
  InvalidToken = 'INVALID_TOKEN',
  PasswordMismatch = 'PASSWORD_MISMATCH',
  UserNotFound = 'USER_NOT_FOUND'
}

export type SetPasswordInput = {
  password1: Scalars['String'];
  password2: Scalars['String'];
  token: Scalars['String'];
  uidb64: Scalars['String'];
};

export type SetPasswordResult = {
  __typename?: 'SetPasswordResult';
  error?: Maybe<SetPasswordError>;
  success: Scalars['Boolean'];
};

export type Tag = {
  __typename?: 'Tag';
  id: Scalars['String'];
  name: Scalars['String'];
};

export type Team = {
  __typename?: 'Team';
  authorizedActions: Array<TeamAuthorizedActions>;
  createdAt: Scalars['DateTime'];
  id: Scalars['String'];
  memberships: MembershipPage;
  name: Scalars['String'];
  updatedAt: Scalars['DateTime'];
};


export type TeamMembershipsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
};

export enum TeamAuthorizedActions {
  CreateMembership = 'CREATE_MEMBERSHIP',
  Delete = 'DELETE',
  Update = 'UPDATE'
}

export type TeamPage = {
  __typename?: 'TeamPage';
  items: Array<Team>;
  pageNumber: Scalars['Int'];
  totalItems: Scalars['Int'];
  totalPages: Scalars['Int'];
};

export enum UpdateAccessmodAccessibilityAnalysisError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND'
}

export type UpdateAccessmodAccessibilityAnalysisInput = {
  algorithm?: InputMaybe<AccessmodAccessibilityAnalysisAlgorithm>;
  barrierId?: InputMaybe<Scalars['String']>;
  demId?: InputMaybe<Scalars['String']>;
  healthFacilitiesId?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  invertDirection?: InputMaybe<Scalars['Boolean']>;
  knightMove?: InputMaybe<Scalars['Boolean']>;
  landCoverId?: InputMaybe<Scalars['String']>;
  maxTravelTime?: InputMaybe<Scalars['Int']>;
  movingSpeeds?: InputMaybe<Scalars['MovingSpeeds']>;
  name?: InputMaybe<Scalars['String']>;
  stackId?: InputMaybe<Scalars['String']>;
  stackPriorities?: InputMaybe<Scalars['StackPriorities']>;
  transportNetworkId?: InputMaybe<Scalars['String']>;
  waterAllTouched?: InputMaybe<Scalars['Boolean']>;
  waterId?: InputMaybe<Scalars['String']>;
};

export type UpdateAccessmodAccessibilityAnalysisResult = {
  __typename?: 'UpdateAccessmodAccessibilityAnalysisResult';
  analysis?: Maybe<AccessmodAccessibilityAnalysis>;
  errors: Array<UpdateAccessmodAccessibilityAnalysisError>;
  success: Scalars['Boolean'];
};

export enum UpdateAccessmodFilesetError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodFilesetInput = {
  id: Scalars['String'];
  metadata?: InputMaybe<Scalars['AccessmodFilesetMetadata']>;
  name?: InputMaybe<Scalars['String']>;
};

export type UpdateAccessmodFilesetResult = {
  __typename?: 'UpdateAccessmodFilesetResult';
  errors: Array<UpdateAccessmodFilesetError>;
  fileset?: Maybe<AccessmodFileset>;
  success: Scalars['Boolean'];
};

export enum UpdateAccessmodProjectError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodProjectInput = {
  description?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
};

export enum UpdateAccessmodProjectPermissionError {
  NotFound = 'NOT_FOUND',
  NotImplemented = 'NOT_IMPLEMENTED',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodProjectPermissionInput = {
  id: Scalars['String'];
  mode: PermissionMode;
};

export type UpdateAccessmodProjectPermissionResult = {
  __typename?: 'UpdateAccessmodProjectPermissionResult';
  errors: Array<UpdateAccessmodProjectPermissionError>;
  permission?: Maybe<AccessmodProjectPermission>;
  success: Scalars['Boolean'];
};

export type UpdateAccessmodProjectResult = {
  __typename?: 'UpdateAccessmodProjectResult';
  errors: Array<UpdateAccessmodProjectError>;
  project?: Maybe<AccessmodProject>;
  success: Scalars['Boolean'];
};

export enum UpdateAccessmodZonalStatisticsError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND'
}

export type UpdateAccessmodZonalStatisticsInput = {
  boundariesId?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
  populationId?: InputMaybe<Scalars['String']>;
  timeThresholds?: InputMaybe<Scalars['TimeThresholds']>;
  travelTimesId?: InputMaybe<Scalars['String']>;
};

export type UpdateAccessmodZonalStatisticsResult = {
  __typename?: 'UpdateAccessmodZonalStatisticsResult';
  analysis?: Maybe<AccessmodZonalStatistics>;
  errors: Array<UpdateAccessmodZonalStatisticsError>;
  success: Scalars['Boolean'];
};

export enum UpdateCollectionError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type UpdateCollectionInput = {
  authorId?: InputMaybe<Scalars['String']>;
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
  summary?: InputMaybe<Scalars['String']>;
  tagIds?: InputMaybe<Array<Scalars['String']>>;
};

export type UpdateCollectionResult = {
  __typename?: 'UpdateCollectionResult';
  collection?: Maybe<Collection>;
  errors: Array<CreateCollectionError>;
  success: Scalars['Boolean'];
};

export enum UpdateDagError {
  Invalid = 'INVALID',
  NotFound = 'NOT_FOUND'
}

export type UpdateDagInput = {
  countries?: InputMaybe<Array<CountryInput>>;
  description?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  label?: InputMaybe<Scalars['String']>;
  schedule?: InputMaybe<Scalars['String']>;
};

export type UpdateDagResult = {
  __typename?: 'UpdateDAGResult';
  dag?: Maybe<Dag>;
  errors: Array<UpdateDagError>;
  success: Scalars['Boolean'];
};

export enum UpdateMembershipError {
  InvalidRole = 'INVALID_ROLE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateMembershipInput = {
  id: Scalars['String'];
  role: MembershipRole;
};

export type UpdateMembershipResult = {
  __typename?: 'UpdateMembershipResult';
  errors: Array<UpdateMembershipError>;
  membership?: Maybe<Membership>;
  success: Scalars['Boolean'];
};

export enum UpdateTeamError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateTeamInput = {
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
};

export type UpdateTeamResult = {
  __typename?: 'UpdateTeamResult';
  errors: Array<UpdateTeamError>;
  success: Scalars['Boolean'];
  team?: Maybe<Team>;
};

export type User = {
  __typename?: 'User';
  avatar: Avatar;
  dateJoined: Scalars['DateTime'];
  displayName: Scalars['String'];
  email: Scalars['String'];
  firstName?: Maybe<Scalars['String']>;
  id: Scalars['String'];
  lastLogin?: Maybe<Scalars['DateTime']>;
  lastName?: Maybe<Scalars['String']>;
};

export type WhoBoundary = {
  __typename?: 'WHOBoundary';
  administrative_level: Scalars['Int'];
  country: Country;
  extent: Scalars['String'];
  id: Scalars['String'];
  name: Scalars['String'];
  parent?: Maybe<Scalars['String']>;
};

export type WhoInfo = {
  __typename?: 'WHOInfo';
  defaultCRS: Scalars['Int'];
  region?: Maybe<WhoRegion>;
  simplifiedExtent?: Maybe<Scalars['SimplifiedExtentType']>;
};

export type WhoRegion = {
  __typename?: 'WHORegion';
  code: Scalars['String'];
  name: Scalars['String'];
};
