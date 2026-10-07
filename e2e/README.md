# End-to-end regression suite

Playwright tests that run against a **deployed** OpenHEXA environment (the demo
environment by default). They are a pre-deployment smoke check: run them against
demo before promoting a release to production and they will catch navigation,
rendering and permission regressions that unit tests cannot.

These tests do not start a server. They sign in as a real account and drive a
real environment, so they are kept as close to read-only as the coverage allows:
they read pages, and open forms and cancel out of them. Where a test has to write
-- creating a workspace, say -- it names the resource uniquely and removes it
again, including when the test fails partway through.

## Setup

```bash
cd e2e
npm install          # also downloads the Chromium build Playwright needs
cp .env.example .env # then fill in E2E_EMAIL / E2E_PASSWORD
```

The account in `.env` must be an admin or owner of the organization under test —
the settings page renders nothing without the `update` permission. It must also
be a member (editor or admin) of the test workspace itself: the organization
role reaches the workspace's pages, but the AI assistant only serves members.

`E2E_OUTSIDER_EMAIL` / `E2E_OUTSIDER_PASSWORD` are optional: a second account
that is signed in but has no access to the test workspace -- not a member of
it, and not an admin or owner of its organization, which would reach every
workspace in it. The tests that check what such a user is refused are skipped
without it. The suite also switches this account's interface language, so that
the main account's never changes under the tests running alongside.

## Running

```bash
npm test                 # headless, all tests

npx playwright test tests/organization-settings.spec.ts
npx playwright test -g "Usage & Limits"
```

From the repository root the Makefile wraps the two common cases, with `ARGS`
passed through to Playwright:

```bash
make te2e                                    # headless
make te2ev                                   # visible browser, slowed down
make te2e ARGS='-g "Usage & Limits"'
make re2e                                    # open the last run's report
```

### Watching it run

| Command | What you get |
| --- | --- |
| `npm run test:ui` | Playwright's UI mode: pick tests, watch them run, step through a timeline with a DOM snapshot per action. The best option for writing or diagnosing a test. |
| `npm run test:watch` | Headed Chromium, one worker, 500ms between actions — a run you can follow in real time. |
| `npm run test:headed` | Headed Chromium at full speed and in parallel. Fast, but hard to follow. |
| `npm run test:debug` | Headed, plus the Playwright Inspector: pauses before each action so you can step and try selectors live. |

These all take the usual filters, so you can point them at a single test:

```bash
npm run test:watch -- -g "Edit opens the General form"
npm run test:ui -- tests/organization-settings.spec.ts
```

Tune the pacing with `E2E_SLOW_MO` (milliseconds per action, `0` to disable):

```bash
E2E_SLOW_MO=1500 npx playwright test --headed --workers=1
```

Headed and UI mode need a display. On a headless box run them under
`xvfb-run`, or stick to the report and traces below.

### After the fact

```bash
make re2e                # HTML report of the last run (npm run report)
npx playwright show-trace test-results/<test-dir>/trace.zip
```

Failures record a screenshot and a video automatically, and a retried failure
records a trace — a step-by-step recording with a DOM snapshot, the network log
and the console at each action. CI uploads all of it as the
`playwright-report` artifact.

To point at another environment, override `E2E_BASE_URL` and the organization
variables:

```bash
E2E_BASE_URL=https://app.openhexa.org E2E_ORGANIZATION_ID=... npm test
```

## Layout

| Path | Contents |
| --- | --- |
| `config/environment.ts` | Environment variables, defaults, and the organization/workspace URLs |
| `fixtures/auth.setup.ts` | Signs in once per run and saves the session to `.auth/user.json` |
| `fixtures/cleanup.ts` | Registers undo steps that run in reverse at teardown, pass or fail |
| `fixtures/disposableWorkspace.ts` | A uniquely named workspace, archived again in teardown |
| `fixtures/visitors.ts` | Pages for an anonymous visitor and for the outsider account |
| `helpers/` | Native-confirm handling, unique names, grid-load waiting |
| `pages/` | Page objects — the only place selectors live |
| `tests/` | Specs |

Every project depends on the `setup` project, so the suite logs in once and
shares the session through `storageState`. Bad credentials or a revoked
membership fail in `auth.setup.ts` with a clear message rather than as a wall of
unrelated failures.

## Conventions

- **Selectors live in page objects.** A spec that needs a new element gets a new
  getter, not an inline CSS selector.
- **Prefer roles and user-visible text** (`getByRole`, `getByPlaceholder`) over
  class names. The app's Tailwind classes change often; its accessible structure
  does not. `data-testid` is used where the app already provides one.
- **Assert on what a user would notice**: the URL, the page title, the headings,
  and the values in the cards.
- **Leave nothing behind.** The environment is shared. Prefer opening a form and
  cancelling to clicking Save. A test that must create something takes a
  fixture that gives it a uniquely named resource and removes it in teardown, so
  a failed run cleans up too -- see `fixtures/disposableWorkspace.ts`.
