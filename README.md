# KDD Cup 2017 Project

## Project Structure

```sh
-ProjectRootDir
├── README.md
├── dataSets
│   ├── test_local
│   │   ├── trajectories(table 6)_valid.csv
│   │   └── volume(table 6)_valid.csv
│   │   └── weather (table 7)_valid.csv
│   ├── testing_phase1
│   │   ├── trajectories(table 5)_test1.csv
│   │   ├── volume(table 6)_test1.csv
│   │   └── weather (table 7)_test1.csv
│   ├── training
│   │   ├── links (table 3).csv
│   │   ├── routes (table 4).csv
│   │   ├── trajectories(table 5)_training.csv
│   │   ├── volume(table 6)_training.csv
│   │   └── weather (table 7)_training.csv
│   └── training_local
│       ├── links (table 3).csv
│       ├── routes (table 4).csv
│       ├── trajectories(table 5)_local.csv
│       └── volume(table 6)_local.csv
│       └── weather (table 7)_local.csv
├── results
│
├── scripts
│   ├── aggregate_travel_time.py
│   ├── aggregate_travel_time.pyc
│   ├── aggregate_volume.py
│   ├── aggregate_volume.pyc
│   ├── testing_pred_avg.py
│   ├── testing_pred_volume.py
│   ├── utils.py
│   └── utils.pyc
├── submission_sample_travelTime.csv
├── submission_sample_volume.csv
└── weather (table 7)_training_update.csv
```

数据集太大没有包含在内，可以从官网下载然后解压到项目路径下。

dataSets 路径下，新建了 test_local 和 training_local 两个文件夹，用来存放本地测试的数据文件。

> training_local/trajectories(table 5)_training.csv 文件中是 table 5 的 Jun. 19 至 Oct. 10 的所有数据。用来训练模型。
>
> training_local/volume(table 6)_training.csv 文件中是 table 6 的 Jun. 19 至 Oct. 10 的所有数据。用来训练模型。
>
> test_local/trajectories(table 5)_valid.csv 文件中是 Oct. 11 至 Oct. 17 的所有数据。用来检测模型的预测结果。
>
> test_local/volume(table 6)_valid.csv 文件中是 Oct. 11 至 Oct. 17 的所有数据。用来检测模型的预测结果。

输出文件的路径我设置在了 results 文件夹下。

scripts文件夹下的原始的两个文件我已经略微修改过，包括输出路径的调整等。
