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
the settings page renders nothing without the `update` permission.

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
npm run report           # HTML report of the last run
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
| `config/environment.ts` | Environment variables, defaults, and the organization URLs |
| `fixtures/auth.setup.ts` | Signs in once per run and saves the session to `.auth/user.json` |
| `fixtures/disposableWorkspace.ts` | A uniquely named workspace, archived again in teardown |
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
| `organization-navigation.spec.ts` | The sidebar and every organization route |
| `organization-settings.spec.ts` | The General, AI Assistant and Usage & Limits cards |
| `workspace-lifecycle.spec.ts` | Creating a workspace and archiving it again |

Pipelines, datasets and the workspace interior are not covered yet; follow the
same page-object shape when adding them.

## CI

`.github/workflows/e2e.yml` runs the suite on demand (`workflow_dispatch`) and
nightly. It needs two repository secrets:

| Secret | Value |
| --- | --- |
| `E2E_EMAIL` | The test account's email |
| `E2E_PASSWORD` | Its password |

The HTML report and any failure traces are uploaded as a build artifact.
