# <img src="calculate_anything/images/icon.svg" alt="drawing" width="25"/> Calculate Anything (v6 fixed)

This is not my work. All credit goes to [tchar](https://github.com/tchar).

[ulauncher-albert-calculate-anything](https://github.com/tchar/ulauncher-albert-calculate-anything) is the most starred extension at [ext.ulauncher.io](https://ext.ulauncher.io/) and there's a new [beta version 6 of Ulauncher](https://github.com/Ulauncher/Ulauncher/releases) which breaks it (Albert probably still works but I haven't tried it).

The extension hasn't been updated since 2024, so I just got Claude Opus 4.6 to fix it.

[![License](https://img.shields.io/github/license/no-faff/ulauncher-calculate-anything?color=%23007ec6)](LICENSE)

A [Ulauncher](https://ulauncher.io/) extension to calculate things like currency, time, percentages, units, complex equations, base-n expressions and more.

See [Features](#features) for supported features, [Contents](#contents) for installation instructions and more.

## Demo

![Ulauncher Demo](misc/demo-ulauncher.gif)

## Features

Calculator for Anything
- `Currency Converter`: See [Currency](#currency) for examples
- `Time Converter`: Convert time to other timezones and compute time expressions or find time remaining until any date-time. See [Time](#time) for examples.
- `Units Converter`: Compute and Convert units to other units. See [Units](#units) for examples.
- `Normal Calculator`: Supports functions such as `cos`, `sin`, `tan`. Check [Calculator](#calculator) for examples.
- `Complex Numbers` Calculator: Also supports Normal Calculator's functions. Check [Calculator](#calculator) for examples.
- `Percentage Calculator` Calculate percentages see [Percentages](#percentages) for examples.
    - Supports all expressions that Normal Calculator and Complex Calculator Support
- `Base N Calculator`: Calculate numbers and expressions to other number base. See [Base N Calculator](#base-n-calculator) for examples.
    - Base 16 (`hex`): Calculates expression to decimal, biniary, octal, color (i.e `RGB`, `YSV`, etc), Bytes (representation of `string`)
    - Base 2 (`bin`), Base 8 (`oct`), Base 10 (`dec`)
    - Supports functions: `or`, `xor`, `and`, `mod`, `div`, `+`, `-`, `/`  

**Dependencies**: [simpleeval](https://github.com/danthedeckie/simpleeval), [pint](https://pypi.org/project/Pint/), [parsedatetime](https://pypi.org/project/parsedatetime/) and [pytz](https://pypi.org/project/pytz/)

Optional: [babel](https://github.com/python-babel/babel) for formatting results in your locale.

## Contents

 - [Install](#install)
 - [How to setup](#how-to-setup)
 - [Examples](#examples)
 - [Known Issues](#known-issues)
 - [Extending and more](#extending-and-more)


## Install

Open Ulauncher, go to Extensions > Add extension and paste:
```
https://github.com/no-faff/ulauncher-calculate-anything
```

The dependencies will automatically be installed by Ulauncher into a virtual environment.

## How to Setup

Use the extension preferences in Ulauncher.

### Trigonometry Mode

The calculator supports calculating trig functions in degrees, radians (default), and gradians. Choose your preferred mode in the extension preferences.

**Note**: Only the radian mode supports complex numbers in trig functions.

### Set Currency Provider

You can select from different currency providers. Supported providers are:
- [fixer.io](https://fixer.io/): You need an API Key (see [Set API Key](#set-api-key)). Get a free one at https://fixer.io/signup (go to your `fixer.io` dashboard and get your API key). This will include all providers from Internal
- Internal: If you select this option currencies are going to be fetched from a variety of providers like [coinbase](https://www.coinbase.com/), [mycurrency.net](https://www.mycurrency.net/) and [European Central Bank](https://www.ecb.europa.eu/home/html/index.en.html): No API key is requred.

Preferences:
Select one in the currency provider preference.

### Set API Key

In order for the currency conversion to work for providers that need an API Key, you need to set it in the preferences.
Copy your API key to the `API KEY` box in preferences.


### Cache

For currency conversion you can enable the cache for a minimum of 1 day up to 1 year. This will store the results fetched by your currency provider to prevent redundant requests. This is especially helpful if you have a free plan on a paid currency provider that limits your requests. It will also display the results faster, since no request is made. If all requested currencies have been cached, no request is made.

Edit `Currency Cache` in the extension preferences.

### Default currency

In the preferences you can define a comma separated list of default currencies to show when typing conversion without target unit/currency.
Defaults to `USD,EUR,CAD,GBP,AUD`

Edit in `Default Currencies` preferences.

### Default cities

In the preferences you can define a comma separated list of default cities when using the time command

Edit in `Default Currencies` preferences.

### Units Conversion Mode

In the preferences you can define a units conversion mode. For now there is normal (default) and crazy.

Crazy means that the unit converter/calculator tries to convert all possible units (currency included) available under the name.

See [Currency](#crazy-conversion) and [Units](#crazy-conversion-1) for more

**Crazy mode is experimental and bugs are to be expected**

Edit in `Units Conversion mode` preferences.

### Show Empty Placeholder

Default is `No`. Set to `Yes` to show an empty placeholder when extension doesn't return anything.

### Commands and Syntax

To calculate/convert anything you can use the keywords
- `=`: For currency, units and calculator
- `time`: For time calculations
- `dec`/`hex`/`bin`/`oct`: For base-n and calculations

You can go directly to [examples](#examples) or use the ones from the demo

To convert currency type your keyword and then

- `AMOUNT CURRENCY` to get conversion in the default currencies set in the preferences (requires cache)
- `AMOUNT CURRENCY in(or to) CURRENCY1,CURRENCY2,CURRENCY3`
- `CURRENCY in(or to) CURRENCY1,CURRENCY2,CURRENCY3`

To convert units use

- `AMOUNT UNIT in(or to) UNIT1,UNIT2,UNIT3`
- `UNIT in(or to) UNIT1,UNIT2,UNIT3`

Comma separated units and currencies can have spaces between them.

For time you can use the time keyword with a syntax

- `time` To get the current time plus the `default cities` you defined in the preferences
- `time at CITY,[COUNTRY|COUNTRY CODE|STATE CODE]` to get the current time for a specified city
- `time + AMOUNT [MONTH|YEAR|WEEK|DAY|HOUR|MINUTE|SECOND] [+ AMOUNT ...] [at CITY, [COUNTRY|COUNTRY CODE|STATE CODE]]` to get the time after the calculation at a specified city.

To calculate an expression just type your expression as in the demo
 - You can use functions such as `tan`,`atan`,`asinh`
 - You can use complex numbers too like `1 + 5i`

To calculate percentages you can use one of the following
- `AMOUNT1% of AMOUNT2` to calculate the AMOUNT1 percent of AMOUNT2
- `AMOUNT1 as % of AMOUNT2` to calculate AMOUNT1 as a percentage of AMOUNT2

If you select one results it will be copied to clipboard.

## Examples

### Currency

#### **Simple Conversion**
- Convert 10 euros to american dollars
    - `10 eur to USD`
    - `10 euros to $`
    - `10 eurs to dollars`

#### **Multiple Conversion**
- Convert 10 euros to american dollars, canadian dollars, bitcoin, and mexican pesos
    - `10 EUR to USD,canadian,bitcoin,mexican`

#### **Crazy Conversion**
`crazy` mode must be enabled in preferences
- Convert 1 us dollar per pound to euros per kilogram
    - `1 $ / pound to EUR / kg`
- Convert 10 us dollars  per square foot squared to canadian dollars per meter squared
    - `10 $ / foot ^ 2 to CAD / meter ^ 2`

### Time

You can also add and subtract time
For example if now is `2021-07-05 14:14:42` then you can use the following

Be careful to use date timespans like `2 years 5 months 2 weeks 3 days 1 hour 4 minutes 3 seconds` and not dates like `December 2022`.

**In the following examples the time returned is accompanied by the date time in the `default cities` you specified in the extension preferences**

- `time`: Returns 2021-07-05 14:14:42 as well as the date time in the default cities specified in settings
- `time plus 1 hour`: Returns Today at 15:14:42 
- `time + 1 day`: Returns Tomorrow at 14:14:42
- `time minus 1 day`: Returns Yesterday at 14:14:42
- `time + 2 hours` 2 minutes 5 seconds: Returns Today at 15:16:47
- `time + 1 year`: Returns 2022-07-05 14:14:42
- `time + 1 year 2 days 2 hours - 4 years 4 minutes`: Returns 2018-07-07 16:10:42

#### **Specifying a target city**

You can use all the commands above followed by `at CITY NAME` or `at CITY NAME, COUNTRY NAME|COUNTRY CODE|STATE CODE` to get te result in your local time as well as the specified city
- `time at Prague`
- `time + 2 hours at Madrid`
- `time + 2 hours at Vancouver, CA`: (There are two Vancouvers, so by specifying CA as returns the Canadian Vancouver)
- `time + 2 days 3 seconds at Vancouver, Canada`
- `time + 1 hour + 3 years at Athens, AL`: (Athens AL refers to Athens at Alabama)

#### **Using until**

You can also use the until command (**Experimental**) to calculate duration of time until a specific date

**Note: The midnight keyword shifts one day after, so midnight is considered to belong in the *next* day**

In the following examples you can specify a specific date and time or say for example a number of years months etc.

Keywords such as `a/next/last/previous/ago`, `years/months/weeks/days/hours/minutes/seconds`, `morning/noon/afternoon/evening/night/midnight`, `tomorrow/yesterday` and the combination of those will work like in the normal mode.

- `time until December 31 midnight`: Returns remaining days, hours minutes until January 00:00:00 (end of day for December)
- `time until midnight`: Returns remaining hours minutes seconds until midnight for this day (midnight is at 00:00:00)
- `time until tomorrow`: Day starts at 09:00
- `time until tomorrow evening`: Hours/Days until tomorrow at 18:00 
- `time until a year ago`: Negative result
- `time until 2000000 year`: Easter egg

And many more combinations

### Units

The units supported are all units that [pint](https://github.com/hgrecco/pint) supports (which is quite a lot)

#### **Simple Conversion**
- Convert 100 fahrenheit to celsius
   - `100 f to c`

#### **Multiple Conversion**
  - Convert 20 centimeters to inches and meters
    - `20 cm to inches, m`
    - `20 cm to inches,meters`

#### **Advanced Conversion**
- Convert kilometers per meter to centimeters per minute, kilometers per minute, inches per second and centimeters per second.
    - `20 km/h to cm/min, km/minute, in/s, cm/sec`
- Convert kilowhats per second to horsepower per hour and megawatts per second
    - `10 kw/sec to hp/h, mw/s`
- Convert meters per squared second to kilometers per squared hour
    - `10 m/s^2 to km/h^2`
- Convert megabytes per second to gigabytes per hour
    - `10 mb/s to gb/h`

**You can lieterally convert anything if the apropriate units match**
- Convert kilometer * centimeter * second per gibabyte to inches * meter * hour per megabyte
    - `10 km * cm * s / gb to inches * meter * hour / mb`

#### **Crazy Conversion**
`crazy` mode must be enabled in preferences
- `1 m to cm` may have two compatible units `meter` and `mole`, so it will return both results

### Percentages

#### **Simple Cases**
- Calculate what is 10% of 40
    - `10% of 40`: Answer is 4
- To calculate what percentage of 30 is 5, any of the following works
    - `5 is what % of 30`: Answer is 16.6667%
    - `5 is what % 30`
    - `5 as % of 30`
    - `5 in % of 30`
    - `5 in % 30`

#### **Advanced Cases**
- `10% of cos(pi) + 5`: Answer is 0.4
- `3 + 2 * pi % of cos(pi) + 5`: Answer is 0.371328
- `5 as % sqrt(2) + 5`: Answer is 77.9519%
- `1 + sin(pi) as % sqrt(2) + 5`: Answer is 15.5904%

### Calculator

The calculator works like a normal calculator, but is able to work with complex numbers too.

The following constants exist: `pi`, `e`, `tau` and others from [cmath](https://docs.python.org/3/library/cmath.html)

The following functions exist: `phase`, `polar`, `rect`, `exp`, `log`, `log10`, `sqrt`, `acos`, `asin`, `atan`, `cos`, `sin`, `tan`, `acosh`, `asinh`, `atanh`, `cosh`, `sinh`, `tanh` and others from [cmath](https://docs.python.org/3/library/cmath.html)

The functions `csc`, `sec`, `cot`, `acsc`, `asec`, and `acot` exist and are calculated using their reciprocals. `atan2` exists but supports only real numbers.

`deg` and `rad` convert from radians to degrees and vice versa respectively, except in gradian mode where they convert from gradians to degrees and from gradians to radians respectively.

#### **Simple Cases**
- `10 + sqrt(2)`: Answer is 11.4142
- `10 + cos(pi) + 30 * e ^ 2`: Answer is 230.672

#### **Complex Numbers**
Use i as the imaginary unit
- `10 + sqrt(2) + i`: Answer is 11.4142 + i
- `cos(1 + i)`: Answer is 0.83373 - 0.988898i
- `e ^ (pi * i) + 1`: Answer is 0 (Euler's identity)

#### **Memory**

The `ans()` function returns the last calculated result.

The calculator has 10 memory slots from `m0` to `m9` which can store numbers for later use. Their values are initialized to `0`, and they are persistent as long as the launcher is running. Reset the entire memory to `0` with `mc()`.

Use the variables `m0` to `m9` to access memory slot values. Use the following functions to load and change the values (Replace `0` with a number from `0` to `9` to use the other slots):
- `m0l(number)`: Load `m0` with `number`
- `m0c()`: Clear `m0` (set to `0`)
- `m0a(number)`: Add `number` to `m0`
- `m0s(number)`: Subtract `number` from `m0`
- `m0m(number)`: Multiply `m0` by `number`
- `m0d(number)`: Divide `m0` by `number`
- `m0e(number)`: Raise `m0` to the power of `number`
- `m0r(number)`: Take the `number`th root of `m0`

The functions return the new memory slot value after the operation to facilitate chaining.

**Note**: the functions run every time a valid expression containing them is evaluated. For example, if `m0` is `1` and the launcher input is `m0a(2)`, `m0` will become `3`. If you type a space, `m0` will become `5` as a new valid expression is evaluated.

### Base N Calculator

Use with the keywords `hex`, `dec`, `bin`, `oct` by default.

#### **Simple Cases**
- `dec 1000`: Returns result in `hex`, `bin`, `oct`
- `hex ffa12`: Returns result in `dec`, `bin`, `oct` as well as `bytes` representation of the input query (including spaces)
- `bin 10101`: Returns result in `dec`, `hex`, `oct`

#### **Special cases with `hex`**
The hex calculator will always produce the `byte` representation of its input query.

#### **Color Conversion with `hex`**
If the input is in the format of #xxxxxx where xxxxxx is a valid hex number, it will convert the number representing a color to other color formats.
- `hex #fa1234`: Returns colors result in `rgb`, `hsv`, `hsl`, `cmyk`.

#### **Advanced Cases**
- `dec/hex/bin/oct 10101 and 10110 xor 10 + 1010 - 1010 div 10 and 10101`: Returns the result in all available base-n (`dec`, `hex`, `oct`, `bin`)
    - Digits must be valid in the base you are using (e.g 2012 is invalid for `bin`)

## Known Issues
If currency stops showing, try removing the cache file and restarting Ulauncher:

```bash
rm ~/.cache/com.github.tchar.calculate-anything/currency_data.json
```


## Extending and More

The `calculate_anything` module does not depend on Ulauncher, only `main.py` does. See the [documentation](docs/API.md) for API examples.

### Adding flags

If your currencie's flag is missing you can place it in the extension's flags directory at `calculate_anything/images/flags/` and restart your launcher or make a pull request to include it.

Make sure to name your flag image in uppercase 2 letter name of your country. To make a currency flag, simply link the country flag you want to the currency `e.g ln -s US.svg USD.svg` or add a completely new flag For example American Dollar's flag is in `calculate_anything/images/flags/USD.svg`. You can use most image formats (i.e `svg`, `png`) 

<div>Flag Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
