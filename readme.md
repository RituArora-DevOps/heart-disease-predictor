python -m venv .venv
.venv\Scripts\activate

## use Conda instead
conda create -n myenv python=3.10
conda activate myenv

uvicorn app:app --reload

