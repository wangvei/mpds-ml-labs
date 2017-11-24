Data-driven predictions from the crystalline structure
======

![Materials simulations ab datum](https://raw.githubusercontent.com/mpds-io/mpds-ml-labs/master/crystallographer_mpds_cc_by_40.png "Materials simulation ab datum")

Rationale
------

This is the proof of concept, how a relatively unsophisticated statistical model (namely, random forest regressor) trained on the large MPDS dataset predicts a set of physical properties from the only crystalline structure. Similarly to _ab initio_, this method could be called _ab datum_. (Note however that the simulation of physical properties with a comparable precision normally takes days, weeks or even months, whereas the present prediction method takes less than a second.) A crystal structure in either CIF or POSCAR format is required.

Installation
------

```shell
git clone REPO_ADDR
virtualenv --system-site-packages REPO_FOLDER
cd REPO_FOLDER
. bin/activate
pip install -r requirements.txt
```

Preparation
------

The model is trained on the MPDS data using the MPDS API and the script `ml_mpds.py`. Some subset of the full MPDS data is opened and possible to obtain via MPDS API [for free](https://mpds.io/open-data-api).

Architecture and usage
------

This is the client-server application. The client is not required although, and it is possible to employ the server code as a standalone command-line application. The client is used for a convenience only. The client and the server communicate using HTTP. Any client able to execute HTTP requests is supported, be it a `curl` command-line client or rich web-browser user interface. As an example of the latter, a simple HTML5 app `index.html` is supplied. Server part is a Flask app, loading the pre-trained ML models:

```python
python index.py /tmp/path_to_model_one /tmp/path_to_model_two
```

Web-browser user interface is then available under `http://localhost:5000`. To serve the requests the development Flask server is used. Therefore an _AS-IS_ deployment in an online environment without the suitable WSGI container is highly discouraged. Serving of the ML models is very simple. For the production environments under high load it is recommended to follow e.g. [TensorFlow Serving](https://www.tensorflow.org/serving).

API
------

At the local server:

```shell
curl -XPOST http://localhost:5000/predict -d "structure=data_in_CIF_or_POSCAR"
```

At the remote Tilde server (may be switched off):

```shell
curl -XPOST https://tilde.pro/services/predict -d "structure=data_in_CIF_or_POSCAR"
```

License
------

- The client and the server code: *MIT*
- The [open part](https://mpds.io/open-data-api) of the MPDS data (5%): *CC BY 4.0*
- The closed part of the MPDS data (95%): *commercial*