- **Decide from a resource, not from a list.** The data grids render their empty
  state while loading, so counting rows to check whether something exists races
  the fetch. Ask for the thing itself: an archived workspace's URL returns 404.

## Adding coverage

Covered so far:

| Spec | What it exercises |
| --- | --- |
| `authentication.spec.ts` | A wrong password refused; a protected page sending a visitor to sign in and back; signing out; requesting a password reset; the sign-up page, and registration needing an invitation |
| `organization-navigation.spec.ts` | The sidebar and every organization route |
| `organization-workspaces.spec.ts` | The organization's workspaces as cards and as a table, searched; tagging a workspace |
| `organization-settings.spec.ts` | The General, AI Assistant and Usage & Limits cards |
| `organization-members.spec.ts` | The members list; inviting an address, resending the invitation and deleting it |
| `user-menu.spec.ts` | The user menu's links (Account settings, MCP, Documentation); the profile name, access tokens and two-factor dialog |
| `outsider.spec.ts` | Everything seen through the outsider account: being added to a workspace and listed as an external collaborator; the interface language; what a workspace Viewer, Editor and Admin are offered; the organization changing a collaborator's roles, converting them to a member, and removing them |
| `workspace-navigation.spec.ts` | The workspace home page; every sidebar section; the global search finding a table and a new pipeline; the retired /pipelines and /notebooks pages leading to the workspaces |
| `workspace-lifecycle.spec.ts` | Creating a workspace and archiving it again |
| `workspace-settings.spec.ts` | In a temporary workspace: its name, countries and configuration, regenerating its database passwords, and a pipeline run that reads the configuration and writes to the database |
| `workspace-files.spec.ts` | Creating a folder, uploading a file, deleting both; browsing into a folder, searching it, downloading and the breadcrumb back; uploading a whole folder; an accented file name and a 5 MB file round-tripping |
| `workspace-datasets.spec.ts` | Creating a dataset and a version, removing both; a file's preview, column profile and download, and picking an earlier version; renaming a dataset and sharing it with the organization (as the organization's dataset list shows); sharing it with another workspace, which reads it, then revoking that |
| `workspace-connections.spec.ts` | Creating and deleting one connection of each type; testing a PostgreSQL connection to the workspace's own database (failing, then passing), keeping its password hidden, and a pipeline run querying it through a connection parameter |
| `workspace-pipelines.spec.ts` | A pipeline from a template: every tab, running it, editing the code, and running the new version |
| `workspace-webapps.spec.ts` | Creating an iFrame app and deleting it; its play page framing its URL, and a changed URL |
| `workspace-pipeline-settings.spec.ts` | A pipeline's name, description, tags and type; its schedule and notification recipients; its webhook starting a run; default parameter values; the Runs tab; editing, downloading and deleting versions |
| `workspace-pipeline-sources.spec.ts` | A pipeline created from a notebook in the workspace's files, and run; a multi-task pipeline's task graph |
| `workspace-templates.spec.ts` | Publishing a pipeline as a template, its pages, building a pipeline from it through the catalogue, upgrading that pipeline to a new template version, and deleting the template |
| `workspace-pipeline-runs.spec.ts` | A run with typed parameters, its file and database table outputs, its messages arriving while it runs, and stopping it |
| `workspace-pipeline-assistant.spec.ts` | Creating a pipeline with AI and landing in its editor with the conversation; on a pipeline's code, a proposal that cannot be resolved while the agent is still writing, then dismissed or published as a new version; separate conversations, named and switched between from the history |
| `workspace-webapp-assistant.spec.ts` | The AI assistant on a static app's code: a proposal that cannot be resolved while the agent is still writing, then dismissed or saved; a second request adding to a pending proposal; a proposal deleting a file |
| `workspace-static-webapps.spec.ts` | A static app's code, history, rollback, name, subdomain, icon and deletion; who can open it when private or public, and its API access |
| `workspace-database.spec.ts` | The database's table list and a table's rows; a table written by a pipeline run, then deleted |
| `workspace-notebooks.spec.ts` | JupyterHub starting the user's server and framing JupyterLab |
| `workspace-data-studio.spec.ts` | Running a query into a table, a failing query, and the bar, line, pie and map widgets; the assistant writing a query from a description |
| `workspace-saved-queries.spec.ts` | Creating, listing, opening and deleting a saved query; editing its name, description, SQL and sharing |

The workspace specs run against a dedicated, otherwise-empty workspace
(`E2E_WORKSPACE_SLUG`, default `playwright-ws`) and are expected to leave it
empty.

