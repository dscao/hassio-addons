## 使用说明

本应用可以帮助你将国网的电费、用电量数据接入HA，适用于除南方电网覆盖省份外的用户。即除广东、广西、云南、贵州、海南等省份的用户外，均可使用本应用获取电力、电费数据。

本应用每12小时抓取一次数据，并在HA里更新以下四个实体

```
sensor.last_electricity_usage：最近一天用电量
sensor.electricity_charge_balance：电费余额
sensor.yearly_electricity_usage： 今年以来用电量
sensor.yearly_electricity_charge: 今年以来电费
```

__注：如果你有一个户号，在HA里就是以上实体名；如果你有多个户号，实体名称还要加 “\_户号”后缀，举例:sensor.last_electricity_usage_1234567890__


由于采用REST API方式创建sensor，没有做实体注册，无法在webui里编辑。如果需要，你可以在configuration.yaml下增加如下配置后重启HA，这样你就可在webUI编辑对应的实体了。


如果你有一个户号，参照以下配置

```yaml
template:
  - trigger:
      - platform: event
        event_type: "state_changed"
        event_data: 
          entity_id: sensor.electricity_95598
    sensor:
      - name: electricity_charge_balance_entity
        unique_id: electricity_charge_balance_entity
        state: "{{ states('sensor.electricity_95598') }}"
        unit_of_measurement: "CNY"
        device_class: monetary

      - name: electricity_balance_is_pay_entity
        unique_id: electricity_balance_is_pay_entity
        state: "{{ state_attr('sensor.electricity_95598', 'is_pay') }}"
 
      - name: last_electricity_usage_entity
        unique_id: last_electricity_usage_entity
        state: "{{ state_attr('sensor.electricity_95598', 'last_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "kWh"

      - name: yearly_electricity_usage_entity
        unique_id: yearly_electricity_usage_entity
        state: "{{ state_attr('sensor.electricity_95598', 'yearly_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "kWh"

      - name: yearly_electricity_charge_entity
        unique_id: yearly_electricity_charge_entity
        state: "{{ state_attr('sensor.electricity_95598', 'yearly_electricity_charge') }}"
        unit_of_measurement: "CNY"
        device_class: monetary
        
      - name: electricity_need_pay
        unique_id: electricity_need_pay
        state: "{{ state_attr('sensor.electricity_95598', 'need_pay') }}"
        unit_of_measurement: "CNY"
        device_class: monetary
        
      - name: thismonth_electricity_usage_entity
        unique_id: thismonth_electricity_usage_entity
        state: "{{ state_attr('sensor.electricity_95598', 'thismonth_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "kWh"
        
      - name: electricity_last_date_entity
        unique_id: electricity_last_date_entity
        state: "{{ state_attr('sensor.electricity_95598', 'last_date') }}"
```

如果你有多个户号，每个户号参照以下配置

```yaml
template:
  - trigger:
      - platform: event
        event_type: "state_changed"
        event_data: 
          entity_id: sensor.electricity_95598_户号
    sensor:
      - name: electricity_charge_balance_entity_户号
        unique_id: electricity_charge_balance_entity_户号
        state: "{{ states('sensor.electricity_95598_户号') }}"
        unit_of_measurement: "CNY"
        device_class: monetary

      - name: electricity_balance_is_pay_entity_户号
        unique_id: electricity_balance_is_pay_entity_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'is_pay') }}"
 
      - name: last_electricity_usage_entity_户号
        unique_id: last_electricity_usage_entity_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'last_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "kWh"

      - name: yearly_electricity_usage_entity_户号
        unique_id: yearly_electricity_usage_entity_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'yearly_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "kWh"

      - name: yearly_electricity_charge_entity_户号
        unique_id: yearly_electricity_charge_entity_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'yearly_electricity_charge') }}"
        unit_of_measurement: "CNY"
        device_class: monetary
        
      - name: electricity_need_pay_户号
        unique_id: electricity_need_pay_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'need_pay') }}"
        unit_of_measurement: "CNY"
        device_class: monetary
        
      - name: thismonth_electricity_usage_entity_户号
        unique_id: thismonth_electricity_usage_entity_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'thismonth_electricity_usage') }}"
        state_class: measurement
        unit_of_measurement: "kWh"
        
      - name: electricity_last_date_entity_户号
        unique_id: electricity_last_date_entity_户号
        state: "{{ state_attr('sensor.electricity_95598_户号', 'last_date') }}"
```
