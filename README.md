# [Calibration](https://github.com/lymanepp/ha-calibration)

The Calibration integration consumes the state from other sensors. It exports the calibrated value as state and the following values as attributes: `source_value`, `source`, `source_attribute` and `coefficients`.  A single polynomial, linear by default, is fit to the data points provided.

This is a fork of the Home Assistant Core [compensation](https://www.home-assistant.io/integrations/compensation/) integration created by [@petro31](https://github.com/petro31). It was forked to add these enhancements:
1. Provide sane defaults for `unique_id` and `name`.
2. Allow `device_class` and `unit_of_measurement` to be configured. This is especially useful when `attribute` is specified.
3. Add auto-configuration of `device_class` when `attribute` is not specified. The `compensation` integration already partially supported that for `unit_of_measurement`.
4. Allow hiding the `source` entity from Home Assistant.

#2-4 have been submitted for integration in Home Assistant Core, but backward-compatibility constraints will prevent sane defaults from being integrated upstream.

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be installed using HACS. To do it search for Calibration in the integrations section.

### Manual

To install this integration manually you can either:

* Use git:

```sh
git clone https://github.com/lymanepp/ha-calibration.git
cd ha-calibration
# if you want a specific version checkout its tag
# e.g. git checkout 1.0.0

# replace $hacs_config_folder with your home assistant config folder path
cp -r custom_components $hacs_config_folder
```

* Download the source release and extract the custom_components folder into your home assistant config folder.

Finally, you need to restart Home Assistant before you can use it.

## Configuration

To enable the calibration integration, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
calibration:
  garage_humidity:
    source: sensor.garage_humidity_uncalibrated
    degree: 1
    hide_source: true
    data_points:
      - [38.68, 32.0]
      - [79.89, 75.0]
```

## Options

<dl>
  <dt><strong>source</strong> <code>string</code> <code>(required)</code></dt>
  <dd>The entity to monitor.</dd>

  <dt><strong>attribute</strong> <code>string</code> <code>(optional)</code></dt>
  <dd>The source attribute to monitor.</dd>

  <dt><strong>hide_source</strong> <code>boolean</code> <code>(optional, default: false)</code></dt>
  <dd>Hide the source entity in Home Assistant. If specified with <code>attribute</code>, it will hide the <code>source</code> entity as attributes cannot be hidden.</dd>

  <dt><strong>name</strong> <code>string</code> <code>(optional)</code></dt>
  <dd>Set the name for the new sensor. By default, a human-readable version of the configuration section name will be used (<strong>Garage Humidity</strong> in the example).</dd>

  <dt><strong>device_class</strong> <code>string</code> <code>(optional, default: from source)</code></dt>
  <dd>Set the device class for the new sensor. By default, the device class from the monitored entity will be used (except when <code>attribute</code> is specified).</dd>

  <dt><strong>unit_of_measurement</strong> <code>string</code> <code>(optional, default: from source)</code></dt>
  <dd>Defines the units of measurement of the sensor, if any. By default, the unit of measurement from the source will be used (except when <code>attribute</code> is specified).</dd>

  <dt><strong>data_points</strong> <code>list</code> <code>(required)</code></dt>
  <dd>The collection of data point conversions with the format <code>[uncalibrated_value, calibrated_value]</code>.  e.g., <code>[38.68, 32.0]</code>. The number of required data points is equal to the polynomial <code>degree</code> + 1. For example, a linear calibration (with <code>degree: 1</code>) requires at least 2 data points.</dd>

  <dt><strong>degree</strong> <code>integer</code> <code>(optional, default: 1)</code></dt>
  <dd>The degree of a polynomial. e.g., Linear calibration (y = x + 3) has 1 degree, Quadratic calibration (y = x<sup>2</sup> + x + 3) has 2 degrees, etc.</dd>

  <dt><strong>precision</strong> <code>integer</code> <code>(optional, default: 2)</code></dt>
  <dd>Defines the precision of the calculated values.</dd>
</dl>
