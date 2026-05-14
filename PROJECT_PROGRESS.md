# Waste Sorting Project Progress

**Cap nhat:** 2026-05-12 (lan 5)

## 1. Tong quan

Project `Waste_Sorting` duoc to chuc theo mo hinh monorepo gom:

- `backend/`: he thong xu ly anh, nhan dien rac va cung cap REST API (FastAPI).
- `frontend/`: giao dien web de tai anh, nhap DSL query, va hien thi ket qua nhan dien.

Backend da duoc chuan hoa hoan toan ve mot huong chinh la **FastAPI**. Flask cu da bi loai bo.

---

## 2. Lich su phat trien

| Ngay | Moc |
|---|---|
| 2026-04-08 | Tich hop frontend React vao monorepo |
| 2026-04-14 | Sua loi TypeScript, xac nhan frontend build duoc |
| 2026-04-17 | Them backend YOLOv26 |
| 2026-05-07 | Them FP pipeline, GoF Interpreter Pattern, formal parse tree tu ANTLR CST, token stream API |
| 2026-05-10 | Resolve merge conflict, khoi phuc FastAPI+DSL sau broken merge, don dep Flask orphan code |
| 2026-05-10 | Them SAHI (Sliced Aided Hyper Inference) vao YoloV26Detector — chia tile + class-aware NMS, expose qua API |
| 2026-05-10 | Wire SAHI xuyen suot pipeline /waste/find: HybridWasteDetector → route → api.ts → useClassify → ClassificationForm checkbox |
| 2026-05-11 | Frontend: hien thi tokens (TokenStream), formal_parse_tree (TreeVisualizer), engine info (EngineInfo); count semantic; layout moi (ImageCanvas full-row, 4 row panels) |
| 2026-05-11 | Task #7 — Danh gia va cai thien model custom: them evaluate_waste_detector.py (metrics per-class + recommendations), oversample minority class trong build script, augmentation hyperparams trong train script, per-group skip-primary config (organic always fallback) |
| 2026-05-11 | Han che "Model primary con yeu" — them 3 co che moi: (1) per-group confidence override (WASTE_HYBRID_GROUP_MIN_CONFIDENCE), (2) merge strategy (WASTE_HYBRID_STRATEGY=merge): chay ca hai engine, spatial NMS blend, (3) TTA (WASTE_DETECTOR_USE_TTA=true): augment=True cho primary. Training: --label-smoothing + --cls-pw cho class imbalance. Tests: 24→27 passed. |
| 2026-05-11 | Task #6 — Xu ly build frontend: xac nhan production build thanh cong (Vite 8 + rolldown + Tailwind CSS v4 native OK); chuyen sang PrismLight + dang ky rieng ngon ngu pascal (vendor-syntax-hl giam tu 607 kB xuong 19 kB, -97%); lazy-load Login va Dashboard qua React.lazy; tach vendor chunks (d3/syntax-hl/react) — build sach khong warning |

---

## 3. Cau truc du an

