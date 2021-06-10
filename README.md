## CellDIVE pipeline

Prepares data and does 2D segmentation of CellDIVE images slice by slice using deepcell method.


### Usage example

`cwltool pipeline.cwl subm.yaml`

Requires `meta.yaml` with names of channels 
that will be used for segmentation of cell and nucleus compartments.


### The expected input directory structure:
```
HuBMAP_OME/
├── region_001
│     ├── S20030077_region_001.ome.tif
│     ├── S20030078_region_001.ome.tif
│     │              ...
│     └── S20030105_region_001.ome.tif
└── region_00N
      ├── S20030077_region_00N.ome.tif
      ├── S20030078_region_00N.ome.tif
      │             ...
      └── S20030105_region_00N.ome.tif
```

### The output structure:
```
pipeline_output/
├── expr
│   ├── region_001
│   │    ├── reg001_S20030077_region_001_expr.ome.tiff
│   │    ├── reg001_S20030078_region_001_expr.ome.tiff
│   │    │                  ...
│   │    └── reg001_S20030105_region_001_expr.ome.tiff
│   └── region_00N
│        ├── reg00N_S20030077_region_00N_expr.ome.tiff
│        ├── reg00N_S20030078_region_00N_expr.ome.tiff
│        │                  ...
│        └── reg00N_S20030105_region_00N_expr.ome.tiff       
└── mask                                              
    ├── region_001                                    
    │    ├── reg001_S20030077_region_001_mask.ome.tiff
    │    ├── reg001_S20030078_region_001_mask.ome.tiff
    │    │                  ...                   
    │    └── reg001_S20030105_region_001_mask.ome.tiff
    └── region_00N                                
         ├── reg00N_S20030077_region_00N_mask.ome.tiff
         ├── reg00N_S20030078_region_00N_mask.ome.tiff
         │                  ...                   
         └── reg00N_S20030105_region_00N_mask.ome.tiff    
```