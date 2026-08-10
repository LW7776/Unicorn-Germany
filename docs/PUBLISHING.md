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

Two of the workflows act on your behalf, and GitHub blocks that by default. The failure looks
like a permissions error deep in a log, so set this before the first Monday.

**Settings → Actions → General → Workflow permissions**

- Select **Read and write permissions**. Without it `rebuild.yml` cannot push the regenerated
  `data/companies.json` after a hand edit.
- `monday-reminder.yml` only needs to open issues, and it asks for exactly that in its own
  `permissions:` block. It commits nothing and opens no pull request, so it needs neither the
  pull-request tick nor write access to contents.

## 5. Turn on the email, which is the whole notification path

The Monday reminder opens an issue. GitHub emails that issue to everyone **watching** the
repository, and that is the entire delivery mechanism: no mail server, no address in any config
file, nothing to pay for.

On the repository page, open **Watch** and choose **All Activity**, or **Custom** with **Issues**
ticked. On "Participating and @mentions" no mail arrives, and the reminder becomes something you
have to remember to look for. Owning the repository does not subscribe you by itself.

## 5b. No API key, and nothing looks for one

There is no `ANTHROPIC_API_KEY` in this repository and no workflow that would read one. CI does
not write the site: it scans the feeds and, when there is something to report, opens an issue.
The week is then written locally by a person with an assistant and pushed, which is what keeps
every published week at the quality of the ones already there.

Adding a secret would therefore change nothing on its own. What it *would* make possible, if you
ever wanted it, is written up in
[docs/UPDATING.md](UPDATING.md#if-an-api-key-were-ever-added), along with why that trade was
turned down.

## 6. Check the reminder works without waiting for Monday

Every scheduled job also has a manual trigger. **Actions → monday-reminder → Run workflow**, with
**register sweep** ticked to see both sections at once. It opens an issue if the week has
anything in it, which proves the permission and the email in one run rather than discovering they
are wrong in two months. A run that reports nothing opens nothing, by design.

---

## What runs on its own afterwards

| Workflow | When | What it does |
|---|---|---|
| `validate.yml` | every push and pull request | tests, contrast, validation, and refuses a stale `data/companies.json` |
| `monday-reminder.yml` | 20:00 Berlin time every Monday, plus on request | scans the feeds and opens **one issue** if there is anything to report. Every eighth week that issue also carries the register sweep. It publishes nothing |
| `rebuild.yml` | any hand edit to `data/companies/` | validates first, and only rebuilds if it passes |

No workflow writes site content. Nothing merges itself. The reminder can also be started from
outside GitHub with an HTTP POST to the `workflow_dispatch` endpoint, with the `curl` and the
token scope written out in
[docs/UPDATING.md](UPDATING.md#starting-a-run-yourself) — and that route publishes nothing either.

## How an update reaches the live site

```
Monday scan  ->  opens an issue  ->  you and an assistant write the week
   ->  you push  ->  main changes  ->  Pages redeploys  ->  live in about a minute
```

Every step after the scan is a person. That is the design, not a gap in it: a scheduled job with
no model behind it could only ever publish a list of parsed headlines, and a register that gets
slightly worse every Monday is worse than one that waits for someone to write it.

## Editing by hand

Three routes, all documented in [docs/UPDATING.md](UPDATING.md): the "Edit this entry" link
on any company card, the `admin.html` form, or the files directly. A bad edit committed
straight to `main` fails validation and leaves the published data untouched.
