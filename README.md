Repository for a Computer Science project course (course code: EDAN70) at Lund Tekniska Högskola (LTH).

## Requirements
In order to reproduce our findings, one first need to:

1. Install required Python packages ([requirements.txt](requirements.txt)):
```
pip install -r requirements.txt
```
2. For brevity, a [`nf.zip`](data/nf.zip) file is provided containing the results of the scraping by [`1_encyclopedia_scraper.py`](1_encyclopedia_scraper.py). Unpack it within the [data](data) directory such that the texts are available as:
- `data/nf_first_edition/...`
- `data/nf_fourth_edition/...`

    Of course, one can perform the scraping if desired, but be warned that this might take a very long time.

3. In addition, we use KB-BERT (locally) which can be downloaded from Hugging Face at https://huggingface.co/KB/bert-base-swedish-cased. Download the files for `bert-base-swedish-cased` (`config.json`, `vocab.txt`, `pytorch_model.bin`) and place them in their own directory named `kb-bert-base-swedish-cased`. 

    Alternatively, KB-BERT can be run via the Hugging Face servers, doing this would require slight modification of [`3_train_classifier.ipynb`](3_train_classifier.ipynb).

4. (Optional, but highly recommended) Creating embeddings for all of the entries is *very* time consuming. If one wants to exactly reproduce our results, then a lot of time can be saved by downloading the embeddings we had for both the training and the encyclopedia classification from [Google Drive](https://drive.google.com/drive/folders/1ZXSYUmf82o3Nu84I2FmWAz6plqRUZw_M?usp=sharing). Unpack and place the files such that they are available as:
- `data/json/classification/encyclopedia_embeds.hf/...`
- `data/json/training/ver1/dataset_1_embeds.hf/...`




## Data Files

### Entry Extraction
The results of [`2_extract_entries.py`](2_extract_entries.py) are available at:
- [`data/json/first_ed/...`](data/json/first_ed/)
- [`data/json/fourth_ed/...`](data/json/fourth_ed/)

but can easily be reproduced by simply executing [`2_extract_entries.py`](2_extract_entries.py), provided that [`nf.zip`](data/nf.zip) has been properly unpacked.

### Training
The training and validation data for [`3_train_classifier.ipynb`](3_train_classifier.ipynb) is available at: [`data/json/training/...`](data/json/training/)

### Classifying the Encyclopedia
The results of the classification ([`4_classify_encyclopedia.ipynb`](4_classify_encyclopedia.ipynb)) is available at: [`data/json/classification/...`](data/json/classification/)
