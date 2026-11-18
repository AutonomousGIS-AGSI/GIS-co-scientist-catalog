# GIS Co-Scientist data-source catalog

The shared data sources used by the **GIS Co-Scientist** desktop app. Each source is a
*handbook*: instructions the app's data agent follows to find and download data from
that source.

The app downloads this catalog from the `main` branch every time it opens, so a source
merged here appears under **Data Sources → Shared Sources** for every user at their next
launch. Open pull requests are never downloaded.

## Layout

| Path | What |
|---|---|
| `handbooks/<name>.toml` | one data source: `data_source_name`, `brief_description`, `handbook`, `code_example`, `website`, ... |
| `keys/<name>.keys` | only for sources that need an API key: the key **names** (`[API_Key]`, values always empty) and sign-up links (`[Links]`) |
| `scripts/` | the checks run on every pull request |

No keys or tokens are ever stored here. Each user enters their own keys in the app.

## Proposing a data source

The easy way is from the desktop app:

1. Add the source under **Data Sources → My Sources** and check that it works.
2. Click **Submit** on its card, or turn on **Submit to the shared catalog** when adding it.
3. The first time, sign in to GitHub with the one-time code the app shows. A free GitHub
   account is enough.

The app opens a pull request for you. You can also open one by hand: add
`handbooks/<name>.toml` (and `keys/<name>.keys` if it needs a key) in a fork.

## Reviewing (maintainer)

Every pull request runs **Check catalog**, which blocks:

- invalid TOML, or a handbook missing `data_source_name`, `brief_description` or `handbook`;
- any value under `[API_Key]` in a `.keys` file;
- anything that looks like an API key, token or private key;
- files other than `handbooks/*.toml` and `keys/*.keys` in those folders.

It flags (without blocking) email addresses, local file paths, private network addresses,
removed sources, and changes outside the catalog folders.

The check can't judge whether a source is trustworthy. The data agent writes and runs code
on users' computers by following these handbooks, so before merging, make sure the source
is real and reputable, it uses official endpoints, and its instructions only fetch data.

Run the check locally with `python scripts/validate_catalog.py`.