```
Waste_Sorting/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py              # Dependency injection
│   │   │   ├── router.py            # Aggregates all routers
│   │   │   └── routes/
│   │   │       ├── health.py        # GET /api/v1/healthz
│   │   │       ├── yolov26.py       # GET/POST /api/v1/yolov26/*
│   │   │       └── waste.py         # GET/POST /api/v1/waste/*
│   │   ├── core/
│   │   │   ├── config.py            # pydantic-settings cấu hình
│   │   │   └── errors.py            # Exception types
│   │   ├── schemas/
│   │   │   ├── yolov26.py           # Detection response schemas
│   │   │   └── waste.py             # Waste API schemas
│   │   └── services/
│   │       ├── image_validation.py  # Validate ảnh upload
│   │       ├── yolov26_detector.py  # COCO model detector (YOLOv26)
│   │       ├── waste_model_detector.py  # Custom waste model detector
│   │       ├── waste_rules.py       # WasteRuleMatcher + ParsedWasteQuery
│   │       └── hybrid_waste_detector.py  # Hybrid engine orchestrator
│   ├── antlr/
│   │   ├── grammar/
│   │   │   └── WasteQuery.g4        # ANTLR grammar definition
│   │   ├── generated/               # Lexer, Parser, Visitor (auto-gen)
│   │   └── generate_parser.ps1      # Script sinh lại parser
│   ├── dsl/
│   │   ├── ast.py                   # TokenInfo, ParseTreeNode, WasteQueryAst
│   │   ├── parser.py                # WasteQueryDslParser (ANTLR-backed)
│   │   ├── functional.py            # FP utilities (compose, pipeline, HOF)
│   │   └── interpreter.py           # GoF Interpreter Pattern
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_config.py
│   │   ├── test_hybrid_waste_detector.py
│   │   ├── test_image_validation.py
│   │   ├── test_waste_query_dsl.py
│   │   ├── test_waste_rules.py
│   │   └── test_yolov26_detector.py
│   ├── training/                    # Scripts và artifacts training model
│   │   ├── training_support.py      # Shared utilities (inventory, labels, classes)
│   │   ├── build_material_dataset.py
│   │   ├── build_taco_project_dataset.py  # --oversample flag de can bang class imbalance
│   │   ├── evaluate_waste_detector.py     # Danh gia model: mAP/P/R per-class + JSON report
│   │   ├── generate_material_manifest.py
│   │   ├── train_waste_detector.py        # Augmentation hyperparams (mosaic, mixup, copy-paste, freeze)
│   │   └── train_material_detector.py
│   └── main.py                      # FastAPI entry point (uvicorn)
├── frontend/
│   └── src/
│       ├── api/client.ts
│       ├── types/waste.ts
│       ├── pages/
│       │   ├── Login.tsx
│       │   └── Dashboard.tsx
│       └── features/classification/
│           ├── components/
│           │   ├── ClassificationForm.tsx
│           │   ├── DSLEditor.tsx
│           │   ├── ImageCanvas.tsx
│           │   ├── MatchResult.tsx
│           │   └── TreeVisualizer.tsx
│           ├── hooks/useClassify.ts
│           └── services/api.ts
└── PROJECT_PROGRESS.md
```

---

## 4. Backend — Trang thai hien tai

### 4.1. API Endpoints

| Method | Path | Mo ta |
|---|---|---|
| GET | `/api/v1/healthz` | Health check |
| GET | `/api/v1/yolov26/model` | Thong tin model COCO |
| POST | `/api/v1/yolov26/detect` | Nhan dien bang model COCO (ho tro SAHI slicing) |
| GET | `/api/v1/waste/queries` | Lay danh sach DSL examples va groups |
| GET | `/api/v1/waste/models` | Trang thai primary/fallback engine |
| POST | `/api/v1/waste/find` | Nhan dien rac theo DSL query (hybrid) |

### 4.2. SAHI — Sliced Aided Hyper Inference

`POST /api/v1/yolov26/detect` nhan them cac Form field tuy chon:

| Tham so | Kieu | Mac dinh | Mo ta |
|---|---|---|---|
| `use_slicing` | bool | `false` | Bat/tat SAHI |
| `slice_width` | int | `640` | Chieu rong moi tile (px) |
| `slice_height` | int | `640` | Chieu cao moi tile (px) |
| `overlap_ratio` | float | `0.2` | Ty le chong lap giua cac tile (0–1) |
| `postprocess_iou_threshold` | float | `0.5` | Nguong IoU cho NMS hau ky |

**Luong xu ly khi `use_slicing=true`:**
1. Chia anh thanh cac tile co kich thuoc `slice_width × slice_height` voi overlap.
2. Them full image vao cuoi de detect vat the lon.
3. Chay YOLO inference tren tung tile.
4. Chuyen toa do bounding box ve he toa do toan anh.
5. Ap dung **class-aware NMS** (tung lop rieng biet) de loai duplicate.
6. Tra ve `DetectionResponse` nhu binh thuong.

> **Khi nao nen dung:** Anh do phan giai cao (>1280px), nhieu vat the nho, canh day dac.

