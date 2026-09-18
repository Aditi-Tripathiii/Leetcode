# LeetCode → GitHub auto-sync setup

## What this does
Every 15 minutes, GitHub's own servers (not your machine) check your recent
LeetCode submissions. Any newly Accepted one gets written to:
- `quest/<problem-slug>/README.md` — problem statement + difficulty + link
- `sol/<problem-slug>/solution.<ext>` — your code

...and committed/pushed automatically. You never run `git push` yourself.

## 1. Copy these files into your existing leetcode repo
Drop `.github/`, `scripts/`, and `data/` into the root of your repo, exactly
as they are here. Commit and push this once, manually, to get the workflow
installed.

## 2. Get your LeetCode session cookie (Firefox)
1. Log into leetcode.com in Firefox.
2. Press F12 to open DevTools → go to the **Storage** tab → **Cookies** →
   `https://leetcode.com`.
3. Find the cookie named `LEETCODE_SESSION` — copy its **Value**.
4. Find the cookie named `csrftoken` — copy its **Value** too.

## 3. Add repo secrets
In your leetcode repo on GitHub: **Settings → Secrets and variables →
Actions → New repository secret**. Add three:
- `LEETCODE_SESSION` = the value from step 2
- `LEETCODE_CSRF_TOKEN` = the csrftoken value from step 2
- `LEETCODE_USERNAME` = your leetcode username (not strictly required by the
  script, kept for future use / debugging)

## 4. Turn it on
Go to the **Actions** tab of the repo → you should see "Sync LeetCode
Submissions" → click **Run workflow** once to test it manually. After that
it runs on its own every 15 minutes.

## When it will break
- If you log out of LeetCode everywhere, or the session naturally expires
  (can take weeks/months), the script will start failing. Just repeat step 2
  and update the `LEETCODE_SESSION` secret.
- Check the **Actions** tab occasionally — a red X means it needs a fresh
  cookie.
