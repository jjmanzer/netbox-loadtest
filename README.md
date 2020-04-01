# Netbox Load Test Tool
A tool to measure the performance of your NetBox API.

Example command

```
netbox-loadtest 10.0.0.0/8 29 1 $FQDN $TOKEN
starting the 1 worker scenario
  starting worker thread 1 of 1 with 10.0.16.0/20
    testing with 10.0.16.0/20

    finished with 10.0.16.0/20
```

Then open the file `netbox_load_test_report_10.0.0.0_8.xlsx` with an excel tool to examine the data.