**SAHI duoc wire xuyen suot ca hai pipeline:**

| Endpoint | Chain |
|---|---|
| `POST /yolov26/detect` | route → `YoloV26Detector.detect()` |
| `POST /waste/find` | route → `HybridWasteDetector.find()` → `_run_engine()` → `detector.detect()` (ca primary lan fallback) |

**Frontend:** `ClassificationForm` co checkbox "SAHI" (default off). Khi tick, `useSahi=true` duoc thread qua `useClassify.classify()` → `api.findWaste()` → append `use_slicing=true` vao FormData.

### 4.4. Cau hinh (pydantic-settings)

- `Settings` trong `backend/app/core/config.py` dung `pydantic-settings`.
- Cau hinh include: `allowed_image_types`, `waste_hybrid_primary_min_confidence`, `waste_hybrid_primary_min_matches`, `waste_hybrid_weak_groups`.
- Co validate anh upload (kich co, content-type, dinh dang) truoc khi suy luan.

| Bien moi | Kieu | Mac dinh | Mo ta |
|---|---|---|---|
| `WASTE_HYBRID_WEAK_GROUPS` | str | `"organic"` | Danh sach group (phan cach dau phay) luon skip primary va fallback thang sang COCO. Default organic vi chi co 8 training boxes. |

### 4.3 Response schema day du cua `POST /api/v1/waste/find`

```python
class WasteFindResponse(DetectionResponse):
    raw_query: str
    normalized_query: str
    query_action: str          # "find" hoac "count"
    waste_group: str
    targets: list[str]         # keywords hop le cho group
    tokens: list[TokenInfoModel]          # token stream tu lexer
    parse_tree: WasteQueryTreeNode        # semantic AST tree
    formal_parse_tree: WasteQueryTreeNode # academic derivation tree (ANTLR CST)
    confidence_operator: str | None
    minimum_confidence: float | None
    label_filter: str | None
    matches: list[DetectionObject]
    match_count: int
    engine_used: str
    decision_reason: str
    primary_result: WasteEngineResult | None
    fallback_result: WasteEngineResult | None
    primary_error: str | None
    fallback_error: str | None
```

### 4.5. Hybrid Detection Strategy

Luong hoat dong cua `HybridWasteDetector`:

1. Parse DSL query → `ParsedWasteQuery`
2. **Kiem tra weak group**: neu `waste_group` nam trong `weak_group_list` (default: `organic`) → skip primary, nhay thang buoc 3.
3. Chay **primary engine** (`custom_waste_detector` — model `waste_yolo26s_taco`):
   - Neu `match_count >= primary_min_matches` VA `max_confidence >= primary_min_confidence` → dung primary.
4. Neu primary khong dat nguong → chay **fallback engine** (`coco_rule_map` — COCO + rule mapping):
   - Neu fallback thanh cong → dung fallback, bao gom ca `primary_result` trong response.
5. Neu ca hai deu that → raise `InferenceError`.

`decision_reason` trong response mo ta ro engine nao duoc dung va tai sao (ke ca ly do skip primary do weak group).

### 4.6. Waste Group Keywords (COCO rule mapping)

| Group | Vi du keyword |
|---|---|
| `organic` | banana, apple, broccoli, carrot, pizza, cake, ... |
| `recyclable` | bottle, wine glass, cup, fork, knife, bowl, vase, ... |
| `inorganic` | chair, laptop, cell phone, refrigerator, keyboard, ... |

---

## 5. DSL / ANTLR — Trang thai hien tai

### 5.1. Grammar (`backend/antlr/grammar/WasteQuery.g4`)

Grammar hien tai ho tro:
- `query_action`: `find` hoac `count` (optional prefix `me`).
- `waste_group`: `recyclable`, `organic`, `inorganic` (+ ten group truc tiep).
- `where` clause voi:
  - `confidence >= 0.8` (cac operator: `>=`, `>`, `<=`, `<`, `==`)
  - `label = bottle` hoac `label = "wine glass"` (quoted string)
  - `AND` ket hop nhieu predicate

