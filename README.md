- Go to https://www.messenger.com/secure_storage/dyi

- Download your messenger data

- Extract the relevant conversation and add the json-file in this directory, make sure it has the name `data.json` (or change the name in the code)

- (if you want) create a venv (done with `python -m pip venv .venv`, and activated with `./.venv/Scripts/activate`)

- Install the needed dependencies with `pip install -r requirements.txt`

- If you wish, set a start date of the conversation (this is done in `main()` in `messenger_wrapped.py`)

- Run with `python messenger_wrapped.py` to get your own Messenger Wrapped as a PDF
