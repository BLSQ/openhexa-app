import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
const defaultOptions = {} as const;
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
};

export type AccessmodAccessibilityAnalysis = AccessmodAnalysis & {
  __typename?: 'AccessmodAccessibilityAnalysis';
  algorithm?: Maybe<AccessmodAccessibilityAnalysisAlgorithm>;
  author: User;
  authorizedActions: Array<AccessmodAnalysisAuthorizedActions>;
  barrier?: Maybe<AccessmodFileset>;
  catchmentAreas?: Maybe<AccessmodFileset>;
  createdAt: Scalars['DateTime'];
  dem?: Maybe<AccessmodFileset>;
  frictionSurface?: Maybe<AccessmodFileset>;
  healthFacilities?: Maybe<AccessmodFileset>;
  id: Scalars['String'];
  invertDirection?: Maybe<Scalars['Boolean']>;
  knightMove?: Maybe<Scalars['Boolean']>;
  landCover?: Maybe<AccessmodFileset>;
  maxSlope?: Maybe<Scalars['Float']>;
  maxTravelTime?: Maybe<Scalars['Int']>;
  movingSpeeds?: Maybe<AccessmodFileset>;
  name: Scalars['String'];
  priorityLandCover?: Maybe<Array<Scalars['Int']>>;
  priorityRoads?: Maybe<Scalars['Boolean']>;
  slope?: Maybe<AccessmodFileset>;
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
  GeographicCoverage = 'GEOGRAPHIC_COVERAGE'
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

export type AccessmodFileset = {
  __typename?: 'AccessmodFileset';
  author: User;
  authorizedActions: Array<AccessmodFilesetAuthorizedActions>;
  createdAt: Scalars['DateTime'];
  files: Array<AccessmodFile>;
  id: Scalars['String'];
  metadata: Scalars['AccessmodFilesetMetadata'];
  name: Scalars['String'];
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
  CatchmentAreas = 'CATCHMENT_AREAS',
  Coverage = 'COVERAGE',
  Dem = 'DEM',
  FrictionSurface = 'FRICTION_SURFACE',
  Geometry = 'GEOMETRY',
  HealthFacilities = 'HEALTH_FACILITIES',
  LandCover = 'LAND_COVER',
  MovingSpeeds = 'MOVING_SPEEDS',
  Population = 'POPULATION',
  Slope = 'SLOPE',
  TransportNetwork = 'TRANSPORT_NETWORK',
  TravelTimes = 'TRAVEL_TIMES',
  Water = 'WATER'
}

export enum AccessmodFilesetStatus {
  Invalid = 'INVALID',
  Pending = 'PENDING',
  Valid = 'VALID',
  Validating = 'VALIDATING'
}

export type AccessmodGeographicCoverageAnalysis = AccessmodAnalysis & {
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
  population?: Maybe<AccessmodFileset>;
  status: AccessmodAnalysisStatus;
  type: AccessmodAnalysisType;
  updatedAt: Scalars['DateTime'];
};

export type AccessmodProject = {
  __typename?: 'AccessmodProject';
  author: User;
  authorizedActions: Array<AccessmodProjectAuthorizedActions>;
  country: Country;
  createdAt: Scalars['DateTime'];
  crs: Scalars['Int'];
  description: Scalars['String'];
  extent?: Maybe<AccessmodFileset>;
  id: Scalars['String'];
  name: Scalars['String'];
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

export type Avatar = {
  __typename?: 'Avatar';
  color: Scalars['String'];
  initials: Scalars['String'];
};

export type Country = {
  __typename?: 'Country';
  alpha3: Scalars['String'];
  code: Scalars['String'];
  flag: Scalars['String'];
  name: Scalars['String'];
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
  extentId?: InputMaybe<Scalars['String']>;
  name: Scalars['String'];
  spatialResolution: Scalars['Int'];
};

export enum CreateAccessmodProjectPermissionError {
  NotFound = 'NOT_FOUND',
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

export enum CreateMembershipError {
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

export enum DeleteAccessmodFileError {
  NotFound = 'NOT_FOUND'
}

export type DeleteAccessmodFileInput = {
  id: Scalars['String'];
};

export type DeleteAccessmodFileResult = {
  __typename?: 'DeleteAccessmodFileResult';
  errors: Array<DeleteAccessmodFileError>;
  success: Scalars['Boolean'];
};

export enum DeleteAccessmodFilesetError {
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
  user?: Maybe<User>;
};

export enum MeAuthorizedActions {
  CreateAccessmodProject = 'CREATE_ACCESSMOD_PROJECT',
  CreateTeam = 'CREATE_TEAM'
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
  createAccessmodAccessibilityAnalysis: CreateAccessmodAccessibilityAnalysisResult;
  createAccessmodFile: CreateAccessmodFileResult;
  createAccessmodFileset: CreateAccessmodFilesetResult;
  createAccessmodProject: CreateAccessmodProjectResult;
  createAccessmodProjectPermission: CreateAccessmodProjectPermissionResult;
  createMembership: CreateMembershipResult;
  createTeam: CreateTeamResult;
  deleteAccessmodAnalysis: DeleteAccessmodAnalysisResult;
  deleteAccessmodFile: DeleteAccessmodFileResult;
  deleteAccessmodFileset: DeleteAccessmodFilesetResult;
  deleteAccessmodProject: DeleteAccessmodProjectResult;
  deleteAccessmodProjectPermission: DeleteAccessmodProjectPermissionResult;
  deleteMembership: DeleteMembershipResult;
  deleteTeam: DeleteTeamResult;
  launchAccessmodAnalysis: LaunchAccessmodAnalysisResult;
  login: LoginResult;
  logout: LogoutResult;
  prepareAccessmodFileDownload: PrepareAccessmodFileDownloadResult;
  prepareAccessmodFileUpload: PrepareAccessmodFileUploadResult;
  resetPassword: ResetPasswordResult;
  setPassword: SetPasswordResult;
  updateAccessmodAccessibilityAnalysis: UpdateAccessmodAccessibilityAnalysisResult;
  updateAccessmodProject: UpdateAccessmodProjectResult;
  updateAccessmodProjectPermission: UpdateAccessmodProjectPermissionResult;
  updateMembership: UpdateMembershipResult;
  updateTeam: UpdateTeamResult;
};


export type MutationCreateAccessmodAccessibilityAnalysisArgs = {
  input?: InputMaybe<CreateAccessmodAccessibilityAnalysisInput>;
};


export type MutationCreateAccessmodFileArgs = {
  input?: InputMaybe<CreateAccessmodFileInput>;
};


export type MutationCreateAccessmodFilesetArgs = {
  input?: InputMaybe<CreateAccessmodFilesetInput>;
};


export type MutationCreateAccessmodProjectArgs = {
  input?: InputMaybe<CreateAccessmodProjectInput>;
};


export type MutationCreateAccessmodProjectPermissionArgs = {
  input: CreateAccessmodProjectPermissionInput;
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


export type MutationDeleteAccessmodFileArgs = {
  input?: InputMaybe<DeleteAccessmodFileInput>;
};


export type MutationDeleteAccessmodFilesetArgs = {
  input?: InputMaybe<DeleteAccessmodFilesetInput>;
};


export type MutationDeleteAccessmodProjectArgs = {
  input?: InputMaybe<DeleteAccessmodProjectInput>;
};


export type MutationDeleteAccessmodProjectPermissionArgs = {
  input: DeleteAccessmodProjectPermissionInput;
};


export type MutationDeleteMembershipArgs = {
  input: DeleteMembershipInput;
};


export type MutationDeleteTeamArgs = {
  input: DeleteTeamInput;
};


export type MutationLaunchAccessmodAnalysisArgs = {
  input?: InputMaybe<LaunchAccessmodAnalysisInput>;
};


export type MutationLoginArgs = {
  input: LoginInput;
};


export type MutationPrepareAccessmodFileDownloadArgs = {
  input?: InputMaybe<PrepareAccessmodFileDownloadInput>;
};


export type MutationPrepareAccessmodFileUploadArgs = {
  input?: InputMaybe<PrepareAccessmodFileUploadInput>;
};


export type MutationResetPasswordArgs = {
  input: ResetPasswordInput;
};


export type MutationSetPasswordArgs = {
  input: SetPasswordInput;
};


export type MutationUpdateAccessmodAccessibilityAnalysisArgs = {
  input?: InputMaybe<UpdateAccessmodAccessibilityAnalysisInput>;
};


export type MutationUpdateAccessmodProjectArgs = {
  input?: InputMaybe<UpdateAccessmodProjectInput>;
};


export type MutationUpdateAccessmodProjectPermissionArgs = {
  input: UpdateAccessmodProjectPermissionInput;
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

export type Query = {
  __typename?: 'Query';
  accessmodAnalyses: AccessmodAnalysisPage;
  accessmodAnalysis?: Maybe<AccessmodAnalysis>;
  accessmodFileset?: Maybe<AccessmodFileset>;
  accessmodFilesetRole?: Maybe<AccessmodFilesetRole>;
  accessmodFilesetRoles: Array<AccessmodFilesetRole>;
  accessmodFilesets: AccessmodFilesetPage;
  accessmodProject?: Maybe<AccessmodProject>;
  accessmodProjects: AccessmodProjectPage;
  countries: Array<Country>;
  me: Me;
  organizations: Array<Organization>;
  team?: Maybe<Team>;
  teams: TeamPage;
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
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  teams?: InputMaybe<Array<Scalars['String']>>;
  term?: InputMaybe<Scalars['String']>;
};


export type QueryTeamArgs = {
  id: Scalars['String'];
};


export type QueryTeamsArgs = {
  page?: InputMaybe<Scalars['Int']>;
  perPage?: InputMaybe<Scalars['Int']>;
  term?: InputMaybe<Scalars['String']>;
};

export type ResetPasswordInput = {
  email: Scalars['String'];
};

export type ResetPasswordResult = {
  __typename?: 'ResetPasswordResult';
  success: Scalars['Boolean'];
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
  maxSlope?: InputMaybe<Scalars['Float']>;
  maxTravelTime?: InputMaybe<Scalars['Int']>;
  movingSpeedsId?: InputMaybe<Scalars['String']>;
  name?: InputMaybe<Scalars['String']>;
  priorityLandCover?: InputMaybe<Array<Scalars['Int']>>;
  priorityRoads?: InputMaybe<Scalars['Boolean']>;
  slopeId?: InputMaybe<Scalars['String']>;
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

export enum UpdateAccessmodProjectError {
  NameDuplicate = 'NAME_DUPLICATE',
  NotFound = 'NOT_FOUND',
  PermissionDenied = 'PERMISSION_DENIED'
}

export type UpdateAccessmodProjectInput = {
  country?: InputMaybe<CountryInput>;
  crs?: InputMaybe<Scalars['Int']>;
  description?: InputMaybe<Scalars['String']>;
  extentId?: InputMaybe<Scalars['String']>;
  id: Scalars['String'];
  name?: InputMaybe<Scalars['String']>;
  spatialResolution?: InputMaybe<Scalars['Int']>;
};

export enum UpdateAccessmodProjectPermissionError {
  NotFound = 'NOT_FOUND',
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

export enum UpdateMembershipError {
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
  email: Scalars['String'];
  firstName?: Maybe<Scalars['String']>;
  id: Scalars['String'];
  lastLogin?: Maybe<Scalars['DateTime']>;
  lastName?: Maybe<Scalars['String']>;
};

export type UserAvatar_UserFragment = { __typename?: 'User', firstName?: string | null, lastName?: string | null, avatar: { __typename?: 'Avatar', initials: string, color: string } };

export type MeQueryQueryVariables = Exact<{ [key: string]: never; }>;


export type MeQueryQuery = { __typename?: 'Query', me: { __typename?: 'Me', user?: { __typename?: 'User', email: string, id: string, firstName?: string | null, lastName?: string | null, avatar: { __typename?: 'Avatar', initials: string, color: string } } | null } };

export type LogoutMutationVariables = Exact<{ [key: string]: never; }>;


export type LogoutMutation = { __typename?: 'Mutation', logout: { __typename?: 'LogoutResult', success: boolean } };

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


export type LoginMutation = { __typename?: 'Mutation', login: { __typename?: 'LoginResult', success: boolean } };

export const UserAvatar_UserFragmentDoc = gql`
    fragment UserAvatar_user on User {
  firstName
  lastName
  avatar {
    initials
    color
  }
}
    `;
export const MeQueryDocument = gql`
    query MeQuery {
  me {
    user {
      email
      id
      firstName
      lastName
      avatar {
        initials
        color
      }
    }
  }
}
    `;

/**
 * __useMeQueryQuery__
 *
 * To run a query within a React component, call `useMeQueryQuery` and pass it any options that fit your needs.
 * When your component renders, `useMeQueryQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useMeQueryQuery({
 *   variables: {
 *   },
 * });
 */
export function useMeQueryQuery(baseOptions?: Apollo.QueryHookOptions<MeQueryQuery, MeQueryQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<MeQueryQuery, MeQueryQueryVariables>(MeQueryDocument, options);
      }
export function useMeQueryLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<MeQueryQuery, MeQueryQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<MeQueryQuery, MeQueryQueryVariables>(MeQueryDocument, options);
        }
export type MeQueryQueryHookResult = ReturnType<typeof useMeQueryQuery>;
export type MeQueryLazyQueryHookResult = ReturnType<typeof useMeQueryLazyQuery>;
export type MeQueryQueryResult = Apollo.QueryResult<MeQueryQuery, MeQueryQueryVariables>;
export const LogoutDocument = gql`
    mutation Logout {
  logout {
    success
  }
}
    `;
export type LogoutMutationFn = Apollo.MutationFunction<LogoutMutation, LogoutMutationVariables>;

/**
 * __useLogoutMutation__
 *
 * To run a mutation, you first call `useLogoutMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useLogoutMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [logoutMutation, { data, loading, error }] = useLogoutMutation({
 *   variables: {
 *   },
 * });
 */
export function useLogoutMutation(baseOptions?: Apollo.MutationHookOptions<LogoutMutation, LogoutMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<LogoutMutation, LogoutMutationVariables>(LogoutDocument, options);
      }
export type LogoutMutationHookResult = ReturnType<typeof useLogoutMutation>;
export type LogoutMutationResult = Apollo.MutationResult<LogoutMutation>;
export type LogoutMutationOptions = Apollo.BaseMutationOptions<LogoutMutation, LogoutMutationVariables>;
export const ResetPasswordDocument = gql`
    mutation ResetPassword($input: ResetPasswordInput!) {
  resetPassword(input: $input) {
    success
  }
}
    `;
export type ResetPasswordMutationFn = Apollo.MutationFunction<ResetPasswordMutation, ResetPasswordMutationVariables>;

/**
 * __useResetPasswordMutation__
 *
 * To run a mutation, you first call `useResetPasswordMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useResetPasswordMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [resetPasswordMutation, { data, loading, error }] = useResetPasswordMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useResetPasswordMutation(baseOptions?: Apollo.MutationHookOptions<ResetPasswordMutation, ResetPasswordMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ResetPasswordMutation, ResetPasswordMutationVariables>(ResetPasswordDocument, options);
      }
export type ResetPasswordMutationHookResult = ReturnType<typeof useResetPasswordMutation>;
export type ResetPasswordMutationResult = Apollo.MutationResult<ResetPasswordMutation>;
export type ResetPasswordMutationOptions = Apollo.BaseMutationOptions<ResetPasswordMutation, ResetPasswordMutationVariables>;
export const SetPasswordDocument = gql`
    mutation SetPassword($input: SetPasswordInput!) {
  setPassword(input: $input) {
    success
    error
  }
}
    `;
export type SetPasswordMutationFn = Apollo.MutationFunction<SetPasswordMutation, SetPasswordMutationVariables>;

/**
 * __useSetPasswordMutation__
 *
 * To run a mutation, you first call `useSetPasswordMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetPasswordMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setPasswordMutation, { data, loading, error }] = useSetPasswordMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSetPasswordMutation(baseOptions?: Apollo.MutationHookOptions<SetPasswordMutation, SetPasswordMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<SetPasswordMutation, SetPasswordMutationVariables>(SetPasswordDocument, options);
      }
export type SetPasswordMutationHookResult = ReturnType<typeof useSetPasswordMutation>;
export type SetPasswordMutationResult = Apollo.MutationResult<SetPasswordMutation>;
export type SetPasswordMutationOptions = Apollo.BaseMutationOptions<SetPasswordMutation, SetPasswordMutationVariables>;
export const LoginDocument = gql`
    mutation Login($input: LoginInput!) {
  login(input: $input) {
    success
  }
}
    `;
export type LoginMutationFn = Apollo.MutationFunction<LoginMutation, LoginMutationVariables>;

/**
 * __useLoginMutation__
 *
 * To run a mutation, you first call `useLoginMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useLoginMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [loginMutation, { data, loading, error }] = useLoginMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useLoginMutation(baseOptions?: Apollo.MutationHookOptions<LoginMutation, LoginMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<LoginMutation, LoginMutationVariables>(LoginDocument, options);
      }
export type LoginMutationHookResult = ReturnType<typeof useLoginMutation>;
export type LoginMutationResult = Apollo.MutationResult<LoginMutation>;
export type LoginMutationOptions = Apollo.BaseMutationOptions<LoginMutation, LoginMutationVariables>;