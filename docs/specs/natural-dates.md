There are a lot of cases where we need to deal with natural dates in task management and this is the PRD for essentially having the adapter layer converts natural dates to a standard date and vice versa.

## Dates

There are three layers of date representation, organized by fidelity and use-case:

1. **Strict Datetimes**  
   Timezone-aware `datetime.datetime` objects used in core logic, CRUD interfaces, and storage.

2. **Debug Datetimes**  
   Developer-centric compact format (`yyyymmddhhmm`) used for:
   - Round-trip testing
   - Serialization and internal interchange
   - Intermediate normalization layer
   - Truncated variants for convenience:
     - `yyyymmddhhmm`
     - `yyyymmdd` → midnight assumed
     - `hhmm` → today's date assumed
     - `hh` → hour today, `00` minutes assumed

3. **Natural Datetimes**  
   Human-facing expressions like:
   - `"tomorrow 6pm"`, `"next Monday"`, `"this Friday"`, `"tonight"`, `"in 2 hours"`, etc.
   Internally parsed via a reference `now` to map onto a debug format.

## The `DT` Class

A unified interface to consume any string and expose all three formats.

```python
from td.utils.dates import DT

dt = DT("tomorrow evening")  # internally uses datetime.now()

dt.as_debug()     # -> '202505141900'  (canonical 24hr debug format)
dt.as_strict()    # -> datetime.datetime(2025, 5, 14, 19, 0)
dt.as_strict(format='iso')  # -> '2025-05-14T19:00:00+05:30'
dt.as_natural()   # -> 'tomorrow evening'
dt.as_natural_verbose()   # -> 'tomorrow evening, 6pm'

dt.d  # shorthand for dt.as_debug()
dt.s  # shorthand for dt.as_strict()
dt.n  # shorthand for dt.as_natural()
dt.nv # shorthand for dt.as_natural_verbose()
```

## Behavior

- The class is **immutable**. Transformations return new instances:
  ```python
  dt2 = dt.shift(days=1).with_time("10pm")
  ```
- Natural phrases like "morning", "afternoon", and "evening" are mapped by default to:
  - `morning` → 08:00
  - `afternoon` / `noon` → 12:00
  - `evening` → 18:00

  ### Fuzzy Time Labels

  | Label              | Time Range     | Natural Label Example        |
  |-------------------|----------------|------------------------------|
  | early morning      | 04:00–07:59    | "early morning"              |
  | morning            | 08:00–10:59    | "this morning"               |
  | late morning       | 11:00–11:59    | "late morning"               |
  | noon               | 12:00–12:29    | "noon"                       |
  | early afternoon    | 12:30–13:59    | "early afternoon"            |
  | afternoon          | 14:00–16:59    | "this afternoon"             |
  | early evening      | 17:00–18:29    | "early evening"              |
  | evening            | 18:30–20:59    | "this evening"               |
  | late evening       | 21:00–21:59    | "late evening"               |
  | night              | 22:00–23:29    | "tonight"                    |
  | late night         | 23:30–00:59    | "late night"                 |
  | past midnight      | 01:00–03:59    | "early morning (next day)"   |

- `.as_natural()` is **contextual**. It may yield `"in 2 hours"` or `"tonight"` depending on the current `now`.
- If input is ambiguous (e.g., `'6pm'`), default `now` is used unless explicitly passed:
  ```python
  DT("6pm", now=datetime(2025, 5, 13, 9, 0))
  ```

- Invalid inputs raise `ValueError`:
  ```python
  DT("yesterday tomorrow")  # raises
  DT("Feb 30")  # raises
  ```

- Round-tripping is **not guaranteed**: natural forms are lossy or context-derived.

- Shorthand properties: `db`, `s`, and `n` map to `.as_debug()`, `.as_strict()`, and `.as_natural()` respectively.

## Tests

