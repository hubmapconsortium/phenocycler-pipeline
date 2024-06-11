## Phenocycler 2.0 pipeline

Prepares data and does 2D segmentation of Phenocycler images using deepcell method.


### Usage example

`cwltool pipeline.cwl subm.yaml`

or to run it using SLURM on the HIVE using singularity:

`sbatch -p GPU --gpus 1 --mem=500G cwltool --singularity pipeline.cwl subm.yaml`

`data_dir` to be set in the subm.yaml to point to the directory containing the dataset

Requires a `*metadata.tsv` file containing the 

Requires a `*.channels.csv` indicating which channel should be used for Nuclear and Cell segmentation according to the specification:

| Field Name                              | Field Type | Recommend for Search (available on the portal) Backfill? | Definition                                                                                                                                                                                                                                                               | Options:<br>required, optional | NOTES                                                                                                                      |
| --------------------------------------- | ---------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| channel id                              | text       |                                                          | Structure of the identifier depends on the acquisition system. Whenever possible this should exactly match the channel ID in the QPTIFF file. For example the channel ID in an QPTIFF might be something like "Channel:0:13" which would then be the value entered here. | required                       |                                                                                                                            |
| is channel used for nuclei segmentation | boolean    |                                                          | Specifies if this channel can be used by algorithms performing nuclei segmentation ("Yes" or "No").                                                                                                                                                                      | required                       | In data types for which a HIVE pipeline performs cell and nuclear segmentation, exactly one channel must have value "Yes". |
| is channel used for cell segmentation   | boolean    |                                                          | Specifies if this channel can be used by algorithms performing cell segmentation ("Yes" or "No").                                                                                                                                                                        | required                       | In data types for which a HIVE pipeline performs cell and nuclear segmentation, exactly one channel must have value "Yes". |
| is antibody                             | boolean    |                                                          | Does this channel encode image intensities associated with an antibody ("Yes" or "No")? If "Yes" then the relevant antibody is expected to be listed in the antibodies.tsv file with the same channel ID.                                                                | required                       |

Channel:0:0,Yes,No,No
Channel:0:1,No,No,Yes
Channel:0:2,No,No,Yes
Channel:0:3,No,No,Yes
Channel:0:4,No,Yes,Yes
Channel:0:5,No,No,Yes
Channel:0:6,No,No,Yes
Channel:0:7,No,No,Yes
Channel:0:8,No,No,Yes
Channel:0:9,No,No,Yes
Channel:0:10,No,No,Yes
Channel:0:11,No,No,Yes
Channel:0:12,No,No,Yes
Channel:0:13,No,No,Yes
Channel:0:14,No,No,Yes
Channel:0:15,No,No,Yes
Channel:0:16,No,No,Yes


### The expected input directory structure:
```
data_dir/
├── experiment.qptiff
├── experiment.channels.csv
├── experiment.metadata.tsv
│ 
└── extras
      ├── antibodies.tsv
      └── contributors.tsv
```

### The output structure:
```
pipeline_output/
├── expr
│   └──  experiment_expr.ome.tiff
└── mask
    └──  converted_mask.ome.tiff
```