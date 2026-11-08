# vlb20.github.io

Personal website of Vincenzo Luigi Bruno, built with Jekyll and published by GitHub Pages.

## Updating content

Almost everything lives in `_data/`, one YAML file per section:

| File | What it holds |
| --- | --- |
| `news.yml` | News on the home page (newest first) |
| `education.yml` | Degrees: drives the *Path* timeline and the CV |
| `teaching.yml` | One entry per course and semester |
| `service.yml` | Reviewing, talks, supervision. Hidden while empty |
| `publications.yml` | Papers. Hidden while empty |
| `experience.yml`, `awards.yml`, `projects.yml`, `skills.yml` | CV and *Work* section |

The bio is the body of `index.md`. The CV PDF is `files/cv.pdf`.
Optional sections get their number in the menu automatically when they appear.

## Local preview

```sh
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000.

## The isometric map

`tools/iso-map/` holds the Python scripts that draw the map. To regenerate it:

```sh
cd tools/iso-map
python3 build.py      # geometry of the two campuses
python3 make_maps.py  # writes _includes/study-map-*.svg and images/study-map.svg
```

Buildings are boxes in metres (`build.py`); labels and layout are in `make_maps.py`.