```python
# Roundtrip-safe
assert DT("202505141900").as_debug() == "202505141900"

# Partial debug forms
assert DT("20250513").as_debug() == "202505130000"
assert DT("1730").as_debug() == "202505131730"
assert DT("17").as_debug() == "202505131700"

# Natural expressions (contextual)
assert DT("tonight").as_debug() == "202505132200"
assert DT("this evening").as_debug() == "202505131900"
assert DT("tomorrow morning").as_debug() == "202505140800"

# Strict iso
assert DT("202505131730").as_strict(format='iso') == "2025-05-13T17:30:00+05:30"

# Failures
try: DT("tomorrow yesterday")
except ValueError: pass

# Natural expression tests
assert DT("202505130800").n == "this morning"
# Verbose versions
assert DT("202505130800").nv == "this morning, 8am"
assert DT("202505131059").n == "this morning"
assert DT("202505131059").nv == "this morning, 10:59am"
assert DT("202505131100").n == "late morning"
assert DT("202505131100").nv == "late morning, 11am"
assert DT("202505131159").n == "late morning"
assert DT("202505131159").nv == "late morning, 11:59am"
assert DT("202505131200").n == "noon"
assert DT("202505131200").nv == "noon, 12pm"
assert DT("202505131229").n == "noon"
assert DT("202505131229").nv == "noon, 12:29pm"
assert DT("202505131230").n == "early afternoon"
assert DT("202505131230").nv == "early afternoon, 12:30pm"
assert DT("202505131359").n == "early afternoon"
assert DT("202505131359").nv == "early afternoon, 1:59pm"
assert DT("202505131400").n == "this afternoon"
assert DT("202505131400").nv == "this afternoon, 2pm"
assert DT("202505131659").n == "this afternoon"
assert DT("202505131659").nv == "this afternoon, 4:59pm"
assert DT("202505131700").n == "early evening"
assert DT("202505131700").nv == "early evening, 5pm"
assert DT("202505131829").n == "early evening"
assert DT("202505131829").nv == "early evening, 6:29pm"
assert DT("202505131830").n == "this evening"
assert DT("202505131830").nv == "this evening, 6:30pm"
assert DT("202505132059").n == "this evening"
assert DT("202505132059").nv == "this evening, 8:59pm"
assert DT("202505132100").n == "late evening"
assert DT("202505132100").nv == "late evening, 9pm"
assert DT("202505132159").n == "late evening"
assert DT("202505132159").nv == "late evening, 9:59pm"
assert DT("202505132200").n == "tonight"
assert DT("202505132200").nv == "tonight, 10pm"
assert DT("202505132329").n == "tonight"
assert DT("202505132329").nv == "tonight, 11:29pm"
assert DT("202505132330").n == "late night"
assert DT("202505132330").nv == "late night, 11:30pm"
assert DT("202505140059").n == "late night"
assert DT("202505140059").nv == "late night, 12:59am"
assert DT("202505140100").n == "early morning (next day)"
assert DT("202505140100").nv == "early morning (next day), 1am"
assert DT("202505140359").n == "early morning (next day)"
assert DT("202505140359").nv == "early morning (next day), 3:59am"

# Verbose future
assert DT("202505140800").nv == "tomorrow morning, 8am"
assert DT("202505150800").nv == "day after tomorrow, 8am"
assert DT("202505161000").nv == "this Thursday, 10am"
assert DT("202505171000").nv == "this Friday, 10am"
assert DT("202505231000").nv == "next Thursday, 10am"
assert DT("202506041000").nv == "in 3 weeks, Tuesday 10am"
assert DT("202506111000").nv == "in 4 weeks, Tuesday 10am"
assert DT("202506131000").nv == "next month, 13th at 10am"
assert DT("202507131000").nv == "in 2 months, 13th at 10am"
assert DT("202508131000").nv == "in 3 months, 13th at 10am"
assert DT("202509131000").nv == "in 4 months, 13th at 10am"
assert DT("202605131000").nv == "next year, 13th May at 10am"
assert DT("202705131000").nv == "in 2 years, 13th May at 10am"
assert DT("202805131000").nv == "in 3 years, 13th May at 10am"

# Verbose past
assert DT("202505120800").nv == "yesterday morning, 8am"
assert DT("202505110800").nv == "day before yesterday, 8am"
assert DT("202505091000").nv == "last Thursday, 10am"
assert DT("202505031000").nv == "last Friday, 10am"
assert DT("202504251000").nv == "2 weeks ago, Thursday 10am"
assert DT("202504181000").nv == "3 weeks ago, Thursday 10am"
assert DT("202504131000").nv == "last month, 13th at 10am"
assert DT("202503131000").nv == "2 months ago, 13th at 10am"
assert DT("202502131000").nv == "3 months ago, 13th at 10am"
assert DT("202501131000").nv == "4 months ago, 13th at 10am"
assert DT("202405131000").nv == "last year, 13th May at 10am"
assert DT("202305131000").nv == "2 years ago, 13th May at 10am"
assert DT("202205131000").nv == "3 years ago, 13th May at 10am"
```