Vi du ho tro:
```
find me recyclable waste
count organic waste where confidence >= 0.6
recyclable waste
find recyclable waste where confidence >= 0.8 and label = bottle
find recyclable waste where label = "wine glass"
```

### 5.2. Parser (`backend/dsl/parser.py`)

`WasteQueryDslParser` cung cap:
- `parse(raw_query)` → `WasteQueryAst`
- `parse_full(raw_query)` → `WasteQueryParseResult`:
  - `ast`: semantic AST (`WasteQueryAst`)
  - `tokens`: tuple cua `TokenInfo` (type + text) trich tu `CommonTokenStream`
  - `formal_parse_tree`: dict mo ta cay phan tich hoc thuat tu ANTLR CST (non-terminal = rule name, terminal = token type + text)

Loi cu phap duoc bat boi `_WasteQueryErrorListener` va nem `InvalidWasteQueryError`.

### 5.3. AST (`backend/dsl/ast.py`)

```python
@dataclass
class WasteQueryAst:
    action: str                           # "find" / "count"
    waste_group: str                      # "recyclable" / "organic" / "inorganic"
    confidence_filter: ConfidencePredicate | None
    label_filter: LabelPredicate | None

    def normalized_query() -> str         # query da chuan hoa
    def to_tree() -> ParseTreeNode        # semantic AST tree
    def to_expression(allowed_keywords)   # xay dung GoF expression tree
```

### 5.4. Functional Programming (`backend/dsl/functional.py`)

Higher-order functions:
- `compose(*fns)` — right-to-left composition
- `pipeline(*fns)` — left-to-right composition
- `make_confidence_filter(operator, threshold)` — curried predicate loc theo confidence
- `make_group_filter(normalize, group, allowed_keywords)` — curried predicate loc theo waste group
- `make_label_filter(normalize, label)` — curried predicate loc theo label
- `apply_filters(detections, filters)` — ap dung danh sach predicate bang `reduce + filter`

### 5.5. GoF Interpreter Pattern (`backend/dsl/interpreter.py`)

```
AbstractExpression (abstract)
├── ActionExpression (Terminal) — tra ve action string
├── WasteGroupExpression (Terminal) — loc detection theo group
├── ConfidenceFilterExpression (Terminal) — tao predicate confidence
├── LabelFilterExpression (Terminal) — tao predicate label
└── WasteQueryExpression (Non-terminal) — ket hop group + filters, tra ve {action, matches, count}
```

`InterpreterContext` chua: `detections`, `normalize`, `allowed_keywords`, `group`.

Luong matching trong `WasteRuleMatcher.match_parsed_query()`:
1. `ast.to_expression(allowed_keywords)` → xay dung cay expression
2. `expression.interpret(context)` → chay qua GoF Interpreter → tra ve `matches`

### 5.6. Lien ket voi Lecture PPL

| Khai niem (Lecture) | Trien khai trong project |
|---|---|
| Lexical Analysis — tokenizer | ANTLR `WasteQueryLexer`; `tokens` field trong response |
| Syntax Analysis — CFG / parse tree | `WasteQuery.g4`; `formal_parse_tree` tu ANTLR CST |
| AST (Semantic Analysis) | `backend/dsl/ast.py` — `WasteQueryAst` + `ParseTreeNode` |
| Interpreter Design Pattern (GoF) | `backend/dsl/interpreter.py` — `AbstractExpression` hierarchy |
| Functional Programming (HOF) | `backend/dsl/functional.py` — compose, pipeline, curried HOF |

---

## 6. Frontend — Trang thai hien tai

### 6.1. Cac component chinh

| Component | Chuc nang |
|---|---|
| `ClassificationForm` | Upload anh + nhap DSL query, gui sang backend |
| `ImageCanvas` | Ve bbox len anh voi label va confidence |
| `MatchResult` | Hien thi danh sach detection objects |
| `DSLEditor` | Hien thi `normalized_query` tu backend (dang code editor) |
| `TreeVisualizer` | Ve parse tree bang `react-d3-tree` |

