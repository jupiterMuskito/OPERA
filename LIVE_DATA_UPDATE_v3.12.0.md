# OPERA-X v3.12.0 live-data update

## Exact requirement for `~/opera_data`

**No manual update is required. Do not replace `~/opera_data` with the full package's seeded `data/` tree.**

The code-only update contains no live data, risk registers or reference-source files.

## Automatic one-time Lesson Bank schema update

The application will update one file automatically when each business unit's lessons are first loaded after deployment:

`~/opera_data/business_units/<business-unit>/lessons.csv`

If the file does not already have `category`, OPERA-X atomically rewrites it with the new column and preserves every existing row:

- rows with a non-empty equipment value default to `Equipment`;
- rows with no equipment default to `General`.

No row, attachment path, event link, timestamp, read count or user value is removed. If the column already exists, it is retained; blank category cells are filled by the same rule.

The existing `equipment_validation.json` file is not changed during deployment. If an administrator later saves Validation Lists, OPERA-X stores the controlled `lesson_categories` list in that existing JSON file.

No other file under `~/opera_data` is changed by the v3.12.0 upgrade itself.

## Deployment

```bash
cd ~/OPERA
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt
~/OPERA/start_opera.sh
```

Confirm `cat VERSION` and `python -c "import opera; print(opera.__version__)"` both show `3.12.0`. Then open the direct and nginx URLs as applicable and hard-refresh with **Ctrl+F5** in both Chrome and Edge.
