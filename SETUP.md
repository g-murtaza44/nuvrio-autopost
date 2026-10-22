# Auto Post: Setup Guide

This posts one ready-made business/money post to Instagram (and your Facebook Page) every day at 6 PM Pakistan time. Fully free. No news, no live data, nothing pulled from the internet, so nothing can be wrong, outdated or archived.

**How it works:** all content lives in `content/posts.json`. You read it once, it is fixed. Every day GitHub turns the next post into an image and publishes it. That's it.

One-time setup: about 1 to 2 hours. After that, nothing to do.

---

## Step 1: Instagram and Facebook Page

1. In the Instagram app: Settings > Account type and tools > **Switch to professional account** (choose Business or Creator).
2. Create a **Facebook Page** for your brand (free).
3. Link them: in the Facebook Page settings, go to **Linked accounts > Instagram** and connect your Instagram account.

## Step 2: Put the package on GitHub (free)

1. Make a free account at github.com.
2. Click **New repository**. Name it anything, e.g. `autopost`. Set it to **Public** (needed so Instagram can fetch the images; your passwords stay hidden in Step 5).
3. Click **uploading an existing file** and drag in everything from this package **except** the `preview` folder.
4. The `.github` folder is sometimes hidden on computers and may not upload. To be safe: click **Add file > Create new file**, type the name `.github/workflows/autopost.yml`, paste the contents of that file from this package, and click **Commit**.

## Step 3: Put your page name in

Open `config.json` on GitHub, click the pencil icon, and change:
- `"page_name"` to your page name
- `"handle"` to your Instagram handle

Click **Commit changes**.

## Step 4: Get your Meta keys (free)

1. Go to **developers.facebook.com**, log in with the Facebook account that manages your Page, and click **My Apps > Create App**. Pick the option for managing Pages / business. Give it any name.
2. Open **Tools > Graph API Explorer**.
3. On the right: pick your app, then click **Generate Access Token** (User Token) and tick these permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
   - `business_management`
4. Copy the token. Open **Tools > Access Token Debugger**, paste it, click **Debug**, then click **Extend Access Token** at the bottom. Copy the new long token.
5. Back in Graph API Explorer, paste the long token in the token box. In the query box type `me/accounts` and press **Submit**.
   - Find your page. Copy its `id` (this is your **FB_PAGE_ID**) and its `access_token` (this is your **PAGE_ACCESS_TOKEN**).
6. In the query box type `YOUR_PAGE_ID?fields=instagram_business_account` (put your page id in) and press **Submit**.
   - Copy the `id` inside `instagram_business_account`. This is your **IG_USER_ID**.
7. Optional check: paste the PAGE_ACCESS_TOKEN into the Access Token Debugger. It should say **Expires: Never**.

Your app can stay in development mode. Since it only posts to your own account, no approval from Meta is needed.

## Step 5: Save the keys in GitHub (hidden, safe)

In your GitHub repository: **Settings > Secrets and variables > Actions > New repository secret**. Add three:

| Name | Value |
|---|---|
| `IG_USER_ID` | from step 4.6 |
| `PAGE_ACCESS_TOKEN` | from step 4.5 |
| `FB_PAGE_ID` | from step 4.5 |

Nobody can see these, even though the repository is public.

## Step 6: Click the button

1. Open the **Actions** tab. If asked, click to enable workflows.
2. Click **Auto Post** on the left, then **Run workflow > Run workflow**.
3. Wait about a minute. Green tick = posted. Check your Instagram.

From now on it posts by itself every day at 6 PM. You never have to touch it.

---

## Everyday things

**See all posts before they go live:** open the `preview` folder in this package. All 30 are already made.

**Add more posts:** open `content/posts.json` and add more blocks in the same format. Or ask Claude to write the next 30 for you.

**Change posting time:** in `.github/workflows/autopost.yml`, change `"0 13 * * *"`. The time is UTC, so subtract 5 hours from Pakistan time. Example, 9 PM PKT = 16:00 UTC = `"0 16 * * *"`.

**Change colors:** edit the `colors` section in `config.json`.

**Turn off Facebook posting:** set `"post_to_facebook_page_too": false` in `config.json`.

**When all 30 posts are used:** it stops posting and waits for new content. Set `"when_all_posts_used": "repeat"` to loop them instead.

**A run shows a red cross:** click it and open the **Publish** step. The message tells you what Meta said. Most common causes: a secret was pasted wrong, or Instagram is not linked to the Page.

**Meta asks you to upgrade API version (every year or two):** change `"graph_api_version"` in `config.json` to the newest version listed at developers.facebook.com/docs/graph-api/changelog.
