# PISA

PISA is an interactive web server that comprehensively annotates protein structures using state-of-the-art algorithms for predicting domain architecture, intrinsically disordered regions, protein-protein interaction sites, nucleic acid binding sites, metal ion binding sites, and post-translational modifications. Furthermore, PISA aligns uploaded structures against major structural databases to identify similar proteins and provides rich visualization and analysis options. Additionally, PISA can also be installed locally using Docker images. PISA is freely available for academic user and is abai at http://bioinfo-sysu.com/PISA/ and https://github.com/nongbaoting/PISA, PISA is a valuable resource for protein structure analysis and annotation.

---

## Prerequisites

* [Docker](https://www.docker.com/) and docker permission
* python3 and pip


---

## Installation

1. Pull from Github
    ```
    git pull https://github.com/nongbaoting/PISA.git
    cd PISA
    git pull https://github.com/nongbaoting/django_prot.git
    git pull https://github.com/nongbaoting/fontEnd.git
    
    ```

2. install Python package
    ```
    pip install -r requirement.txt
    ```

2. change `main.js` according to your server **IP**
    `vim fontEnd/src/main.js`, change the line below
    ```
    const apiUrl = 'http://IP'
    ```

4. Pull Docker images
    ```
    docker pull nongbaoting/pisa:latest
    ```

3. Download the data
    
    1. Download the pretrained **ProtT5-XL-UniRef50** model ([Link](https://github.com/agemagician/ProtTrans?tab=readme-ov-file)) and put in under directory `data/prot_t5_xl_uniref50`  
    2. Download prot_bert and put in it under directory `data/prot_bert` ([prot_bert](https://huggingface.co/Rostlab/prot_bert/tree/main))
    3. Download InterproScan and download PDB data 
    ```
    sh ./download_and_prepare.sh
    ```

5. install npm packages
    ```
    cd fontEnd
    docker run -it  \
        --add-host dockerhost:${IP}  \
        --gpus all \
        -v `pwd`:/apps \
        -p 9008:9006 \
        -p 9116:9112 \
        nongbaoting/pisa:latest /bin/bash -c "cd /apps/fontEnd  && npm install"
    cd ..
    ```

5. Start Web server
    * change the `IP`below according to your server IP
    * `-p 9006:9006 -p 9112:9112 ` mapping the server port to docker container port, make sure the server port is open

    ```
    IP=172.22.148.150
    docker run -it  \
        --add-host dockerhost:${IP}  \
        --gpus all \
        -v `pwd`:/apps \
        -p 9006:9006 \
        -p 9112:9112 \
        nongbaoting/pisa:latest /apps/startapp.sh
    ```

7. Visit the server from http://IP:9112/#/domain_annotation/pdb_annotations, again change the IP according to your server IP
