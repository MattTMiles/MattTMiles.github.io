# matttmiles.github.io

Personal website of Matthew T. Miles. Plain Jekyll, built by GitHub Pages — no build step or Actions needed.

## Pages

| Page | File | Content from |
|---|---|---|
| Home | `index.html` | `_config.yml` (`author:`), `_data/news.yml`, `_data/papers.yml` |
| Research | `research.html` | text in the file + `_data/papers.yml` sidebar |
| Publications | `publications.html` | `_data/papers.yml` |
| Software | `software.html` | text in the file |
| CV | `cv.html` | text in the file + PDF at `assets/cv/Miles_CV.pdf` |
| Contact | `contact.html` | `_config.yml` |

Search the repo for `TODO` to find everything that still needs your details.

## Editing

- **Profile links** (Scholar, ADS, ORCID, GitHub, …): `_config.yml` → `links:`. Empty = hidden.
- **Headshot**: add `assets/img/matthew-miles-astronomer.jpg` (square, ≥ 400 px) and set `author.headshot` and `image` in `_config.yml`.
- **News**: add an item to the top of `_data/news.yml`.
- **Papers**: `python3 tools/update_papers.py` pulls everything from arXiv. Then fix by hand in `_data/papers.yml`:
  `"role"` = `first` / `significant` / `collaboration`, `"hide": true` to drop a paper. Hand edits survive re-runs.

## Preview locally

```bash
mamba run -n jekyll jekyll serve --livereload
```

Then open http://localhost:4000.

## Deploy

1. Create a **public** repo on GitHub named exactly `MattTMiles.github.io`.
2. `git remote add origin git@github.com:MattTMiles/MattTMiles.github.io.git && git push -u origin main`
3. Repo → Settings → Pages → Source: *Deploy from a branch*, `main`, `/ (root)`.
4. Site appears at https://matttmiles.github.io within a minute or two.

A `username.github.io` address must match the GitHub username, so `mattmiles.github.io` would need a GitHub account called `mattmiles`.
The better option is a custom domain (next section).

### Custom domain (recommended)

A domain with your name in it (e.g. `matthewtmiles.com`, `mattmiles.space`, about $10–15 per year) ranks better for name searches and stays yours if you leave GitHub.
1. Buy the domain. At the registrar, add a `CNAME` record `www` → `matttmiles.github.io`, and `A` records for the apex domain → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
2. Repo → Settings → Pages → Custom domain → enter it, tick *Enforce HTTPS*. GitHub then commits a `CNAME` file.
3. Set `url:` in `_config.yml` to the new domain.

## Getting found on Google

The site already has page titles and descriptions, Open Graph tags, `sitemap.xml`, `robots.txt`, and schema.org `Person` data. That data lists your name variants, job, affiliation, award, and every profile in `links:` as `sameAs`.

1. **Google Search Console** (search.google.com/search-console): add the site and verify it. Use the *HTML tag* method and paste the code into `google_site_verification` in `_config.yml`. Then submit `sitemap.xml` and use *URL inspection → Request indexing* on the home page. This is the single most important step.
2. **Link to the site from everywhere you already rank.** Google trusts these pages, and the links tell it the new site is you:
   - GitHub profile (Website field and profile README)
   - Google Scholar profile (Homepage field)
   - ORCID (Websites)
   - Vanderbilt / VIPER team page and the Swinburne alumni/OzGrav pages, if they can link out
   - LinkedIn, Bluesky/X bio, email signature, conference speaker bios, Live Science / The Conversation author bio
3. **Fill in Scholar and ORCID** in `_config.yml`. They become `sameAs` links, which helps Google build a knowledge panel for you.
4. **Use one name consistently.** Use "Matthew T. Miles" everywhere. The middle initial is what separates you from the other Matt Miles online.
5. **Add a real headshot** with a descriptive filename. Google Images is often where people find you first.
6. **Keep it alive.** Add a news item for each paper or talk. Updated sites get crawled more often.

Expect about 1–4 weeks after Search Console submission before a search for your name shows the site near the top.
