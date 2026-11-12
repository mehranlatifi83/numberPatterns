# Number Patterns (الگوی اعداد)

An NVDA add-on that reads long numbers in groups you define.

افزونه‌ای برای NVDA که اعداد طولانی را با الگویی که خودتان تعریف می‌کنید می‌خواند.

## English

- Define patterns as group sizes separated by dashes, e.g. `4-3-4` or `4-2-2-3`.
  A number whose digit count equals the sum of a pattern's groups is read with that pattern.
  For example, with `4-3-4`, `09123456789` is read as `0912 345 6789`.
- Optionally read all other numbers in fixed groups, e.g. every 3 or 4 digits.
- Decimal numbers (`3.14`) and numbers with separators (`1,234`) are left alone.
- Persian/Arabic-Indic digits are supported.

Settings: NVDA menu → Preferences → Settings → Number Patterns:

- Read numbers using patterns
- Patterns, one per line
- For other numbers, read in groups of (0 = off)
- Only group numbers with at least this many digits
- Pause between groups

A command to toggle the add-on is available, unassigned, under Input gestures → Number Patterns.

Requires NVDA 2024.2 or later.

## فارسی

- الگو را با اندازه‌ی گروه‌ها و خط تیره بنویسید، مثلاً `4-3-4` یا `4-2-2-3`.
  هر عددی که تعداد رقم‌هایش با جمع گروه‌های یک الگو برابر باشد، با همان الگو خوانده می‌شود.
- بقیه‌ی اعداد را هم می‌توان چندتا چندتا خواند، مثلاً سه‌تا سه‌تا.
- اعداد اعشاری و اعداد جداشده با ویرگول تغییر نمی‌کنند.
- ارقام فارسی پشتیبانی می‌شوند.

تنظیمات: منوی NVDA ← تنظیمات ← تنظیمات ← الگوی اعداد.
دستور روشن و خاموش کردن افزونه در «حرکات ورودی» ← «الگوی اعداد» است و کلیدی برایش تعیین نشده.

## Build

```
python build.py
```

## License

GNU General Public License version 2.
