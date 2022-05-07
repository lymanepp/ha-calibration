---
title: Calibration
description: Instructions on how to integrate calibration into Home Assistant.
ha_category:
  - Utility
  - Sensor
ha_iot_class: Calculated
ha_codeowners:
  - '@lymanepp'
ha_domain: calibration
ha_platforms:
  - sensor
---

The Calibration integration consumes the state from other sensors. It exports the calibrated value as state and the following values as attributes: `source_value`, `source`, `source_attribute` and `coefficients`.  A single polynomial, linear by default, is fit to the data points provided.

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

{% configuration %}
source:
  description: The entity to monitor.
  required: true
  type: string
attribute:
  description: Attribute to monitor.
  required: false
  type: string
hide_source:
  description: Hide the source entity in Home Assistant. Cannot be specified with `attribute`.
  required: false
  default: false
  type: boolean
friendly_name:
  description: Set the friendly name for the new sensor.
  required: false
  default: A prettified version of the configuration section name will be used (`Garage Humidity` in the example).
  type: string
device_class:
  description: Set the device class for the new sensor.
  required: false
  default: The device class from the monitored entity will be used (except when `attribute` is specified).
  type: string
unit_of_measurement:
  description: Defines the units of measurement of the sensor, if any.
  required: false
  default: The unit of measurement from the source will be used (except when `attribute` is specified).
  type: string
data_points:
  description: "The collection of data point conversions with the format `[uncalibrated_value, calibrated_value]`.  e.g., `[1.0, 2.1]`. The number of required data points is equal to the polynomial `degree` + 1. For example, a linear calibration (with `degree: 1`) requires at least 2 data points."
  required: true
  type: list
degree:
  description: "The degree of a polynomial. e.g., Linear calibration (y = x + 3) has 1 degree, Quadratic calibration (y = x<sup>2</sup> + x + 3) has 2 degrees, etc."
  required: false
  default: 1
  type: integer
precision:
  description: Defines the precision of the calculated values.
  required: false
  default: 2
  type: integer
{% endconfiguration %}