### 6.2. Flow du lieu

1. User nhap DSL query + upload anh.
2. `ClassificationForm` goi `onScan(file, query)`.
3. `useClassify` hook goi `findWaste(file, query)` → POST `/api/v1/waste/find`.
4. Response duoc map sang `UseClassifyData`:
   - `imageUrl` — object URL de hien thi anh
   - `detectedObjects` — tat ca detections (co bbox % cua anh)
   - `dslCode` — `response.normalized_query`
   - `parseTree` — `response.parse_tree` (semantic AST)
   - `result` — summary string ("find query matched N recyclable item(s)...")
5. `Dashboard` render cac panel voi du lieu nay.

### 6.3. TypeScript types (frontend/src/types/waste.ts)

Frontend da mapping day du cac truong:
- `WasteFindResponse` co: `raw_query`, `normalized_query`, `query_action`, `waste_group`, `targets`, `tokens`, `parse_tree`, `formal_parse_tree`, `confidence_operator`, `minimum_confidence`, `label_filter`, `matches`, `match_count`, `engine_used`, `decision_reason`, `primary_result`, `fallback_result`.

### 6.4. Tinh trang hien tai cua frontend

- `tokens`: hien thi qua component `TokenStream` (token type + text chip).
- `formal_parse_tree`: hien thi qua `TreeVisualizer` (co the switch giua semantic va formal tree).
- `engine_used`, `decision_reason`, `primary_result`, `fallback_result`: hien thi qua `EngineInfo` component.
- `match_count` voi `queryAction === "count"`: `MatchResult` hien thi big count badge.

---

## 7. Kiem thu

Co 7 file test trong `backend/tests/`:

| File | Noi dung kiem thu |
|---|---|
| `test_api.py` | Integration test cac endpoint FastAPI |
| `test_config.py` | Validate pydantic-settings config |
| `test_hybrid_waste_detector.py` | Primary/fallback selection logic |
| `test_image_validation.py` | Validate anh upload |
| `test_waste_query_dsl.py` | DSL parser: parse, AST, confidence/label filter, error |
| `test_waste_rules.py` | WasteRuleMatcher: group filter, confidence, label, count action |
| `test_yolov26_detector.py` | YOLO detector inference |

Tinh trang: repo hien co **27 test functions** trong `backend/tests/`. Frontend production build + lint da duoc xac nhan lai ngay **2026-05-12**. Backend pytest can moi truong Python **3.11/3.12** co day du dependencies de rerun day du.

---

## 8. Han che va viec con lai

### Han che hien tai

| Han che | Mo ta |
|---|---|
| Model primary con yeu | Organic: luon fallback (8 training boxes) — da giam thieu bang merge strategy va weak_groups config. Recyclable/inorganic: co the cai thien them bang retrain voi --label-smoothing va --cls-pw. |
| Grammar DSL con don gian | Chua ho tro nhieu group trong 1 query, khong co ORDER BY / LIMIT |
| Chua co scope/binding, code generation | Cac khai niem PPL nang cao chua duoc tich hop |
| Test FP/Interpreter chua rieng biet | `functional.py`, `interpreter.py` chi duoc test gian tiep qua `test_waste_rules.py` |

### Viec nen lam tiep theo

