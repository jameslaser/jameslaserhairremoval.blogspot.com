# James Laser Hair Removal for Men: Blog

Nurse James's men's laser hair removal blog: bilingual (English and Arabic) articles, published free on GitHub Pages. This replaces the Blogspot blog at https://jameslaserhairremoval.blogspot.com.

**Live address (after setup):** https://jameslaser.github.io/jameslaserhairremoval.blogspot.com/

Every change you save to the `main` branch republishes the site automatically in about a minute.

---

## 1. Turn on publishing (one time)

1. On GitHub, open this repo → **Settings** → **Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Open the **Actions** tab → **Publish blog** → **Run workflow**.

> GitHub Pages only works on a **private** repo with a paid plan (GitHub Pro, about $4/month).
> On the free plan, make the repo public first: **Settings → General → Danger Zone → Change visibility → Public**.
> The site is public either way. Only the source files would become visible.

## 2. Write a new article (works from your phone)

1. Open the **`src/posts`** folder → **Add file** → **Create new file**.
2. Name it with the date and a short English address, for example:
   `2026-11-20-beard-line-aftercare.md`
3. Paste this template, fill it in, then **Commit changes**:

```markdown
---
title: "Beard Line Aftercare | العناية بعد ليزر خط اللحية"
date: 2026-11-20
description: "One or two sentences for Google and for the article card."
labels:
  - Aftercare
  - Beard Line
image: https://link-to-a-photo.jpg   # optional; shown on the home page card
---

Write the English text here. Leave a blank line between paragraphs.

## A heading

- A bullet point
- **Bold text** like this

<p lang="ar" dir="rtl">اكتب الفقرة العربية هنا.</p>
```

The article appears at `/2026/11/beard-line-aftercare.html`.
To hide an article without deleting it, add `draft: true` under `labels`.
You can also name the file `.html` and paste HTML straight from Blogger's HTML view.

## 3. Bring over the Blogspot articles

1. In Blogger, open **Settings** → **Manage blog** → **Back up content** → **Download**.
2. Send the downloaded `.xml` file to Claude, or run:

```bash
npm run import -- path/to/blog-backup.xml
```

Each published post keeps its title, date, labels, images and exact Blogger address (`/2026/11/post-name.html`). Links between your own posts are switched to point at the new site. Images stay hosted on Google, so they keep working.

## 4. Change clinic details

Phone numbers, hours, address, devices and social links are all in **`src/_data/site.js`**. Edit them there once and every page updates.

The About page text is in `src/about.njk`.

## 5. Use your own domain (optional)

To serve the blog from, say, `blog.jameslaserformen.com`:

1. **Settings → Pages → Custom domain** → enter the domain → Save.
2. At your domain provider, add a **CNAME** record: `blog` → `jameslaser.github.io`.

The links fix themselves on the next publish.

---

### For developers

- Built with [Eleventy 3](https://www.11ty.dev/). Run `npm install`, then `npm start` (preview at http://localhost:8080) or `npm run build` (output to `_site/`).
- `.github/workflows/deploy.yml` builds and deploys to Pages. It sets `PATH_PREFIX` and `SITE_URL` from the Pages configuration.
- Post bodies are never processed as templates, so Blogger HTML containing `{{ }}` is safe.
- Advertising copy should follow Saudi healthcare advertising rules: no "permanent", "painless", "guaranteed" or "number one" claims.
