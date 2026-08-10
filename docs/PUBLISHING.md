# Publishing checklist

The site is live at the URL below. This records how it got there and what to do next.
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

## 5. The Anthropic API key — optional, and the schedule runs without it

No key is held, and the Monday schedule is **on** regardless. Those two facts used to be in
conflict, which is why the schedule was previously switched off. They no longer are:
`weekly-funding.yml` picks its mode from what the repository actually has.

- **No `ANTHROPIC_API_KEY`** (the current state): the job makes no model call at all. It fetches
  the week's German rounds from the same allowlisted feeds and opens a pull request publishing
  them as a list, each round carrying company, amount, currency, source link and publication
  date read out of the headline that states it. Nothing is invented and nothing is written in
  prose. The page marks the week as listed rather than written up.
- **With the key**: the same job additionally asks Claude to pick the lead round or two and write
  them up in the site's voice, with every claim checked back against the fetched article text.

So the key buys prose, not coverage. Nothing breaks without it, no run turns red for want of it,
and adding or removing it later needs no code change.

### If you do add one

**Settings → Secrets and variables → Actions → New repository secret**

Name it exactly `ANTHROPIC_API_KEY`. Full steps and what each mode may and may not do are in
[docs/UPDATING.md](UPDATING.md#the-weekly-round-up-in-two-modes).

## 5b. Optional: let the funding pull request merge itself

**Settings → Secrets and variables → Actions → Variables → New repository variable**, named
`FUNDING_AUTO_MERGE`, value `true`.

Unset — the default — the weekly pull request waits for a person, which is what the site's About
page promises. Set to `true`, the workflow enables auto-merge and the week lands on its own once
`validate.yml` passes. That also needs **Settings → General → Allow auto-merge**; without it the
pull request simply stays open, which is the safe failure. Note what you are trading: validation
proves a week is well-formed, sourced, linked and dated, and cannot prove that a company name was
read correctly out of a headline. The register sweep should stay manual either way, since it
proposes changes to published company figures.

## 6. Check the sweep works without waiting eight weeks

Every scheduled job also has a manual trigger. **Actions → pick the workflow → Run workflow.**
Run `watch` once by hand and confirm it opens an issue listing candidates. That needs no API
key and proves the permissions are right, rather than discovering they are not in two months.

---

## What runs on its own afterwards

| Workflow | When | What it does |
|---|---|---|
| `validate.yml` | every push and pull request | tests, contrast, validation, and refuses a stale `data/companies.json` |
| `weekly-funding.yml` | every Monday 07:00 UTC, plus on request, by API, and by webhook | drafts or lists a funding week and opens a pull request |
| `watch.yml` | every 8 weeks | re-checks the register and opens an issue listing candidates |
| `rebuild.yml` | any hand edit to `data/companies/` | validates first, and only rebuilds if it passes |

Every automated change arrives as a pull request or an issue, and nothing merges itself unless
`FUNDING_AUTO_MERGE` is set to `true` (section 5b). The weekly round-up can also be started from
outside GitHub — an HTTP POST to the `workflow_dispatch` or `repository_dispatch` endpoint, with
the `curl` and the token scope written out in
[docs/UPDATING.md](UPDATING.md#starting-a-run-yourself-three-ways). Neither route publishes: both
end at an open pull request.

## How an update reaches the live site

```
workflow runs  ->  opens a pull request  ->  you merge it
   ->  main changes  ->  Pages redeploys  ->  live in about a minute
```

That merge is the only manual step, and it is deliberate. It is the point where a person
sees what the automation wrote before the public does.

If you would rather it were hands-off, section 5b turns that step over to the machine:
`FUNDING_AUTO_MERGE=true` plus **Settings → General → Allow auto-merge**. You gain a site that
updates with no involvement, and you give up the review step.

## Editing by hand

Three routes, all documented in [docs/UPDATING.md](UPDATING.md): the "Edit this entry" link
on any company card, the `admin.html` form, or the files directly. A bad edit committed
straight to `main` fails validation and leaves the published data untouched.
