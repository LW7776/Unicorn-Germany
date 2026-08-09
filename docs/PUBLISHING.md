# Publishing checklist

The site is finished and verified locally. Four steps put it online. Do them in order —
step 1 is a legal requirement, not a formality.

Repository: `https://github.com/LW7776/Unicorn-Germany`
Live URL once Pages is on: `https://lw7776.github.io/Unicorn-Germany/`

---

## 1. Fill in the Impressum — before anything is served

`impressum.html` carries five placeholders and a visible warning banner:

```
[OPERATOR NAME]  [STREET AND NUMBER]  [POSTCODE AND CITY]  [CONTACT EMAIL]
```

German law (§5 DDG) requires a real name, postal address and contact on a site like this,
and the exposure for getting it wrong is an Abmahnung. Nobody but you can supply these,
which is why they were never guessed.

Replace all five, then delete the warning banner (the block marked
`<!-- PUBLISH BLOCKER -->`).

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

## 4. Add the Anthropic API key — only needed for the weekly funding block

**Settings → Secrets and variables → Actions → New repository secret**

Name it exactly `ANTHROPIC_API_KEY`.

Until it exists, the weekly funding workflow fails on its first step with a message naming
the secret, and publishes nothing. The three demo weeks stay on the site either way.

---

## What runs on its own afterwards

| Workflow | When | What it does |
|---|---|---|
| `validate.yml` | every push and pull request | tests, contrast, validation, and refuses a stale `data/companies.json` |
| `weekly-funding.yml` | Mondays | writes the week's funding block and opens a pull request |
| `watch.yml` | every 8 weeks | re-checks the register and opens an issue listing candidates |
| `rebuild.yml` | any hand edit to `data/companies/` | validates first, and only rebuilds if it passes |

Nothing merges itself. Every automated change arrives as a pull request or an issue.

## Editing by hand

Three routes, all documented in [docs/UPDATING.md](UPDATING.md): the "Edit this entry" link
on any company card, the `admin.html` form, or the files directly. A bad edit committed
straight to `main` fails validation and leaves the published data untouched.