The Data Studio specs also read the tables loaded into that workspace's database
(Senegal's `level_2_region` and `level_3_department`, and `bikes_history`) and
assert on their values, so reloading that data means updating the expectations.

### Things worth knowing before adding a test

- **Some destructive actions use `window.confirm`.** Playwright dismisses native
  dialogs unless something handles them, which silently cancels the action. Arm
  `acceptNextConfirm(page)` from `helpers/confirm.ts` before the click.
- **Not every control has an accessible name.** A few fields -- the web app
  create form, GCS's service account key -- are rendered without a label the
  browser associates with them, so they are reached through their `<dt>` term or
  a `name` attribute. Prefer a role wherever the app provides one.
- **Upload dialogs hold two file inputs**, one of them a directory picker.
  Target `input[type="file"]:not([webkitdirectory])` for files, and the
  `[webkitdirectory]` one, given a local directory, for folders.
- **The files search runs on Enter and covers the folder on screen only**, not
  the folders below it.
- **A file has no preview page**; clicking its name does nothing.
- **Pipelines created from a template take the template's name**, so that spec
  runs `serial` -- two of its tests at once would collide over the same code.
- **A published template is offered to every user of the platform** until it
  is deleted, which the templates spec does at its end and in cleanup. While
  it exists it may also be the first entry in the catalogue, which is what
  `workspace-pipelines.spec.ts` builds from; that spec copes with any template.
- **A template's own run may legitimately fail.** Most templates call a real
  external service, so the first run is only asserted to reach a verdict. The
  run that has to succeed is the one after the code is replaced with a pipeline
  that just logs a marker; a pipeline version's decorator does not have to match
  the pipeline it is uploaded to, so that source is the same whichever template
  the catalogue lists first.
- **Run specs use their own pipeline**, `RUN_PIPELINE_SOURCE`, created through
  the API with a unique name. It logs its parameters back, can hold for a
  while logging every five seconds (to watch a live run, and to stop one), and
  can write a CSV and a database table under a given name -- which cleanup then
  removes from the files and the database.
- **Filling CodeMirror replaces the whole file**, which is what the edit relies
  on. Save only appears once there are pending changes and goes once they are
  committed, so its disappearance is the signal that a version was published.
- **Data Studio's map is a canvas.** Its features cannot be inspected, so the
  test clicks the middle of the map -- which MapLibre frames on the result --
  and reads the popup. A popup is also the only proof the shapes were drawn:
  MapLibre's worker fails silently and leaves a bare basemap.
- **`browser.newContext()` is still signed in.** Inside a test it inherits the
  project's `use` options, storage state included. A visitor's context needs
  an explicitly empty one -- see `fixtures/visitors.ts`.
- **A static web app is served on its own subdomain**, and a private one
  sends the browser through the backend's `auth-token` view to get there: to
  the login page when nobody is signed in, to a bare "Forbidden" for a user
  without access. Its address is read off the General tab rather than built,
  since the web app domain differs per environment.
- **Saving a static app's code publishes it.** Each save is a commit that goes
  live at once; publishing an older commit from the Code tab rolls it back.
- **The assistant specs talk to the real agent**, so they spend tokens on
  every run and take as long as the model does. A proposal can only be saved
  or dismissed once the agent's turn has ended; the prompt asks for a long
  answer after the proposal, so the turn stays open long enough to check that
  both are refused until then.
- **A pipeline created with AI is cleaned up by its requested name.** Its code
  is its name slugified, so the prompt asks for an exact lowercase, hyphenated
  name and cleanup is registered under it before the agent runs. While the agent
  works, the dialog holds the page with a `beforeunload` prompt, which cleanup
  accepts. The editing specs skip the agent for setup and create their pipeline
  with a known `pipeline.py` through the API.
- **The interface language belongs to the account, not the browser.**
  Switching it changes every session of that user at once, which is why the
  language test runs as the outsider and resets the language through the API
  in cleanup.
- **Every test that uses the outsider lives in `outsider.spec.ts`**, which runs
  its tests one after the other. They share one account: the language test
  changes how it reads, and the others change what it belongs to -- removing
  an external collaborator, or an organization member, deletes every workspace
  membership they hold in the organization. A test that makes the outsider an
  organization member removes them again in cleanup.
- **Adding an existing user to a workspace makes them a member at once** --
  there is no invitation to accept. Pending invitations only exist for emails
  without an account, so the account page's invitation list is not covered.
- **A workspace creation can outlive its test.** Under load the redirect to a
  new workspace can take longer than the test waits, while the backend still
  creates it. `DisposableWorkspace` then looks it up by its unique name in
  teardown and archives it.
- **A saved query is deleted from the list only**, and the list is searched by
  name, so cleanup reads the current name off the query's page first in case
  the test renamed it before failing.
- **Saving a query needs the git server**: each saved query gets a repository,
  and creating one fails ("the query history is unavailable") when it is down.

## CI

`.github/workflows/e2e.yml` runs the suite on demand (`workflow_dispatch`) and
nightly. It needs two repository secrets, plus two optional ones:

| Secret | Value |
| --- | --- |
| `E2E_EMAIL` | The test account's email |
| `E2E_PASSWORD` | Its password |
| `E2E_OUTSIDER_EMAIL` | Optional: an account without access to the test workspace |
| `E2E_OUTSIDER_PASSWORD` | Its password |

The HTML report and any failure traces are uploaded as a build artifact.