1. ~~**Frontend: hien thi token stream va formal parse tree**~~ — **Hoan thanh.** `TokenStream` component, `TreeVisualizer` voi `showTerminalText`. TypeScript types va hook da duoc cap nhat.
2. ~~**Semantic layer cho action `count`**~~ — **Hoan thanh.** Frontend: khi `queryAction === "count"`, `MatchResult` hien thi so dem lon (big count badge) + van giu list matched items. `matchedObjects` duoc map tu `response.matches` (filtered) thay vi `response.detections` (all).
3. ~~**Frontend: hien thi decision_reason / engine info**~~ — **Hoan thanh.** `EngineInfo` component hien thi engine_used, decision_reason, primary/fallback match_count va max_confidence.
4. **Mo rong grammar DSL** — Ho tro nhieu nhom trong mot query, them `ORDER BY confidence`, `LIMIT N`, hoac cac filter phong phu hon.
5. **Them test cho FP/Interpreter** — Unit test rieng cho `functional.py`, `interpreter.py` (hien tai chi duoc test gian tiep qua `test_waste_rules.py`).
6. ~~**Xu ly build frontend**~~ — **Hoan thanh.** Vite 8 + rolldown + Tailwind CSS v4 build OK tren Windows. `DSLEditor` chuyen sang `PrismLight` + chi dang ky ngon ngu `pascal`: `vendor-syntax-hl` tu 607 kB xuong **19 kB** (-97%). `Login` va `Dashboard` duoc lazy-load qua `React.lazy`. Vendor chunks tach rieng (d3 / syntax-hl / react). Build sach, khong warning.
7. ~~**Danh gia va cai thien model custom**~~ — **Hoan thanh.** `evaluate_waste_detector.py` moi: do mAP/P/R per-class + khuyen nghi tu dong. `build_taco_project_dataset.py`: flag `--oversample --oversample-factor N` can bang class imbalance. `train_waste_detector.py`: augmentation hyperparams (degrees, mosaic, mixup, copy-paste, freeze). `config.py`: `WASTE_HYBRID_WEAK_GROUPS` (default `organic`). `hybrid_waste_detector.py`: skip primary cho weak groups → organic luon fallback sang COCO (chi co 8 training boxes).
8. ~~**Tich hop SAHI vao waste/find endpoint**~~ — **Hoan thanh.** SAHI da duoc wire xuyen suot `/waste/find` qua `HybridWasteDetector` va frontend checkbox.

---

## 9. Huong dan chay project

### 9.1. Yeu cau tien quyet

- Python 3.11 hoac 3.12
- Node.js >= 18 + npm
- (Tuy chon) GPU CUDA neu muon chay model nhanh hon

### 9.2. Backend

**Buoc 1 — Cai dat dependency**

```bash
cd backend
pip install -r requirements.txt
```

**Buoc 2 — Tao file `.env`**

```bash
# Sao chep file mau, sau do chinh sua neu can
cp .env.example .env
```

Cac bien quan trong trong `.env`:

| Bien | Mo ta | Mac dinh |
|---|---|---|
| `WASTE_YOLOV26_WEIGHTS_PATH` | Duong dan den weights COCO (yolo26n.pt) | `runtime/weights/yolo26n.pt` |
| `WASTE_DETECTOR_WEIGHTS_PATH` | Duong dan den weights custom waste model | `runs/waste_detector/waste_yolo26s_taco/weights/best.pt` |
| `WASTE_CORS_ORIGINS` | Origin cho phep (frontend URL) | `http://localhost:5173` |
| `WASTE_YOLOV26_DEVICE` | Thiet bi chay model (`cpu` hoac `cuda:0`) | `cpu` |

> **Luu y model weights:** File `.pt` khong duoc commit vao git. Dat file weights vao dung duong dan trong `.env` truoc khi chay.

**Buoc 3 — Chay backend**

```bash
# Tu thu muc backend/
python main.py
# hoac dung uvicorn truc tiep
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API se chay tai `http://127.0.0.1:8000`. Docs tai `http://127.0.0.1:8000/docs`.

**Buoc 4 — Chay tests**

```bash
cd backend
pytest tests/ -v
```

### 9.3. Frontend

**Buoc 1 — Cai dat dependency**

```bash
cd frontend
npm install
```

**Buoc 2 — Tao file `.env`**

```bash
cp .env.example .env
# Kiem tra VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Buoc 3 — Chay dev server**

```bash
npm run dev
```

Frontend se chay tai `http://localhost:5173`.

> Neu PowerShell chan `npm.ps1`, hay dung `npm.cmd run dev`, `npm.cmd run build`, va `npm.cmd run lint`.

### 9.4. Chay toan bo (ca backend lan frontend)

Mo 2 terminal song song:

```bash
# Terminal 1 — Backend
cd backend && python main.py

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Truy cap `http://localhost:5173` de su dung app.

