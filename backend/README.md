# Waste Finder YOLO26

This project now uses a simpler rule-based workflow:

1. `YOLO26` detects objects from the standard COCO 80 classes
2. a Python class maps those object names into one of 3 waste groups
3. the web app only supports these queries:
   - `find me organic waste`
   - `find me recyclable waste`
   - `find me inorganic waste`

## Main files

- `app.py`: Flask app and `/api/find`
- `waste_sorter/keyword_classifier.py`: fixed keyword-to-waste-group rules
- `waste_sorter/detector.py`: YOLO detection + rule filtering + crop generation
- `templates/index.html`: main web UI
- `static/app.js`: frontend submit/render logic

## Supported keyword mapping

### Organic waste

- `banana`
- `apple`
- `sandwich`
- `orange`
- `broccoli`
- `carrot`
- `hot dog`
- `pizza`
- `donut`
- `cake`
- `potted plant`

### Recyclable waste

- `bottle`
- `wine glass`
- `cup`
- `fork`
- `knife`
- `spoon`
- `bowl`
- `book`
- `kite`
- `vase`
- `scissors`

### Inorganic waste

- `backpack`
- `umbrella`
- `handbag`
- `tie`
- `suitcase`
- `frisbee`
- `skis`
- `snowboard`
- `sports ball`
- `baseball bat`
- `baseball glove`
- `skateboard`
- `surfboard`
- `tennis racket`
- `chair`
- `couch`
- `bed`
- `dining table`
- `toilet`
- `tv`
- `laptop`
- `mouse`
- `remote`
- `keyboard`
- `cell phone`
- `microwave`
- `oven`
- `toaster`
- `sink`
- `refrigerator`
- `clock`
- `teddy bear`
- `hair drier`
- `toothbrush`

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Notes

- This flow does not require a custom waste detector to work.
- It is best for a demo or MVP where the allowed waste groups are fixed.
- The result depends on whether YOLO COCO can detect a supported object class in the image.
- Training scripts and TACO conversion scripts are still kept in the repo for future upgrades, but they are no longer required for the main scan flow.
