# Publishing checklist

The site is finished and verified locally. Four steps put it online. Do them in order.
Step 1 is a legal requirement, not a formality.

Repository: `https://github.com/LW7776/Unicorn-Germany`
Live URL once Pages is on: `https://lw7776.github.io/Unicorn-Germany/`

---

## 1. The Impressum. Done, but check it before anything is served

`impressum.html` now carries the operator's real details, and the placeholders and the
publish-blocker banner are gone:

```
Lan Lukas Welge · Berlin, Germany · lanlukas.welge@gmail.com
```

German law (§5 DDG) requires a real name, address and contact on a site like this, and the
exposure for getting it wrong is an Abmahnung. Read the page once and confirm those three
lines are still current before you serve anything.

## 2. Push

No credentials are stored on this machine, so the first push is yours to run:

```bash
git push -u origin build/site
```

If it asks for a password, use a personal access token rather than your account password —
GitHub stopped accepting passwords for git over HTTPS.

## 3. Merge and enable Pages

Open a pull request from `build/site` into `main` and merge it, or push `main` directly
if you prefer. Then:

**Settings → Pages → Source: Deploy from a branch → `main` / `/ (root)`**

No build step runs. The repository *is* the site, which is why `.nojekyll` is there.

Give it a minute, then check `https://lw7776.github.io/Unicorn-Germany/`.

## 4. Let the workflows write

The automated jobs commit and open pull requests on your behalf. GitHub blocks that by
default, and the failure looks like a permissions error deep in a log, so set both of these
before the first Monday.

**Settings → Actions → General → Workflow permissions**

- Select **Read and write permissions**. Without it `watch.yml` and `rebuild.yml` cannot push.
- Tick **Allow GitHub Actions to create and approve pull requests**. Without it
  `weekly-funding.yml` cannot open its pull request.

## 5. Add the Anthropic API key — only needed for the weekly funding block

**Settings → Secrets and variables → Actions → New repository secret**

Name it exactly `ANTHROPIC_API_KEY`.

Until it exists, the weekly funding workflow fails on its first step with a message naming
the secret, and publishes nothing. The three demo weeks stay on the site either way.

## 6. Check it works without waiting a week

Every scheduled job also has a manual trigger. **Actions → pick the workflow → Run workflow.**
Run `weekly-funding` once by hand and confirm a pull request appears. That proves the key,
the permissions and the job all work, rather than discovering it broken on a Monday.

---

## What runs on its own afterwards

| Workflow | When | What it does |
|---|---|---|
| `validate.yml` | every push and pull request | tests, contrast, validation, and refuses a stale `data/companies.json` |
| `weekly-funding.yml` | Mondays | writes the week's funding block and opens a pull request |
| `watch.yml` | every 8 weeks | re-checks the register and opens an issue listing candidates |
| `rebuild.yml` | any hand edit to `data/companies/` | validates first, and only rebuilds if it passes |

Nothing merges itself. Every automated change arrives as a pull request or an issue.

## How an update reaches the live site

```
workflow runs  ->  opens a pull request  ->  you merge it
   ->  main changes  ->  Pages redeploys  ->  live in about a minute
```

That merge is the only manual step, and it is deliberate. It is the point where a person
sees what the automation wrote before the public does.

If you would rather it were hands-off, turn on **Settings → General → Allow auto-merge** and
enable auto-merge on the weekly funding pull request. It then merges itself once
`validate.yml` passes. You gain a site that updates with no involvement, and you give up the
review step. The register sweep should stay manual either way, since it proposes changes to
published company figures.

## Editing by hand

Three routes, all documented in [docs/UPDATING.md](UPDATING.md): the "Edit this entry" link
on any company card, the `admin.html` form, or the files directly. A bad edit committed
straight to `main` fails validation and leaves the published data untouched.