---

## 10. Xu ly loi thuong gap (Troubleshooting)

### 10.1. Loi: ultralytics chua duoc cai dat

**Trieu chung:**
```
Failed to load yolo26n weights from '...runtime\weights\yolo26n.pt':
The 'ultralytics' package is not installed in this environment.
```

**Nguyen nhan:** Chua activate virtual environment truoc khi chay uvicorn, hoac `pip install -r requirements.txt` bi bo qua.

**Cach sua:**
```powershell
# Kiem tra da activate venv chua (phai thay "(venv)" dau dong)
.\venv\Scripts\Activate.ps1

# Cai lai toan bo dependencies
pip install -r requirements.txt
```

---

### 10.2. Loi: numpy khong import duoc (Python version khong tuong thich)

**Trieu chung:**
```
OpenCV bindings requires "numpy" package.
ImportError: No module named 'numpy._core._multiarray_umath'

The following compiled module files exist, but seem incompatible
with with either python 'cpython-314' or the platform 'win32':
  * _multiarray_umath.cp311-win_amd64.pyd
```

**Nguyen nhan:** Python 3.14 (hoac cac phien ban qua moi) khong tuong thich voi numpy va cac thu vien nhu opencv, ultralytics. Cac package nay chi co ban compiled san cho Python 3.11 / 3.12.

**Cach kiem tra:**
```powershell
python --version
# Neu hien thi Python 3.13+ -> can doi xuong 3.11 hoac 3.12
```

**Cach sua — tao lai venv voi Python 3.11:**

Buoc 1: Cai Python 3.11 qua winget (neu chua co):
```powershell
winget install Python.Python.3.11
```

> Mo terminal moi sau khi cai xong.

Buoc 2: Kiem tra Python 3.11 da duoc nhan:
```powershell
py -3.11 --version
```

Buoc 3: Xoa venv cu va tao lai:
```powershell
cd backend

# Thoat venv hien tai
deactivate

# Xoa venv cu
Remove-Item -Recurse -Force venv

# Tao venv moi voi Python 3.11
py -3.11 -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Cai lai toan bo dependencies
pip install -r requirements.txt
```

Buoc 4: Chay lai server:
```powershell
uvicorn main:app --reload
```

---

## 11. Ket luan

Den 2026-05-11, project da hoan thanh cac thanh phan nen tang:

**Backend:**
- FastAPI voi cac route day du, validate input, dependency injection ro rang.
- Hybrid detection (primary custom model + fallback COCO rule map) voi per-group weak-group skip logic.
- DSL query dua tren ANTLR 4.13.2 voi grammar, lexer, parser, visitor.
- Semantic AST (`WasteQueryAst`) va academic parse tree (`formal_parse_tree`) tu ANTLR CST.
- Token stream expose trong API response.
- Functional Programming pipeline (compose, pipeline, curried HOF, apply_filters).
- GoF Interpreter Pattern (AbstractExpression hierarchy, interpret(context)).
- 24 tests pass, runtime on.
- SAHI (Sliced Aided Hyper Inference) tich hop day du: chia tile, class-aware NMS, wire xuyen suot ca `/yolov26/detect` lan `/waste/find` (primary + fallback); frontend co checkbox bat/tat.
- Model evaluation script (`evaluate_waste_detector.py`): do mAP/P/R per-class, bao cao imbalance, khuyen nghi tu dong.
- Training pipeline cai thien: oversampling minority class, augmentation hyperparams (mosaic, mixup, copy-paste, freeze).

**Frontend:**
- React + TypeScript + react-d3-tree.
- Upload anh va nhap DSL query.
- Hien thi detection bbox (ve tren canvas), detection list, DSL code.
- Hien thi token stream (`TokenStream`), ca hai loai parse tree — semantic va formal (`TreeVisualizer`).
- Hien thi engine info: `engine_used`, `decision_reason`, primary/fallback match count va confidence (`EngineInfo`).
- Count action hien thi big count badge trong `MatchResult`.
